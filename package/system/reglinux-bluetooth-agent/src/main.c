/*
 * reglinux-bluetooth-agent — C daemon replacing the Python system-bluetooth-agent.
 *
 * Drop-in replacement: same binary name, same signal protocol (SIGUSR1/2),
 * same file paths (/var/run/bt_device, /var/run/bt_listing, /var/run/bt_status).
 *
 * Uses sd-bus (basu) instead of dbus-python + GLib main loop.
 */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <getopt.h>
#include <poll.h>
#include <signal.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/signalfd.h>
#include <time.h>
#include <unistd.h>

#include <basu/sd-bus.h>

/* ------------------------------------------------------------------ */
/* Logging                                                            */
/* ------------------------------------------------------------------ */
static FILE *logfp;

static void log_open(void)
{
    logfp = fopen("/var/log/bluetooth-agent.log", "a");
    if (!logfp)
        logfp = stderr;
    setvbuf(logfp, NULL, _IOLBF, 0);
}

static void log_msg(const char *fmt, ...)
{
    time_t now = time(NULL);
    struct tm tm;
    localtime_r(&now, &tm);
    char ts[32];
    strftime(ts, sizeof(ts), "%Y-%m-%d %H:%M:%S", &tm);
    fprintf(logfp, "%s ", ts);
    va_list ap;
    va_start(ap, fmt);
    vfprintf(logfp, fmt, ap);
    va_end(ap);
    fputc('\n', logfp);
}

/* ------------------------------------------------------------------ */
/* Status file (shown in UI)                                          */
/* ------------------------------------------------------------------ */
static void logging_status(const char *msg)
{
    FILE *f = fopen("/var/run/bt_status", "w");
    if (f) {
        fprintf(f, "%s\n", msg);
        fclose(f);
    }
}

/* ------------------------------------------------------------------ */
/* Device list                                                        */
/* ------------------------------------------------------------------ */
typedef struct bt_device {
    struct bt_device *next;
    char *path;
    char *address;
    char *name;
    char *icon;
    bool trusted;
    bool paired;
    bool connected;
    bool listed;       /* already written to bt_listing */
} bt_device_t;

static bt_device_t *devices;

static bt_device_t *dev_find(const char *path)
{
    for (bt_device_t *d = devices; d; d = d->next)
        if (strcmp(d->path, path) == 0)
            return d;
    return NULL;
}

static bt_device_t *dev_get_or_create(const char *path)
{
    bt_device_t *d = dev_find(path);
    if (d) return d;
    d = calloc(1, sizeof(*d));
    d->path = strdup(path);
    d->next = devices;
    devices = d;
    return d;
}

static void dev_remove(const char *path)
{
    bt_device_t **pp = &devices;
    while (*pp) {
        if (strcmp((*pp)->path, path) == 0) {
            bt_device_t *tmp = *pp;
            *pp = tmp->next;
            free(tmp->path);
            free(tmp->address);
            free(tmp->name);
            free(tmp->icon);
            free(tmp);
            return;
        }
        pp = &(*pp)->next;
    }
}

/* helper: update a string field */
static void str_update(char **dst, const char *src)
{
    if (!src) return;
    free(*dst);
    *dst = strdup(src);
}

/* ------------------------------------------------------------------ */
/* Name helpers (match Python getDevName / getShortDevName)           */
/* ------------------------------------------------------------------ */
static const char *dev_name_full(const bt_device_t *d)
{
    static char buf[256];
    if (d->name && d->address && d->icon)
        snprintf(buf, sizeof(buf), "%s (%s, %s)", d->name, d->address, d->icon);
    else if (d->name && d->address)
        snprintf(buf, sizeof(buf), "%s (%s)", d->name, d->address);
    else if (d->name && d->icon)
        snprintf(buf, sizeof(buf), "%s (%s)", d->name, d->icon);
    else if (d->name)
        snprintf(buf, sizeof(buf), "%s", d->name);
    else if (d->address && d->icon)
        snprintf(buf, sizeof(buf), "%s (%s)", d->address, d->icon);
    else if (d->address)
        snprintf(buf, sizeof(buf), "%s", d->address);
    else if (d->icon)
        snprintf(buf, sizeof(buf), "%s", d->icon);
    else
        snprintf(buf, sizeof(buf), "unknown");
    return buf;
}

