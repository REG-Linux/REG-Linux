################################################################################
#
# wxwidgets
#
################################################################################

WXWIDGETS_VERSION = v3.3.1
WXWIDGETS_SITE = https://github.com/wxWidgets/wxWidgets
WXWIDGETS_DEPENDENCIES = zlib libpng jpeg gdk-pixbuf libgtk3 libglu
WXWIDGETS_SITE_METHOD = git
WXWIDGETS_GIT_SUBMODULES = YES
WXWIDGETS_DEPENDENCIES = host-libgtk3 libgtk3

WXWIDGETS_SUPPORTS_IN_SOURCE_BUILD = NO
WXWIDGETS_INSTALL_STAGING = YES

WXWIDGETS_CONFIGURE_OPTS += -DCMAKE_BUILD_TYPE=Release
WXWIDGETS_CONFIGURE_OPTS += -DBUILD_SHARED_LIBS=ON
WXWIDGETS_CONFIGURE_OPTS += -DBUILD_STATIC_LIBS=ON

define WXWIDGETS_FIXUP_WXWIDGET_CONFIG
       ln -sf $(STAGING_DIR)/usr/lib/wx/config/*gtk3-unicode-* $(STAGING_DIR)/usr/bin/wx-config
	$(SED) 's%^prefix=.*%prefix=$(STAGING_DIR)/usr%' \
		$(STAGING_DIR)/usr/bin/wx-config
	$(SED) 's%^exec_prefix=.*%exec_prefix=$${prefix}%' \
		$(STAGING_DIR)/usr/bin/wx-config
endef

define WXWIDGETS_FIXUP_WEBP_LIBS_STAGING
	cp $(@D)/buildroot-build/libs/webp-build/wxsharpyuv* $(STAGING_DIR)/usr/lib/
	cp $(@D)/buildroot-build/libs/webp-build/wxwebp* $(STAGING_DIR)/usr/lib/
endef

define WXWIDGETS_FIXUP_WEBP_LIBS_TARGET
	cp $(@D)/buildroot-build/libs/webp-build/wxsharpyuv* $(TARGET_DIR)/usr/lib/
	cp $(@D)/buildroot-build/libs/webp-build/wxwebp* $(TARGET_DIR)/usr/lib/
endef

WXWIDGETS_POST_INSTALL_STAGING_HOOKS += WXWIDGETS_FIXUP_WXWIDGET_CONFIG
WXWIDGETS_POST_INSTALL_STAGING_HOOKS += WXWIDGETS_FIXUP_WEBP_LIBS_STAGING
WXWIDGETS_POST_INSTALL_TARGET_HOOKS += WXWIDGETS_FIXUP_WEBP_LIBS_TARGET

$(eval $(cmake-package))
