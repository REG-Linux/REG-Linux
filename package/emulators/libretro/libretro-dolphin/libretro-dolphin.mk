################################################################################
#
# libretro-dolphin
#
################################################################################
# Version: Commits on Apr 19, 2024
LIBRETRO_DOLPHIN_VERSION = 89a4df725d4eb24537728f7d655cddb1add25c18
LIBRETRO_DOLPHIN_SITE = $(call github,libretro,dolphin,$(LIBRETRO_DOLPHIN_VERSION))
LIBRETRO_DOLPHIN_LICENSE = GPLv2
LIBRETRO_DOLPHIN_DEPENDENCIES = libevdev fmt bluez5_utils

LIBRETRO_DOLPHIN_PLATFORM = $(LIBRETRO_PLATFORM)

LIBRETRO_DOLPHIN_CONF_OPTS = -DLIBRETRO=ON \
                             -DENABLE_NOGUI=OFF \
                             -DENABLE_QT=OFF \
                             -DENABLE_TESTS=OFF \
                             -DUSE_DISCORD_PRESENCE=OFF \
                             -DBUILD_SHARED_LIBS=OFF \
                             -DCMAKE_BUILD_TYPE=Release

ifeq ($(BR2_PACKAGE_XWAYLAND),y)
    LIBRETRO_DOLPHIN_DEPENDENCIES += xwayland
    LIBRETRO_DOLPHIN_CONF_OPTS += -DENABLE_X11=ON
else
    LIBRETRO_DOLPHIN_CONF_OPTS += -DENABLE_X11=OFF
endif

define LIBRETRO_DOLPHIN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/dolphin_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/dolphin_libretro.so
endef

define LIBRETRO_DOLPHIN_SYS_FOLDER
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/bios/dolphin-emu/Sys
	cp -r $(@D)/Data/Sys/* $(TARGET_DIR)/usr/share/reglinux/datainit/bios/dolphin-emu/Sys
endef

LIBRETRO_DOLPHIN_POST_INSTALL_TARGET_HOOKS += LIBRETRO_DOLPHIN_SYS_FOLDER

$(eval $(cmake-package))
