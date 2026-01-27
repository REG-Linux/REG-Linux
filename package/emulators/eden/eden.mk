################################################################################
#
# EDEN
#
################################################################################

EDEN_VERSION = v0.1.0
EDEN_SITE = https://git.eden-emu.dev/eden-emu/eden
EDEN_SITE_METHOD=git
EDEN_GIT_SUBMODULES=YES
EDEN_LICENSE = GPLv2
EDEN_DEPENDENCIES = reglinux-qt6 fmt boost gamemode \
                    zstd zlib libzip lz4 catch2 sdl2 opus \
		    json-for-modern-cpp enet libva xwayland \
		    libusb ffmpeg mbedtls

EDEN_SUPPORTS_IN_SOURCE_BUILD = NO

EDEN_CONF_ENV += LDFLAGS=-lpthread

EDEN_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
EDEN_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
EDEN_CONF_OPTS += -DENABLE_SDL2=ON
EDEN_CONF_OPTS += -DENABLE_QT6=ON
EDEN_CONF_OPTS += -DYUZU_USE_EXTERNAL_SDL2=OFF
EDEN_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
EDEN_CONF_OPTS += -DEDEN_TESTS=OFF
EDEN_CONF_OPTS += -DENABLE_WEB_SERVICE=ON
EDEN_CONF_OPTS += -DUSE_SANITIZERS=OFF
EDEN_CONF_OPTS += -DLINUX=ON
EDEN_CONF_OPTS += -DYUZU_CHECK_SUBMODULES=OFF
EDEN_CONF_OPTS += -DYUZU_USE_CPM=OFF
EDEN_CONF_OPTS += -DENABLE_CUBEB=OFF
EDEN_CONF_OPTS += -DENABLE_LIBUSB=ON
EDEN_CONF_OPTS += -DENABLE_LTO=ON
EDEN_CONF_OPTS += -DYUZU_USE_BUNDLED_FFMPEG=OFF
ifeq ($(BR2_aarch64),y)
EDEN_CONF_ENV += ARCHITECTURE_arm64=1
EDEN_CONF_OPTS += -DARCHITECTURE_arm64=ON
else ifeq ($(BR2_x86_64),y)
EDEN_CONF_ENV += ARCHITECTURE_x86_64=1
EDEN_CONF_OPTS += -DARCHITECTURE_x86_64=ON
EDEN_DEPENDENCIES += host-yasm
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),yy)
    EDEN_DEPENDENCIES += host-glslang vulkan-headers vulkan-loader
endif

define EDEN_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    mkdir -p $(TARGET_DIR)/usr/lib/eden
    $(INSTALL) -D $(@D)/buildroot-build/bin/eden $(TARGET_DIR)/usr/bin/
    $(INSTALL) -D $(@D)/buildroot-build/bin/eden-cli $(TARGET_DIR)/usr/bin/
    $(INSTALL) -D $(@D)/buildroot-build/bin/eden-room $(TARGET_DIR)/usr/bin/
    #evmap config
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp -prn $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/eden/switch.eden.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

# Ugly hack because lz4 is not installed with CMake and pkgconfig returns
# $(STAGING_DIR)/usr/local/include which does NOT exist
define EDEN_CREATE_STAGING_USR_LOCAL_INCLUDE
    mkdir -p $(STAGING_DIR)/usr/local/include
endef
EDEN_PRE_CONFIGURE_HOOKS += EDEN_CREATE_STAGING_USR_LOCAL_INCLUDE

$(eval $(cmake-package))
