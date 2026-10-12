/*
 * reglinux-test-wl-probe
 *
 * Enumerate Wayland toplevels via ext_foreign_toplevel_list_v1 (preferred)
 * or zwlr_foreign_toplevel_manager_v1 (fallback). One JSON object per
 * toplevel, then a terminating {"end":true}.
 *
 * Exit codes:
 *   0  success
 *   2  --wait / --wait-activated timed out
 *   3  no foreign-toplevel protocol advertised, OR
 *      --wait-activated requested but selected protocol exposes no state event
 *   1  generic error (connect, args, etc.)
 *
 * License: MIT.
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <getopt.h>
#include <poll.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include <wayland-client.h>

#include "ext-foreign-toplevel-list-v1-client-protocol.h"
#include "wlr-foreign-toplevel-management-unstable-v1-client-protocol.h"

enum proto_mode { PROTO_AUTO, PROTO_EXT, PROTO_WLR };

/* Tri-state for state flags: the ext protocol (as vendored) has no state
 * event, so we surface those as JSON null. wlr does advertise them. */
enum tri { TRI_UNK = -1, TRI_FALSE = 0, TRI_TRUE = 1 };

struct toplevel {
	struct toplevel *next;
	uint32_t serial;
	char *id;     /* ext: identifier; wlr: synthetic "toplevel-N" */
	char *app_id;
	char *title;
	enum tri activated, maximized, minimized, fullscreen;
	bool printed_once;
	bool gone;
};

struct ctx {
	struct wl_display *display;
	struct ext_foreign_toplevel_list_v1 *ext_list;
	struct zwlr_foreign_toplevel_manager_v1 *wlr_mgr;
	uint32_t ext_name, ext_version;
	uint32_t wlr_name, wlr_version;

	struct toplevel *head;
	uint32_t next_serial;

	enum proto_mode mode;
	bool using_wlr;            /* false => ext, true => wlr */

	const char *wait_app_id;       /* --wait        : presence */
	const char *wait_act_app_id;   /* --wait-activated : activation */
	bool match_found;
	bool list_finished;
};

static void die(const char *m) { fprintf(stderr, "wl-probe: %s\n", m); exit(1); }

static char *xstrdup(const char *s) {
	if (!s) return NULL;
	char *r = strdup(s);
	if (!r) die("oom");
	return r;
}

static void json_escape(FILE *out, const char *s) {
	if (!s) { fputs("\"\"", out); return; }
	fputc('"', out);
	for (; *s; ++s) {
		unsigned char c = (unsigned char)*s;
		switch (c) {
		case '"':  fputs("\\\"", out); break;
		case '\\': fputs("\\\\", out); break;
		case '\n': fputs("\\n", out); break;
		case '\r': fputs("\\r", out); break;
		case '\t': fputs("\\t", out); break;
		default:
			if (c < 0x20) fprintf(out, "\\u%04x", c);
			else fputc(c, out);
		}
	}
	fputc('"', out);
}

static const char *tri_json(enum tri t) {
	return t == TRI_UNK ? "null" : (t == TRI_TRUE ? "true" : "false");
}

static struct toplevel *tl_new(struct ctx *c) {
	struct toplevel *t = calloc(1, sizeof(*t));
	if (!t) die("oom");
	t->serial = ++c->next_serial;
	t->activated = t->maximized = t->minimized = t->fullscreen =
		c->using_wlr ? TRI_FALSE : TRI_UNK;
	t->next = c->head;
	c->head = t;
	return t;
}

static bool tl_matches(const struct toplevel *t, const char *app_id) {
	return app_id && t->app_id && strcmp(t->app_id, app_id) == 0;
}

static void tl_emit(struct ctx *c, struct toplevel *t) {
	if (t->gone) return;
	fputs("{\"id\":", stdout);
	if (t->id) json_escape(stdout, t->id);
	else fprintf(stdout, "\"toplevel-%u\"", t->serial);
	fputs(",\"app_id\":", stdout); json_escape(stdout, t->app_id);
	fputs(",\"title\":", stdout);  json_escape(stdout, t->title);
	fprintf(stdout, ",\"activated\":%s",  tri_json(t->activated));
	fprintf(stdout, ",\"maximized\":%s",  tri_json(t->maximized));
	fprintf(stdout, ",\"minimized\":%s",  tri_json(t->minimized));
	fprintf(stdout, ",\"fullscreen\":%s}\n", tri_json(t->fullscreen));
	fflush(stdout);
	t->printed_once = true;
	if (tl_matches(t, c->wait_app_id)) c->match_found = true;
	if (tl_matches(t, c->wait_act_app_id) && t->activated == TRI_TRUE)
		c->match_found = true;
}