static const char *dev_name_short(const bt_device_t *d)
{
    if (d->name) return d->name;
    if (d->address) return d->address;
    if (d->icon) return d->icon;
    return "unknown";
}

/* ------------------------------------------------------------------ */
/* Icon to basic name (for listing XML)                               */
/* ------------------------------------------------------------------ */
static const char *icon2basicname(const char *icon)
{
    if (!icon) return "unknown";
    if (strcmp(icon, "input-gaming") == 0) return "joystick";
    if (strncmp(icon, "audio-", 6) == 0) return "audio";
    return icon;
}

/* ------------------------------------------------------------------ */
/* Globals                                                            */
/* ------------------------------------------------------------------ */
static sd_bus *bus;
static char *adapter_path;
static bool discovering;
static bool listing_mode;
static char *opt_dev_id;        /* -i / --device */

/* ------------------------------------------------------------------ */
/* D-Bus helpers                                                      */
/* ------------------------------------------------------------------ */

/* Call a void method on an interface (fire-and-forget) */
static int call_void_method(const char *path, const char *iface, const char *method)
{
    sd_bus_error err = SD_BUS_ERROR_NULL;
    sd_bus_message *reply = NULL;
    int r = sd_bus_call_method(bus, "org.bluez", path, iface, method,
                               &err, &reply, NULL);
    if (r < 0)
        log_msg("call %s.%s on %s failed: %s", iface, method, path, err.message ? err.message : strerror(-r));
    sd_bus_error_free(&err);
    sd_bus_message_unref(reply);
    return r;
}

/* Set a boolean property */
static int set_bool_property(const char *path, const char *iface, const char *prop, bool val)
{
    sd_bus_error err = SD_BUS_ERROR_NULL;
    int r = sd_bus_set_property(bus, "org.bluez", path, iface, prop,
                                &err, "b", (int)val);
    if (r < 0)
        log_msg("set %s.%s on %s failed: %s", iface, prop, path, err.message ? err.message : strerror(-r));
    sd_bus_error_free(&err);
    return r;
}

/* ------------------------------------------------------------------ */
/* Discovery helpers                                                  */
/* ------------------------------------------------------------------ */
static void start_discovery(void)
{
    if (!adapter_path) return;
    log_msg("Start discovery");
    call_void_method(adapter_path, "org.bluez.Adapter1", "StartDiscovery");
}

static void stop_discovery(void)
{
    if (!adapter_path) return;
    log_msg("Stop discovery");
    call_void_method(adapter_path, "org.bluez.Adapter1", "StopDiscovery");
}

/* ------------------------------------------------------------------ */
/* Read filter from /var/run/bt_device                                */
/* ------------------------------------------------------------------ */
static char *get_bt_filter(void)
{
    FILE *f = fopen("/var/run/bt_device", "r");
    if (!f) return NULL;
    static char buf[128];
    if (!fgets(buf, sizeof(buf), f)) {
        fclose(f);
        return NULL;
    }
    fclose(f);
    /* trim trailing whitespace */
    char *end = buf + strlen(buf) - 1;
    while (end >= buf && (*end == '\n' || *end == '\r' || *end == ' '))
        *end-- = '\0';
    if (buf[0] == '\0') return NULL;
    log_msg("bt_dev: %s", buf);
    return buf;
}

/* ------------------------------------------------------------------ */
/* Listing support                                                    */
/* ------------------------------------------------------------------ */
static void listing_dev_event(bt_device_t *d, bool adding)
{
    if (!d) return;
    /* already listed / already removed */
    if (d->listed && adding) return;
    if (!d->listed && !adding) return;

    d->listed = adding;

    FILE *f = fopen("/var/run/bt_listing", "a");
    if (!f) return;
    fprintf(f, "<device id=\"%s\" name=\"%s\" status=\"%s\" type=\"%s\" />\n",
            d->address ? d->address : "",
            d->name ? d->name : "",
            adding ? "added" : "removed",
            icon2basicname(d->icon));
    fclose(f);
}

