################################################################################
#
# SUDACHI
#
################################################################################
# Version: Commits on May 27, 2024
SUDACHI_VERSION = v1.0.2
SUDACHI_SITE = https://github.com/sudachi-emu/sudachi.git
SUDACHI_SITE_METHOD=git
SUDACHI_GIT_SUBMODULES=YES
SUDACHI_LICENSE = GPLv2
SUDACHI_DEPENDENCIES = reglinux-qt6 fmt boost ffmpeg \
                    zstd zlib libzip lz4 catch2 sdl2 opus json-for-modern-cpp

SUDACHI_SUPPORTS_IN_SOURCE_BUILD = NO

SUDACHI_CONF_ENV += LDFLAGS=-lpthread

SUDACHI_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SUDACHI_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
SUDACHI_CONF_OPTS += -DENABLE_SDL2=ON
SUDACHI_CONF_OPTS += -DENABLE_QT6=ON
SUDACHI_CONF_OPTS += -DSUDACHI_USE_EXTERNAL_SDL2=OFF
SUDACHI_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
SUDACHI_CONF_OPTS += -DSUDACHI_TESTS=OFF
SUDACHI_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF

ifeq ($(BR2_aarch64),y)
SUDACHI_CONF_ENV += ARCHITECTURE_arm64=1
SUDACHI_CONF_OPTS += -DARCHITECTURE_arm64=ON
SUDACHI_CONF_OPTS += -DENABLE_LIBUSB=OFF
else ifeq ($(BR2_x86_64),y)
SUDACHI_CONF_ENV += ARCHITECTURE_x86_64=1
SUDACHI_CONF_OPTS += -DARCHITECTURE_x86_64=ON
endif

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    SUDACHI_DEPENDENCIES += host-glslang vulkan-headers vulkan-loader
endif

define SUDACHI_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    mkdir -p $(TARGET_DIR)/usr/lib/sudachi
    $(INSTALL) -D $(@D)/buildroot-build/bin/sudachi $(TARGET_DIR)/usr/bin/
    $(INSTALL) -D $(@D)/buildroot-build/bin/sudachi-cmd $(TARGET_DIR)/usr/bin/
    $(INSTALL) -D $(@D)/buildroot-build/bin/sudachi-room $(TARGET_DIR)/usr/bin/
    #evmap config
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/emulators/sudachi/switch.sudachi.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
