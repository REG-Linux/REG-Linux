################################################################################
#
# ares
#
################################################################################
# Version.: Release on Aug 27, 2024
ARES_VERSION = v140
ARES_SITE = $(call github,ares-emulator,ares,$(ARES_VERSION))
ARES_LICENSE = GPLv3
ARES_DEPENDENCIES = sdl2 libgl zlib

ARES_FLAGS = -I$(STAGING_DIR)/usr/include/glib-2.0 -I$(STAGING_DIR)/usr/lib/glib-2.0/include -I$(STAGING_DIR)/usr/include/pango-1.0 -I$(STAGING_DIR)/usr/include/cairo -I$(STAGING_DIR)/usr/include/harfbuzz -I$(STAGING_DIR)/usr/include/gtk-3.0 -I$(STAGING_DIR)/usr/include/gdk-pixbuf-2.0  -I$(STAGING_DIR)/usr/include/atk-1.0

define ARES_BUILD_CMDS
	SYSROOT="$(STAGING_DIR)" \
        PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
        PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
        CFLAGS="--sysroot=$(STAGING_DIR)" \
        CPPFLAGS="--sysroot=$(STAGING_DIR)" \
        CXXFLAGS="--sysroot=$(STAGING_DIR)" \
        LDFLAGS="--sysroot=$(STAGING_DIR)" \
	$(MAKE) compiler="$(TARGET_CC)" flags.cpp="$(ARES_FLAGS)" verbose local=false platform=linux hiro=gtk3 librashader=false vulkan=false -C $(@D) -f ./GNUmakefile
endef

$(eval $(generic-package))
