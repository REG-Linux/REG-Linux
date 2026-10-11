################################################################################
#
# srb2 — Sonic Robo Blast 2 (3D Sonic fan game on Doom Legacy engine)
#
################################################################################

SRB2_VERSION = SRB2_release_2.2.15
SRB2_SITE = https://github.com/STJr/SRB2
SRB2_SITE_METHOD = git
SRB2_LICENSE = GPL-2.0
SRB2_LICENSE_FILES = LICENSE
SRB2_SUPPORTS_IN_SOURCE_BUILD = NO

SRB2_DEPENDENCIES = sdl2 sdl2_mixer libpng zlib libcurl

# Fix C23: true/false are keywords, can't be used as enum constants
define SRB2_FIX_C23_BOOL
	sed -i 's/enum {false = 0, true = 1};/#include <stdbool.h>/' $(@D)/src/doomtype.h
endef
SRB2_POST_PATCH_HOOKS += SRB2_FIX_C23_BOOL

SRB2_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_C_FLAGS="-Wno-error=incompatible-pointer-types -Wno-error=int-conversion" \
	-DSRB2_CONFIG_ENABLE_TESTS=OFF \
	-DSRB2_CONFIG_SYSTEM_LIBRARIES=ON \
	-DSRB2_SDL2_EXE_NAME=srb2 \
	-DCMAKE_DISABLE_FIND_PACKAGE_Git=ON

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
SRB2_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
SRB2_DEPENDENCIES += libgles
endif

define SRB2_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/bin/srb2 $(TARGET_DIR)/usr/bin/srb2
endef

$(eval $(cmake-package))
