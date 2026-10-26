/*
 * wl_fixes_interface (wayland >= 1.24) for when an older libwayland-client is
 * loaded first: PortMaster's Weston pack bundles one and puts it ahead in
 * LD_LIBRARY_PATH, and Mesa >= 26 libEGL references this symbol, so libEGL
 * would fail to load. Compositors that old never advertise wl_fixes, so Mesa
 * never actually uses it there. pack.sh makes libEGL NEED this library.
 */
#include <stddef.h>
struct wl_interface;
struct wl_message { const char *name; const char *signature; const struct wl_interface **types; };
struct wl_interface { const char *name; int version; int method_count;
	const struct wl_message *methods; int event_count; const struct wl_message *events; };
extern const struct wl_interface wl_registry_interface;
static const struct wl_interface *types[] = { NULL, &wl_registry_interface };
static const struct wl_message wl_fixes_requests[] = {
	{ "destroy", "", types + 0 },
	{ "destroy_registry", "o", types + 1 },
};
__attribute__((visibility("default")))
const struct wl_interface wl_fixes_interface = { "wl_fixes", 1, 2, wl_fixes_requests, 0, NULL };
