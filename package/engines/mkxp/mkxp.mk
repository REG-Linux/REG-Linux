################################################################################
#
# mkxp — RPG Maker XP/VX/VX Ace player (Falcon-mkxp fork)
#
################################################################################

MKXP_VERSION = 104d66d81c47e0848d10b61fb426cc833e7c3f6b
MKXP_SITE = https://github.com/pk-2000/Falcon-mkxp
MKXP_SITE_METHOD = git

MKXP_LICENSE = GPL-2.0+
MKXP_LICENSE_FILES = COPYING

MKXP_DEPENDENCIES = boost sdl2 sdl2_image sdl2_ttf sdl_sound \
	openal physfs pixman libsigc libvorbis libogg zlib ruby

# Use system Ruby via pkg-config (Buildroot's ruby provides ruby-3.4.pc)
MKXP_CONF_OPTS = \
	-DBINDING=MRI \
	-DMRIVERSION=3.4 \
	-DSHARED_FLUID=ON \
	-DWORKDIR_CURRENT=OFF

ifeq ($(BR2_PACKAGE_FLUIDSYNTH),y)
MKXP_DEPENDENCIES += fluidsynth
MKXP_CONF_OPTS += -DSHARED_FLUID=ON
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
MKXP_DEPENDENCIES += libgles
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
MKXP_DEPENDENCIES += libgl
endif

define MKXP_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/mkxp $(TARGET_DIR)/usr/bin/mkxp
endef

$(eval $(cmake-package))
