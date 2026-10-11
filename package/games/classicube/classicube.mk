################################################################################
#
# classicube — Minecraft Classic compatible client
#
################################################################################

CLASSICUBE_VERSION = 1.3.8
CLASSICUBE_SITE = https://github.com/ClassiCube/ClassiCube
CLASSICUBE_SITE_METHOD = git
CLASSICUBE_LICENSE = BSD-3-Clause
CLASSICUBE_LICENSE_FILES = misc/LICENSE

CLASSICUBE_DEPENDENCIES = sdl2

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
CLASSICUBE_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
CLASSICUBE_DEPENDENCIES += gl4es libgles
endif

# On GLES: replace X11/GL with gl4es path
define CLASSICUBE_FIX_GLES
	$(if $(BR2_PACKAGE_HAS_LIBGL),,\
		sed -i 's|-lX11 -lXi||g' $(@D)/Makefile && \
		sed -i 's|-lGL|-L$(STAGING_DIR)/usr/lib/gl4es -lGL|g' $(@D)/Makefile)
endef
CLASSICUBE_POST_PATCH_HOOKS += CLASSICUBE_FIX_GLES

define CLASSICUBE_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) sdl2 \
		CC="$(TARGET_CC)" \
		EXTRA_CFLAGS="$(TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)"
endef

define CLASSICUBE_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/ClassiCube $(TARGET_DIR)/usr/bin/classicube
endef

$(eval $(generic-package))
