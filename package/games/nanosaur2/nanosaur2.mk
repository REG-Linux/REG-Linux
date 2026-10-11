################################################################################
#
# nanosaur2 — Pangea Software's Nanosaur 2 (open-sourced by Jorio)
#
################################################################################

NANOSAUR2_VERSION = v2.1.0
NANOSAUR2_SITE = https://github.com/jorio/Nanosaur2
NANOSAUR2_SITE_METHOD = git
NANOSAUR2_GIT_SUBMODULES = YES
NANOSAUR2_LICENSE = CC-BY-NC-SA-4.0
NANOSAUR2_LICENSE_FILES = LICENSE.md

NANOSAUR2_DEPENDENCIES = sdl2

NANOSAUR2_CONF_ENV = SDL2DIR="$(STAGING_DIR)/usr"
NANOSAUR2_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_CXX_FLAGS="-include cstdint"

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
NANOSAUR2_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
NANOSAUR2_DEPENDENCIES += gl4es libgles
NANOSAUR2_CONF_OPTS += \
	-DOPENGL_INCLUDE_DIR=$(STAGING_DIR)/usr/lib/gl4es \
	-DOPENGL_gl_LIBRARY=$(STAGING_DIR)/usr/lib/gl4es/libGL.so.1
endif

define NANOSAUR2_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/Nanosaur2 $(TARGET_DIR)/usr/bin/nanosaur2
	mkdir -p $(TARGET_DIR)/usr/share/nanosaur2
	cp -r $(@D)/Data $(TARGET_DIR)/usr/share/nanosaur2/
endef

$(eval $(cmake-package))
