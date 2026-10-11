################################################################################
#
# billyfrontier — Pangea Software's Billy Frontier (open-sourced by Jorio)
#
################################################################################

BILLYFRONTIER_VERSION = v1.1.1
BILLYFRONTIER_SITE = https://github.com/jorio/BillyFrontier
BILLYFRONTIER_SITE_METHOD = git
BILLYFRONTIER_GIT_SUBMODULES = YES
BILLYFRONTIER_LICENSE = CC-BY-NC-SA-4.0
BILLYFRONTIER_LICENSE_FILES = LICENSE.md

BILLYFRONTIER_DEPENDENCIES = sdl2

BILLYFRONTIER_CONF_ENV = SDL2DIR="$(STAGING_DIR)/usr"
BILLYFRONTIER_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
BILLYFRONTIER_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
BILLYFRONTIER_DEPENDENCIES += gl4es libgles
BILLYFRONTIER_CONF_OPTS += \
	-DOPENGL_INCLUDE_DIR=$(STAGING_DIR)/usr/lib/gl4es \
	-DOPENGL_gl_LIBRARY=$(STAGING_DIR)/usr/lib/gl4es/libGL.so.1
endif

define BILLYFRONTIER_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/BillyFrontier $(TARGET_DIR)/usr/bin/billyfrontier
	mkdir -p $(TARGET_DIR)/usr/share/billyfrontier
	cp -r $(@D)/Data $(TARGET_DIR)/usr/share/billyfrontier/
endef

$(eval $(cmake-package))