/* ------------------------------------------------------------------ */
/* Pairing / Trusting / Connecting                                    */
/* ------------------------------------------------------------------ */
static void do_pair(bt_device_t *d)
{
    log_msg("Pairing... (%s)", dev_name_full(d));
    char statusmsg[256];
    snprintf(statusmsg, sizeof(statusmsg), "Pairing %s...", dev_name_short(d));
    logging_status(statusmsg);

    sd_bus_error err = SD_BUS_ERROR_NULL;
    sd_bus_message *reply = NULL;
    int r = sd_bus_call_method(bus, "org.bluez", d->path,
                               "org.bluez.Device1", "Pair",
                               &err, &reply, NULL);
    if (r < 0) {
        log_msg("Pairing failed (%s)", dev_name_full(d));
        snprintf(statusmsg, sizeof(statusmsg), "Pairing failed (%s)", dev_name_short(d));
        logging_status(statusmsg);
    }
    sd_bus_error_free(&err);
    sd_bus_message_unref(reply);
}

static void do_connect(bt_device_t *d)
{
    bool was_discovering = discovering;

    /* pause discovery during connection */
    if (was_discovering) {
        log_msg("Stop discovery");
        stop_discovery();
    }

    int ntry = 5;
    while (ntry-- > 0) {
        log_msg("Connecting... (%s)", dev_name_full(d));
        char statusmsg[256];
        snprintf(statusmsg, sizeof(statusmsg), "Connecting %s...", dev_name_short(d));
        logging_status(statusmsg);

        sd_bus_error err = SD_BUS_ERROR_NULL;
        sd_bus_message *reply = NULL;
        int r = sd_bus_call_method(bus, "org.bluez", d->path,
                                   "org.bluez.Device1", "Connect",
                                   &err, &reply, NULL);
        sd_bus_error_free(&err);
        sd_bus_message_unref(reply);

        if (r >= 0) {
            log_msg("Connected successfully (%s)", dev_name_full(d));
            snprintf(statusmsg, sizeof(statusmsg), "Connected successfully (%s)", dev_name_short(d));
            logging_status(statusmsg);
            if (was_discovering) {
                log_msg("Start discovery");
                start_discovery();
            }
            return;
        }
        log_msg("Connection attempt failed (%s)", dev_name_full(d));
        sleep(1);
    }

    log_msg("Connection failed. Give up. (%s)", dev_name_full(d));
    char statusmsg[256];
    snprintf(statusmsg, sizeof(statusmsg), "Connection failed. Give up. (%s)", dev_name_short(d));
    logging_status(statusmsg);

    if (was_discovering) {
        log_msg("Start discovery");
        start_discovery();
    }
}

static void connect_device(bt_device_t *d, bool force_connect)
{
    char *filter = get_bt_filter();
    if (!filter) {
        log_msg("skipping %s. No filter.", d->address ? d->address : "?");
        return;
    }

    if (!d->icon) {
        log_msg("Skipping device %s (no type)", dev_name_full(d));
        return;
    }

    log_msg("filter=%s, Icon=%s, Address=%s", filter, d->icon, d->address ? d->address : "?");

    /* filter check */
    bool match = false;
    if (d->address && strcmp(filter, d->address) == 0)
        match = true;
    if (strcmp(filter, "input") == 0 && strncmp(d->icon, "input-", 6) == 0)
        match = true;
    if (!match) {
        log_msg("Skipping device %s (not %s)", dev_name_full(d), filter);
        return;
    }

    log_msg("event for %s(paired=%s, trusted=%s, connected=%s)",
            dev_name_full(d),
            d->paired ? "paired" : "not paired",
            d->trusted ? "trusted" : "untrusted",
            d->connected ? "connected" : "disconnected");

    /* skip fully connected */
    if (d->paired && d->trusted && d->connected) {
        log_msg("Skipping already connected device %s", dev_name_full(d));
        return;
    }

    /* pair if needed */
    if (!d->paired) {
        if (!d->connected && discovering)
            do_pair(d);
    }

    /* trust if needed */
    if (!d->trusted && (discovering || force_connect)) {
        log_msg("Trusting (%s)", dev_name_full(d));
        char statusmsg[256];
        snprintf(statusmsg, sizeof(statusmsg), "Trusting %s...", dev_name_short(d));
        logging_status(statusmsg);
        set_bool_property(d->path, "org.bluez.Device1", "Trusted", true);
    }

    /* connect if needed */
    if (!d->connected || force_connect)
        do_connect(d);
}

