################################################################################
#
# cromagrally — Caveman kart racing game (Pangea Software, open-sourced)
#
################################################################################

CROMAGRALLY_VERSION = 3.0.1
CROMAGRALLY_SITE = https://github.com/jorio/CroMagRally
CROMAGRALLY_SITE_METHOD = git
CROMAGRALLY_GIT_SUBMODULES = YES
CROMAGRALLY_LICENSE = CC-BY-NC-SA-4.0
CROMAGRALLY_LICENSE_FILES = LICENSE.md

CROMAGRALLY_DEPENDENCIES = sdl2

CROMAGRALLY_CONF_ENV = SDL2DIR="$(STAGING_DIR)/usr"
CROMAGRALLY_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
CROMAGRALLY_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
# Legacy GL 1.x game — use gl4es translation layer on GLES platforms
CROMAGRALLY_DEPENDENCIES += gl4es libgles
CROMAGRALLY_CONF_OPTS += \
	-DOPENGL_INCLUDE_DIR=$(STAGING_DIR)/usr/lib/gl4es \
	-DOPENGL_gl_LIBRARY=$(STAGING_DIR)/usr/lib/gl4es/libGL.so.1
endif

define CROMAGRALLY_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/CroMagRally $(TARGET_DIR)/usr/bin/cromagrally
	mkdir -p $(TARGET_DIR)/usr/share/cromagrally
	cp -r $(@D)/Data $(TARGET_DIR)/usr/share/cromagrally/
endef

$(eval $(cmake-package))
