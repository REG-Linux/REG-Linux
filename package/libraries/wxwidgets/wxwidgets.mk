################################################################################
#
# wxwidgets
#
################################################################################

WXWIDGETS_VERSION = v3.3.2
WXWIDGETS_SITE = https://github.com/wxWidgets/wxWidgets
WXWIDGETS_DEPENDENCIES = zlib libpng jpeg gdk-pixbuf libgtk3 libglu host-libgtk3 host-wayland wayland
WXWIDGETS_SITE_METHOD = git
WXWIDGETS_GIT_SUBMODULES = YES

WXWIDGETS_SUPPORTS_IN_SOURCE_BUILD = NO
WXWIDGETS_INSTALL_STAGING = YES

WXWIDGETS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
WXWIDGETS_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
WXWIDGETS_CONF_OPTS += -DBUILD_STATIC_LIBS=ON

# Generate Wayland protocol headers using host wayland-scanner
# (CMake's pkg_get_variable returns the target path which is unusable in cross-compilation)
define WXWIDGETS_GENERATE_WAYLAND_PROTOCOLS
	mkdir -p $(@D)/include/wx/protocols
	$(HOST_DIR)/bin/wayland-scanner client-header \
		$(@D)/src/unix/protocols/pointer-warp-v1.xml \
		$(@D)/include/wx/protocols/pointer-warp-v1-client-protocol.h
	$(HOST_DIR)/bin/wayland-scanner private-code \
		$(@D)/src/unix/protocols/pointer-warp-v1.xml \
		$(@D)/include/wx/protocols/pointer-warp-v1-client-protocol.c
endef

WXWIDGETS_POST_CONFIGURE_HOOKS += WXWIDGETS_GENERATE_WAYLAND_PROTOCOLS

define WXWIDGETS_FIXUP_WXWIDGET_CONFIG
       ln -sf $(STAGING_DIR)/usr/lib/wx/config/*gtk3-unicode-* $(STAGING_DIR)/usr/bin/wx-config
	$(SED) 's%^prefix=.*%prefix=$(STAGING_DIR)/usr%' \
		$(STAGING_DIR)/usr/bin/wx-config
	$(SED) 's%^exec_prefix=.*%exec_prefix=$${prefix}%' \
		$(STAGING_DIR)/usr/bin/wx-config
endef

define WXWIDGETS_FIXUP_WEBP_LIBS_STAGING
	cp $(@D)/buildroot-build/libs/webp-build/libwxsharpyuv* $(STAGING_DIR)/usr/lib/
	cp $(@D)/buildroot-build/libs/webp-build/libwxwebp* $(STAGING_DIR)/usr/lib/
endef

define WXWIDGETS_FIXUP_WEBP_LIBS_TARGET
	cp $(@D)/buildroot-build/libs/webp-build/libwxsharpyuv* $(TARGET_DIR)/usr/lib/
	cp $(@D)/buildroot-build/libs/webp-build/libwxwebp* $(TARGET_DIR)/usr/lib/
endef

WXWIDGETS_POST_INSTALL_STAGING_HOOKS += WXWIDGETS_FIXUP_WXWIDGET_CONFIG
WXWIDGETS_POST_INSTALL_STAGING_HOOKS += WXWIDGETS_FIXUP_WEBP_LIBS_STAGING
WXWIDGETS_POST_INSTALL_TARGET_HOOKS += WXWIDGETS_FIXUP_WEBP_LIBS_TARGET

$(eval $(cmake-package))