/* ------------------------------------------------------------------ */
/* Parse Device1 properties from a message iterator                   */
/* ------------------------------------------------------------------ */
static void parse_device_props(bt_device_t *d, sd_bus_message *m)
{
    /* m is positioned at the start of a{sv} */
    int r = sd_bus_message_enter_container(m, 'a', "{sv}");
    if (r < 0) return;

    while (sd_bus_message_enter_container(m, 'e', "sv") > 0) {
        const char *key;
        sd_bus_message_read_basic(m, 's', &key);

        if (strcmp(key, "Address") == 0) {
            sd_bus_message_enter_container(m, 'v', "s");
            const char *val;
            sd_bus_message_read_basic(m, 's', &val);
            str_update(&d->address, val);
            sd_bus_message_exit_container(m);
        } else if (strcmp(key, "Name") == 0) {
            sd_bus_message_enter_container(m, 'v', "s");
            const char *val;
            sd_bus_message_read_basic(m, 's', &val);
            str_update(&d->name, val);
            sd_bus_message_exit_container(m);
        } else if (strcmp(key, "Icon") == 0) {
            sd_bus_message_enter_container(m, 'v', "s");
            const char *val;
            sd_bus_message_read_basic(m, 's', &val);
            str_update(&d->icon, val);
            sd_bus_message_exit_container(m);
        } else if (strcmp(key, "Trusted") == 0) {
            sd_bus_message_enter_container(m, 'v', "b");
            int val;
            sd_bus_message_read_basic(m, 'b', &val);
            d->trusted = val;
            sd_bus_message_exit_container(m);
        } else if (strcmp(key, "Paired") == 0) {
            sd_bus_message_enter_container(m, 'v', "b");
            int val;
            sd_bus_message_read_basic(m, 'b', &val);
            d->paired = val;
            sd_bus_message_exit_container(m);
        } else if (strcmp(key, "Connected") == 0) {
            sd_bus_message_enter_container(m, 'v', "b");
            int val;
            sd_bus_message_read_basic(m, 'b', &val);
            d->connected = val;
            sd_bus_message_exit_container(m);
        } else {
            sd_bus_message_skip(m, "v");
        }
        sd_bus_message_exit_container(m);  /* dict entry */
    }
    sd_bus_message_exit_container(m);  /* array */
}

/* ------------------------------------------------------------------ */
/* Signal: InterfacesAdded                                            */
/* ------------------------------------------------------------------ */
static int on_interfaces_added(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    const char *path;
    int r;

    r = sd_bus_message_read_basic(m, 'o', &path);
    if (r < 0) return 0;

    /* enter a{sa{sv}} */
    r = sd_bus_message_enter_container(m, 'a', "{sa{sv}}");
    if (r < 0) return 0;

    bool found_device = false;
    while (sd_bus_message_enter_container(m, 'e', "sa{sv}") > 0) {
        const char *iface;
        sd_bus_message_read_basic(m, 's', &iface);

        if (strcmp(iface, "org.bluez.Device1") == 0) {
            bt_device_t *d = dev_get_or_create(path);
            parse_device_props(d, m);
            found_device = true;
            log_msg("Interface added: %s", dev_name_full(d));

            if (listing_mode)
                listing_dev_event(d, true);

            if (d->address)
                connect_device(d, false);
            else
                log_msg("No address. skip.");
        } else {
            sd_bus_message_skip(m, "a{sv}");
        }
        sd_bus_message_exit_container(m);  /* dict entry */
    }
    sd_bus_message_exit_container(m);  /* array */

    return 0;
}

/* ------------------------------------------------------------------ */
/* Signal: InterfacesRemoved                                          */
/* ------------------------------------------------------------------ */
static int on_interfaces_removed(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    const char *path;
    int r;

    r = sd_bus_message_read_basic(m, 'o', &path);
    if (r < 0) return 0;

    bt_device_t *d = dev_find(path);
    if (d)
        listing_dev_event(d, false);

    dev_remove(path);
    return 0;
}