/* ---------- ext_foreign_toplevel_handle_v1 ---------- */

static void ext_h_closed(void *data, struct ext_foreign_toplevel_handle_v1 *h) {
	struct toplevel *t = data;
	t->gone = true;
	ext_foreign_toplevel_handle_v1_destroy(h);
}
static void ext_h_done(void *data, struct ext_foreign_toplevel_handle_v1 *h) {
	(void)data; (void)h;
}
static void ext_h_title(void *data, struct ext_foreign_toplevel_handle_v1 *h, const char *s) {
	(void)h; struct toplevel *t = data; free(t->title); t->title = xstrdup(s);
}
static void ext_h_app_id(void *data, struct ext_foreign_toplevel_handle_v1 *h, const char *s) {
	(void)h; struct toplevel *t = data; free(t->app_id); t->app_id = xstrdup(s);
}
static void ext_h_identifier(void *data, struct ext_foreign_toplevel_handle_v1 *h, const char *s) {
	(void)h; struct toplevel *t = data; free(t->id); t->id = xstrdup(s);
}
static const struct ext_foreign_toplevel_handle_v1_listener ext_h_listener = {
	.closed = ext_h_closed, .done = ext_h_done,
	.title = ext_h_title, .app_id = ext_h_app_id, .identifier = ext_h_identifier,
};

/* ---------- ext_foreign_toplevel_list_v1 ---------- */

static void ext_l_toplevel(void *data, struct ext_foreign_toplevel_list_v1 *l,
                           struct ext_foreign_toplevel_handle_v1 *h) {
	(void)l;
	struct ctx *c = data;
	struct toplevel *t = tl_new(c);
	ext_foreign_toplevel_handle_v1_add_listener(h, &ext_h_listener, t);
}
static void ext_l_finished(void *data, struct ext_foreign_toplevel_list_v1 *l) {
	(void)l; struct ctx *c = data; c->list_finished = true;
}
static const struct ext_foreign_toplevel_list_v1_listener ext_l_listener = {
	.toplevel = ext_l_toplevel, .finished = ext_l_finished,
};

/* ---------- zwlr_foreign_toplevel_handle_v1 ---------- */

static void wlr_h_title(void *data, struct zwlr_foreign_toplevel_handle_v1 *h, const char *s) {
	(void)h; struct toplevel *t = data; free(t->title); t->title = xstrdup(s);
}
static void wlr_h_app_id(void *data, struct zwlr_foreign_toplevel_handle_v1 *h, const char *s) {
	(void)h; struct toplevel *t = data; free(t->app_id); t->app_id = xstrdup(s);
}
static void wlr_h_output_enter(void *d, struct zwlr_foreign_toplevel_handle_v1 *h, struct wl_output *o) { (void)d;(void)h;(void)o; }
static void wlr_h_output_leave(void *d, struct zwlr_foreign_toplevel_handle_v1 *h, struct wl_output *o) { (void)d;(void)h;(void)o; }
static void wlr_h_state(void *data, struct zwlr_foreign_toplevel_handle_v1 *h, struct wl_array *state) {
	(void)h;
	struct toplevel *t = data;
	t->activated = t->maximized = t->minimized = t->fullscreen = TRI_FALSE;
	uint32_t *s;
	for (s = state->data; (const char *)s < (const char *)state->data + state->size; ++s) {
		switch (*s) {
		case ZWLR_FOREIGN_TOPLEVEL_HANDLE_V1_STATE_ACTIVATED:  t->activated  = TRI_TRUE; break;
		case ZWLR_FOREIGN_TOPLEVEL_HANDLE_V1_STATE_MAXIMIZED:  t->maximized  = TRI_TRUE; break;
		case ZWLR_FOREIGN_TOPLEVEL_HANDLE_V1_STATE_MINIMIZED:  t->minimized  = TRI_TRUE; break;
		case ZWLR_FOREIGN_TOPLEVEL_HANDLE_V1_STATE_FULLSCREEN: t->fullscreen = TRI_TRUE; break;
		default: break;
		}
	}
}
static void wlr_h_done(void *data, struct zwlr_foreign_toplevel_handle_v1 *h) { (void)data;(void)h; }
static void wlr_h_closed(void *data, struct zwlr_foreign_toplevel_handle_v1 *h) {
	struct toplevel *t = data; t->gone = true;
	zwlr_foreign_toplevel_handle_v1_destroy(h);
}
static void wlr_h_parent(void *d, struct zwlr_foreign_toplevel_handle_v1 *h, struct zwlr_foreign_toplevel_handle_v1 *p) { (void)d;(void)h;(void)p; }
static const struct zwlr_foreign_toplevel_handle_v1_listener wlr_h_listener = {
	.title = wlr_h_title, .app_id = wlr_h_app_id,
	.output_enter = wlr_h_output_enter, .output_leave = wlr_h_output_leave,
	.state = wlr_h_state, .done = wlr_h_done, .closed = wlr_h_closed,
	.parent = wlr_h_parent,
};

