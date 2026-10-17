################################################################################
#
# wxwidgets
#
################################################################################

WXWIDGETS_VERSION = v3.3.4
WXWIDGETS_SITE = https://github.com/wxWidgets/wxWidgets
WXWIDGETS_DEPENDENCIES = zlib libpng jpeg gdk-pixbuf libgtk3 libglu host-libgtk3 host-wayland wayland wayland-protocols
WXWIDGETS_SITE_METHOD = git
WXWIDGETS_GIT_SUBMODULES = YES

WXWIDGETS_SUPPORTS_IN_SOURCE_BUILD = NO
WXWIDGETS_INSTALL_STAGING = YES

WXWIDGETS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
WXWIDGETS_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
WXWIDGETS_CONF_OPTS += -DBUILD_STATIC_LIBS=ON

# Generate Wayland protocol headers using host wayland-scanner
# (CMake's pkg_get_variable returns the target path which is unusable in cross-compilation)
# 3.3.4 wants every protocol in src/unix/protocols, plus xdg-shell from
# wayland-protocols, once that package is found.
WXWIDGETS_WAYLAND_PROTOCOLS = \
	$(@D)/src/unix/protocols/*.xml \
	$(STAGING_DIR)/usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml

define WXWIDGETS_GENERATE_WAYLAND_PROTOCOLS
	mkdir -p $(@D)/include/wx/protocols
	for xml in $(WXWIDGETS_WAYLAND_PROTOCOLS); do \
		p=$$(basename $$xml .xml); \
		$(HOST_DIR)/bin/wayland-scanner client-header $$xml \
			$(@D)/include/wx/protocols/$$p-client-protocol.h || exit 1; \
		$(HOST_DIR)/bin/wayland-scanner private-code $$xml \
			$(@D)/include/wx/protocols/$$p-client-protocol.c || exit 1; \
	done
endef

WXWIDGETS_POST_CONFIGURE_HOOKS += WXWIDGETS_GENERATE_WAYLAND_PROTOCOLS

define WXWIDGETS_FIXUP_WXWIDGET_CONFIG
       ln -sf $(STAGING_DIR)/usr/lib/wx/config/*gtk3-unicode-* $(STAGING_DIR)/usr/bin/wx-config
	$(SED) 's%^prefix=.*%prefix=$(STAGING_DIR)/usr%' \
		$(STAGING_DIR)/usr/bin/wx-config
	$(SED) 's%^exec_prefix=.*%exec_prefix=$${prefix}%' \
		$(STAGING_DIR)/usr/bin/wx-config
endef

# When wxwidgets builds its bundled webp instead of using the system one, it
# emits libwxwebp/libwxwebpdemux/libwxsharpyuv next to the wx libraries but
# never installs them. libwx_gtk3u_core has a DT_NEEDED on all three, so both
# staging and target need them or anything linking wx fails (Cemu at link time,
# every wx app at runtime). Copy with -a to keep the SONAME symlinks.
WXWIDGETS_BUNDLED_WEBP_DIR = $(@D)/buildroot-build/lib

define WXWIDGETS_FIXUP_WEBP_LIBS_STAGING
	if ls $(WXWIDGETS_BUNDLED_WEBP_DIR)/libwxsharpyuv* >/dev/null 2>&1; then \
		cp -a $(WXWIDGETS_BUNDLED_WEBP_DIR)/libwxsharpyuv* $(STAGING_DIR)/usr/lib/ ; \
		cp -a $(WXWIDGETS_BUNDLED_WEBP_DIR)/libwxwebp* $(STAGING_DIR)/usr/lib/ ; \
	fi
endef

define WXWIDGETS_FIXUP_WEBP_LIBS_TARGET
	if ls $(WXWIDGETS_BUNDLED_WEBP_DIR)/libwxsharpyuv* >/dev/null 2>&1; then \
		cp -a $(WXWIDGETS_BUNDLED_WEBP_DIR)/libwxsharpyuv* $(TARGET_DIR)/usr/lib/ ; \
		cp -a $(WXWIDGETS_BUNDLED_WEBP_DIR)/libwxwebp* $(TARGET_DIR)/usr/lib/ ; \
	fi
endef

WXWIDGETS_POST_INSTALL_STAGING_HOOKS += WXWIDGETS_FIXUP_WXWIDGET_CONFIG
WXWIDGETS_POST_INSTALL_STAGING_HOOKS += WXWIDGETS_FIXUP_WEBP_LIBS_STAGING
WXWIDGETS_POST_INSTALL_TARGET_HOOKS += WXWIDGETS_FIXUP_WEBP_LIBS_TARGET

$(eval $(cmake-package))