/* ------------------------------------------------------------------ */
/* Signal: PropertiesChanged (arg0 = org.bluez.Device1)               */
/* ------------------------------------------------------------------ */
static int on_properties_changed(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    const char *iface;
    int r;

    r = sd_bus_message_read_basic(m, 's', &iface);
    if (r < 0) return 0;
    if (strcmp(iface, "org.bluez.Device1") != 0)
        return 0;

    const char *path = sd_bus_message_get_path(m);
    bt_device_t *d = dev_get_or_create(path);

    /* read changed properties */
    bool paired_changed = false, paired_val = false;
    bool connected_changed = false, connected_val = false;

    r = sd_bus_message_enter_container(m, 'a', "{sv}");
    if (r < 0) return 0;

    while (sd_bus_message_enter_container(m, 'e', "sv") > 0) {
        const char *key;
        sd_bus_message_read_basic(m, 's', &key);

        if (strcmp(key, "Address") == 0) {
            sd_bus_message_enter_container(m, 'v', "s");
            const char *val;
            sd_bus_message_read_basic(m, 's', &val);
            str_update(&d->address, val);
            sd_bus_message_exit_container(m);
        } else if (strcmp(key, "Name") == 0) {
            sd_bus_message_enter_container(m, 'v', "s");
            const char *val;
            sd_bus_message_read_basic(m, 's', &val);
            str_update(&d->name, val);
            sd_bus_message_exit_container(m);
        } else if (strcmp(key, "Icon") == 0) {
            sd_bus_message_enter_container(m, 'v', "s");
            const char *val;
            sd_bus_message_read_basic(m, 's', &val);
            str_update(&d->icon, val);
            sd_bus_message_exit_container(m);
        } else if (strcmp(key, "Trusted") == 0) {
            sd_bus_message_enter_container(m, 'v', "b");
            int val;
            sd_bus_message_read_basic(m, 'b', &val);
            d->trusted = val;
            sd_bus_message_exit_container(m);
        } else if (strcmp(key, "Paired") == 0) {
            sd_bus_message_enter_container(m, 'v', "b");
            int val;
            sd_bus_message_read_basic(m, 'b', &val);
            d->paired = val;
            paired_changed = true;
            paired_val = val;
            sd_bus_message_exit_container(m);
        } else if (strcmp(key, "Connected") == 0) {
            sd_bus_message_enter_container(m, 'v', "b");
            int val;
            sd_bus_message_read_basic(m, 'b', &val);
            d->connected = val;
            connected_changed = true;
            connected_val = val;
            sd_bus_message_exit_container(m);
        } else {
            sd_bus_message_skip(m, "v");
        }
        sd_bus_message_exit_container(m);  /* dict entry */
    }
    sd_bus_message_exit_container(m);  /* array */

    if (listing_mode)
        listing_dev_event(d, true);

    log_msg("Properties changed: %s", dev_name_full(d));

    /* match Python logic */
    if (paired_changed && paired_val) {
        connect_device(d, true);
        return 0;
    }

    if (connected_changed && connected_val) {
        return 0;
    }
    if (connected_changed && !connected_val) {
        log_msg("Skipping (property Connected changed to False)");
        return 0;
    }

    if (d->address)
        connect_device(d, false);

    return 0;
}

/* ------------------------------------------------------------------ */
/* Agent1 vtable                                                      */
/* ------------------------------------------------------------------ */
static int agent_release(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    log_msg("agent: Release");
    return sd_bus_reply_method_return(m, NULL);
}

static int agent_request_pin_code(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    const char *dev;
    sd_bus_message_read(m, "o", &dev);
    log_msg("RequestPinCode (%s)", dev);
    return sd_bus_reply_method_return(m, "s", "0000");
}

static int agent_request_passkey(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    const char *dev;
    sd_bus_message_read(m, "o", &dev);
    log_msg("RequestPasskey (%s)", dev);
    return sd_bus_reply_method_return(m, "u", (uint32_t)0);
}

static int agent_display_passkey(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    const char *dev;
    uint32_t passkey;
    uint16_t entered;
    sd_bus_message_read(m, "ouq", &dev, &passkey, &entered);
    log_msg("agent: DisplayPasskey (%s, %06u entered %u)", dev, passkey, entered);
    return sd_bus_reply_method_return(m, NULL);
}