/* ---------- zwlr_foreign_toplevel_manager_v1 ---------- */

static void wlr_m_toplevel(void *data, struct zwlr_foreign_toplevel_manager_v1 *m,
                           struct zwlr_foreign_toplevel_handle_v1 *h) {
	(void)m;
	struct ctx *c = data;
	struct toplevel *t = tl_new(c);
	zwlr_foreign_toplevel_handle_v1_add_listener(h, &wlr_h_listener, t);
}
static void wlr_m_finished(void *data, struct zwlr_foreign_toplevel_manager_v1 *m) {
	(void)m; struct ctx *c = data; c->list_finished = true;
}
static const struct zwlr_foreign_toplevel_manager_v1_listener wlr_m_listener = {
	.toplevel = wlr_m_toplevel, .finished = wlr_m_finished,
};

/* ---------- registry ---------- */

static void reg_global(void *data, struct wl_registry *r, uint32_t name,
                       const char *iface, uint32_t version) {
	struct ctx *c = data;
	if (strcmp(iface, ext_foreign_toplevel_list_v1_interface.name) == 0) {
		c->ext_name = name; c->ext_version = version;
	} else if (strcmp(iface, zwlr_foreign_toplevel_manager_v1_interface.name) == 0) {
		c->wlr_name = name; c->wlr_version = version > 3 ? 3 : version;
	}
	(void)r;
}
static void reg_global_remove(void *data, struct wl_registry *r, uint32_t name) {
	(void)data; (void)r; (void)name;
}
static const struct wl_registry_listener reg_listener = {
	.global = reg_global, .global_remove = reg_global_remove,
};

/* ---------- main loop ---------- */

static double now_sec(void) {
	struct timespec ts;
	clock_gettime(CLOCK_MONOTONIC, &ts);
	return ts.tv_sec + ts.tv_nsec / 1e9;
}

static int dispatch_until(struct ctx *c, double deadline) {
	struct wl_display *d = c->display;
	while (wl_display_prepare_read(d) != 0) {
		if (wl_display_dispatch_pending(d) < 0) return -1;
	}
	if (wl_display_flush(d) < 0 && errno != EAGAIN) {
		wl_display_cancel_read(d);
		return -1;
	}
	double left = deadline - now_sec();
	if (left <= 0) { wl_display_cancel_read(d); return 1; /* timeout */ }
	struct pollfd pfd = { .fd = wl_display_get_fd(d), .events = POLLIN };
	int n = poll(&pfd, 1, (int)(left * 1000));
	if (n < 0) { wl_display_cancel_read(d); return errno == EINTR ? 0 : -1; }
	if (n == 0) { wl_display_cancel_read(d); return 1; }
	if (wl_display_read_events(d) < 0) return -1;
	if (wl_display_dispatch_pending(d) < 0) return -1;
	return 0;
}

static void usage(FILE *f) {
	fputs(
		"Usage: reglinux-test-wl-probe [options]\n"
		"  --wait <app_id>            block until a toplevel with this app_id appears\n"
		"  --wait-activated <app_id>  block until that app_id is activated\n"
		"  --timeout <seconds>        timeout for --wait* (default 10)\n"
		"  --protocol auto|ext|wlr    force protocol (default auto)\n"
		"  --help                     show this help\n",
		f);
}