static int agent_display_pin_code(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    const char *dev, *pincode;
    sd_bus_message_read(m, "os", &dev, &pincode);
    log_msg("agent: DisplayPinCode (%s, %s)", dev, pincode);
    return sd_bus_reply_method_return(m, NULL);
}

static int agent_request_confirmation(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    log_msg("agent: RequestConfirmation");
    return sd_bus_reply_method_return(m, NULL);
}

static int agent_request_authorization(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    log_msg("agent: RequestAuthorization");
    return sd_bus_reply_method_return(m, NULL);
}

static int agent_authorize_service(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    log_msg("agent: AuthorizeService");
    return sd_bus_reply_method_return(m, NULL);
}

static int agent_cancel(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    (void)userdata; (void)ret_error;
    log_msg("agent: Cancel");
    return sd_bus_reply_method_return(m, NULL);
}

static const sd_bus_vtable agent_vtable[] = {
    SD_BUS_VTABLE_START(0),
    SD_BUS_METHOD("Release",              "",    "",  agent_release,              SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_METHOD("RequestPinCode",       "o",   "s", agent_request_pin_code,    SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_METHOD("RequestPasskey",       "o",   "u", agent_request_passkey,     SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_METHOD("DisplayPasskey",       "ouq", "",  agent_display_passkey,     SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_METHOD("DisplayPinCode",       "os",  "",  agent_display_pin_code,    SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_METHOD("RequestConfirmation",  "ou",  "",  agent_request_confirmation,SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_METHOD("RequestAuthorization", "o",   "",  agent_request_authorization,SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_METHOD("AuthorizeService",     "os",  "",  agent_authorize_service,   SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_METHOD("Cancel",               "",    "",  agent_cancel,              SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_VTABLE_END
};

/* ------------------------------------------------------------------ */
/* GetManagedObjects — enumerate adapter & devices                    */
/* ------------------------------------------------------------------ */
static int enumerate_objects(void)
{
    sd_bus_error err = SD_BUS_ERROR_NULL;
    sd_bus_message *reply = NULL;
    int r;

    r = sd_bus_call_method(bus, "org.bluez", "/",
                           "org.freedesktop.DBus.ObjectManager",
                           "GetManagedObjects",
                           &err, &reply, NULL);
    if (r < 0) {
        log_msg("GetManagedObjects failed: %s", err.message ? err.message : strerror(-r));
        sd_bus_error_free(&err);
        return r;
    }

    /* reply is a{oa{sa{sv}}} */
    r = sd_bus_message_enter_container(reply, 'a', "{oa{sa{sv}}}");
    if (r < 0) goto out;

    while (sd_bus_message_enter_container(reply, 'e', "oa{sa{sv}}") > 0) {
        const char *obj_path;
        sd_bus_message_read_basic(reply, 'o', &obj_path);

        r = sd_bus_message_enter_container(reply, 'a', "{sa{sv}}");
        if (r < 0) { sd_bus_message_exit_container(reply); continue; }

        while (sd_bus_message_enter_container(reply, 'e', "sa{sv}") > 0) {
            const char *iface;
            sd_bus_message_read_basic(reply, 's', &iface);

            if (strcmp(iface, "org.bluez.Adapter1") == 0) {
                /* find our adapter */
                bool match = false;
                const char *addr = NULL;
                const char *name = NULL;
                int powered = 0;

                r = sd_bus_message_enter_container(reply, 'a', "{sv}");
                if (r >= 0) {
                    while (sd_bus_message_enter_container(reply, 'e', "sv") > 0) {
                        const char *key;
                        sd_bus_message_read_basic(reply, 's', &key);
                        if (strcmp(key, "Address") == 0) {
                            sd_bus_message_enter_container(reply, 'v', "s");
                            sd_bus_message_read_basic(reply, 's', &addr);
                            sd_bus_message_exit_container(reply);
                        } else if (strcmp(key, "Name") == 0) {
                            sd_bus_message_enter_container(reply, 'v', "s");
                            sd_bus_message_read_basic(reply, 's', &name);
                            sd_bus_message_exit_container(reply);
                        } else if (strcmp(key, "Powered") == 0) {
                            sd_bus_message_enter_container(reply, 'v', "b");
                            sd_bus_message_read_basic(reply, 'b', &powered);
                            sd_bus_message_exit_container(reply);
                        } else {
                            sd_bus_message_skip(reply, "v");
                        }
                        sd_bus_message_exit_container(reply);
                    }
                    sd_bus_message_exit_container(reply);
                }

                /* select adapter: match by dev_id or take first */
                if (!adapter_path) {
                    if (!opt_dev_id || (addr && strcmp(opt_dev_id, addr) == 0) ||
                        (strstr(obj_path, opt_dev_id ? opt_dev_id : "") != NULL)) {
                        adapter_path = strdup(obj_path);
                        log_msg("adapter found");
                        log_msg("%s(%s), powered=%d", name ? name : "?", addr ? addr : "?", powered);

                        if (!powered) {
                            log_msg("powering on adapter (%s)", addr ? addr : "?");
                            set_bool_property(adapter_path, "org.bluez.Adapter1", "Powered", true);
                        }
                        match = true;
                    }
                }

                (void)match;
            } else if (strcmp(iface, "org.bluez.Device1") == 0) {
                bt_device_t *d = dev_get_or_create(obj_path);
                parse_device_props(d, reply);
            } else {
                sd_bus_message_skip(reply, "a{sv}");
            }
            sd_bus_message_exit_container(reply);  /* dict entry {sa{sv}} */
        }
        sd_bus_message_exit_container(reply);  /* array a{sa{sv}} */
        sd_bus_message_exit_container(reply);  /* dict entry {oa{sa{sv}}} */
    }
    sd_bus_message_exit_container(reply);

out:
    sd_bus_error_free(&err);
    sd_bus_message_unref(reply);
    return adapter_path ? 0 : -ENODEV;
}

/* ------------------------------------------------------------------ */
/* Main                                                               */
/* ------------------------------------------------------------------ */
int main(int argc, char *argv[])
{
    int r;
    sd_bus_slot *vtable_slot = NULL;
    sd_bus_slot *added_slot = NULL;
    sd_bus_slot *removed_slot = NULL;
    sd_bus_slot *changed_slot = NULL;

    /* parse options (compatible with Python version) */
    static struct option long_opts[] = {
        { "device", required_argument, NULL, 'i' },
        { NULL, 0, NULL, 0 }
    };
    int c;
    while ((c = getopt_long(argc, argv, "i:", long_opts, NULL)) != -1) {
        if (c == 'i')
            opt_dev_id = optarg;
    }

    log_open();
    log_msg("bluetooth agent starting");

    /* open system bus */
    r = sd_bus_open_system(&bus);
    if (r < 0) {
        log_msg("failed to open system bus: %s", strerror(-r));
        return 1;
    }

    /* register agent vtable */
    r = sd_bus_add_object_vtable(bus, &vtable_slot,
                                  "/reglinux/agent",
                                  "org.bluez.Agent1",
                                  agent_vtable, NULL);
    if (r < 0) {
        log_msg("failed to register agent vtable: %s", strerror(-r));
        return 1;
    }

    /* subscribe to D-Bus signals */
    r = sd_bus_match_signal(bus, &added_slot,
                            "org.bluez", "/",
                            "org.freedesktop.DBus.ObjectManager",
                            "InterfacesAdded",
                            on_interfaces_added, NULL);
    if (r < 0) log_msg("failed to subscribe InterfacesAdded: %s", strerror(-r));

    r = sd_bus_match_signal(bus, &removed_slot,
                            "org.bluez", "/",
                            "org.freedesktop.DBus.ObjectManager",
                            "InterfacesRemoved",
                            on_interfaces_removed, NULL);
    if (r < 0) log_msg("failed to subscribe InterfacesRemoved: %s", strerror(-r));

    r = sd_bus_match_signal(bus, &changed_slot,
                            "org.bluez", NULL,
                            "org.freedesktop.DBus.Properties",
                            "PropertiesChanged",
                            on_properties_changed, NULL);
    if (r < 0) log_msg("failed to subscribe PropertiesChanged: %s", strerror(-r));

    /* register as agent with BlueZ */
    {
        sd_bus_error err = SD_BUS_ERROR_NULL;
        sd_bus_message *reply = NULL;
        r = sd_bus_call_method(bus, "org.bluez", "/org/bluez",
                               "org.bluez.AgentManager1", "RegisterAgent",
                               &err, &reply, "os", "/reglinux/agent", "NoInputNoOutput");
        if (r < 0) {
            log_msg("RegisterAgent failed: %s", err.message ? err.message : strerror(-r));
            sd_bus_error_free(&err);
            /* not fatal — bluez may not be ready yet */
        } else {
            sd_bus_error_free(&err);
            sd_bus_message_unref(reply);
        }
    }
    {
        sd_bus_error err = SD_BUS_ERROR_NULL;
        sd_bus_message *reply = NULL;
        r = sd_bus_call_method(bus, "org.bluez", "/org/bluez",
                               "org.bluez.AgentManager1", "RequestDefaultAgent",
                               &err, &reply, "o", "/reglinux/agent");
        if (r < 0)
            log_msg("RequestDefaultAgent failed: %s", err.message ? err.message : strerror(-r));
        sd_bus_error_free(&err);
        sd_bus_message_unref(reply);
    }
    log_msg("agent registered");

    /* give hardware time to settle (matches Python sleep(5)) */
    sleep(5);

    /* enumerate existing objects */
    r = enumerate_objects();
    if (r < 0)
        log_msg("warning: could not find adapter (will retry on signals)");

    /* set up signalfd for SIGUSR1/SIGUSR2/SIGTERM/SIGINT */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGUSR1);
    sigaddset(&mask, SIGUSR2);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGINT);
    sigprocmask(SIG_BLOCK, &mask, NULL);

    int sigfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sigfd < 0) {
        log_msg("signalfd failed: %m");
        return 1;
    }

    log_msg("signals set");

    /* event loop */
    for (;;) {
        struct pollfd fds[2];
        fds[0].fd = sd_bus_get_fd(bus);
        fds[0].events = sd_bus_get_events(bus);
        fds[1].fd = sigfd;
        fds[1].events = POLLIN;

        uint64_t timeout_usec;
        sd_bus_get_timeout(bus, &timeout_usec);
        int timeout_ms = (timeout_usec == UINT64_MAX) ? -1 : (int)(timeout_usec / 1000);
        if (timeout_ms < 0 || timeout_ms > 30000)
            timeout_ms = 30000;

        r = poll(fds, 2, timeout_ms);
        if (r < 0 && errno == EINTR)
            continue;

        /* handle signals */
        if (fds[1].revents & POLLIN) {
            struct signalfd_siginfo si;
            while (read(sigfd, &si, sizeof(si)) == (ssize_t)sizeof(si)) {
                if (si.ssi_signo == SIGUSR1) {
                    if (access("/var/run/bt_listing", F_OK) == 0) {
                        listing_mode = true;
                        log_msg("listing mode enabled");
                        /* reset listed flags and write initial listing */
                        for (bt_device_t *d = devices; d; d = d->next) {
                            d->listed = false;
                            listing_dev_event(d, true);
                        }
                    }
                    if (!discovering) {
                        discovering = true;
                        log_msg("Start discovery (signal)");
                        start_discovery();
                    }
                } else if (si.ssi_signo == SIGUSR2) {
                    if (listing_mode)
                        log_msg("listing mode disabled");
                    listing_mode = false;
                    if (discovering) {
                        discovering = false;
                        log_msg("Stop discovery (signal)");
                        stop_discovery();
                    }
                } else if (si.ssi_signo == SIGTERM || si.ssi_signo == SIGINT) {
                    log_msg("exiting on signal %u", si.ssi_signo);
                    goto cleanup;
                }
            }
        }

        /* process bus events */
        r = sd_bus_process(bus, NULL);
        if (r < 0) {
            log_msg("sd_bus_process failed: %s", strerror(-r));
            break;
        }
    }

cleanup:
    sd_bus_slot_unref(vtable_slot);
    sd_bus_slot_unref(added_slot);
    sd_bus_slot_unref(removed_slot);
    sd_bus_slot_unref(changed_slot);
    close(sigfd);
    sd_bus_flush_close_unref(bus);
    if (logfp && logfp != stderr)
        fclose(logfp);
    return 0;
}