int main(int argc, char **argv) {
	struct ctx c = {0};
	c.mode = PROTO_AUTO;
	double timeout = 10.0;

	enum { OPT_WAIT_ACT = 1000 };
	static const struct option opts[] = {
		{ "wait",           required_argument, 0, 'w' },
		{ "wait-activated", required_argument, 0, OPT_WAIT_ACT },
		{ "timeout",        required_argument, 0, 't' },
		{ "protocol",       required_argument, 0, 'p' },
		{ "help",           no_argument,       0, 'h' },
		{ 0, 0, 0, 0 },
	};
	int o;
	while ((o = getopt_long(argc, argv, "", opts, NULL)) != -1) {
		switch (o) {
		case 'w':         c.wait_app_id     = optarg; break;
		case OPT_WAIT_ACT: c.wait_act_app_id = optarg; break;
		case 't':         timeout = atof(optarg); break;
		case 'p':
			if (!strcmp(optarg, "auto")) c.mode = PROTO_AUTO;
			else if (!strcmp(optarg, "ext")) c.mode = PROTO_EXT;
			else if (!strcmp(optarg, "wlr")) c.mode = PROTO_WLR;
			else { usage(stderr); return 1; }
			break;
		case 'h': usage(stdout); return 0;
		default: usage(stderr); return 1;
		}
	}

	c.display = wl_display_connect(NULL);
	if (!c.display) {
		fprintf(stderr, "wl-probe: cannot connect to WAYLAND_DISPLAY\n");
		return 1;
	}
	struct wl_registry *reg = wl_display_get_registry(c.display);
	wl_registry_add_listener(reg, &reg_listener, &c);
	if (wl_display_roundtrip(c.display) < 0) {
		fprintf(stderr, "wl-probe: registry roundtrip failed\n");
		wl_display_disconnect(c.display);
		return 1;
	}

	bool want_ext = (c.mode == PROTO_AUTO || c.mode == PROTO_EXT) && c.ext_name;
	bool want_wlr = ((c.mode == PROTO_AUTO && !want_ext) || c.mode == PROTO_WLR) && c.wlr_name;

	if (!want_ext && !want_wlr) {
		fputs("{\"error\":\"no_protocol_advertised\",\"tried\":[\"ext\",\"wlr\"]}\n", stdout);
		fflush(stdout);
		wl_display_disconnect(c.display);
		return 3;
	}

	/* --wait-activated requires a protocol that actually exposes activation.
	 * The vendored ext_foreign_toplevel_list_v1 (v1) has no state event;
	 * only wlr does. If we'd land on ext, prefer wlr if also advertised,
	 * else bail with exit 3. */
	if (c.wait_act_app_id && want_ext && !c.wlr_name) {
		fputs("{\"error\":\"no_activation_state\",\"tried\":[\"ext\",\"wlr\"]}\n", stdout);
		fflush(stdout);
		wl_display_disconnect(c.display);
		return 3;
	}
	if (c.wait_act_app_id && want_ext && c.wlr_name && c.mode == PROTO_AUTO) {
		want_ext = false; want_wlr = true;
	}

	c.using_wlr = want_wlr;
	if (want_ext) {
		c.ext_list = wl_registry_bind(reg, c.ext_name,
		                              &ext_foreign_toplevel_list_v1_interface, 1);
		ext_foreign_toplevel_list_v1_add_listener(c.ext_list, &ext_l_listener, &c);
	} else {
		c.wlr_mgr = wl_registry_bind(reg, c.wlr_name,
		                             &zwlr_foreign_toplevel_manager_v1_interface,
		                             c.wlr_version ? c.wlr_version : 3);
		zwlr_foreign_toplevel_manager_v1_add_listener(c.wlr_mgr, &wlr_m_listener, &c);
	}

	/* Initial enumeration: two roundtrips — first surfaces toplevel events,
	 * second flushes the per-handle property events (title/app_id/state). */
	if (wl_display_roundtrip(c.display) < 0) goto disconnected;
	if (wl_display_roundtrip(c.display) < 0) goto disconnected;

	const char *waiting = c.wait_act_app_id ? c.wait_act_app_id : c.wait_app_id;

	/* Emit everything we know so far. tl_emit updates match_found. */
	for (struct toplevel *t = c.head; t; t = t->next) tl_emit(&c, t);

	if (waiting && !c.match_found) {
		double deadline = now_sec() + timeout;
		while (!c.match_found) {
			int r = dispatch_until(&c, deadline);
			if (r < 0) goto disconnected;
			if (r > 0) { /* timeout */
				fputs("{\"end\":true}\n", stdout);
				fflush(stdout);
				wl_display_disconnect(c.display);
				return 2;
			}
			/* Re-emit any toplevel whose state changed; for simplicity,
			 * we always emit those that haven't printed or that match the
			 * --wait-activated target (state may have flipped to active). */
			for (struct toplevel *t = c.head; t; t = t->next) {
				if (!t->printed_once || tl_matches(t, c.wait_act_app_id))
					tl_emit(&c, t);
			}
		}
	}

	fputs("{\"end\":true}\n", stdout);
	fflush(stdout);
	wl_display_disconnect(c.display);
	return 0;

disconnected:
	fputs("{\"end\":true}\n", stdout);
	fflush(stdout);
	if (c.display) wl_display_disconnect(c.display);
	return 1;
}
