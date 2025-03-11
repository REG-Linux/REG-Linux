################################################################################
#
# CITRON
#
################################################################################
# Version: v0.5-canary-refresh
CITRON_VERSION = v0.5-canary-refresh
CITRON_SITE = https://git.citron-emu.org/Citron/Citron
CITRON_SITE_METHOD=git
CITRON_GIT_SUBMODULES=YES
CITRON_LICENSE = GPLv2
CITRON_DEPENDENCIES = reglinux-qt6 fmt boost ffmpeg \
                    zstd zlib libzip lz4 catch2 sdl2 opus json-for-modern-cpp enet

CITRON_SUPPORTS_IN_SOURCE_BUILD = NO

CITRON_CONF_ENV += LDFLAGS=-lpthread

CITRON_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CITRON_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
CITRON_CONF_OPTS += -DENABLE_SDL2=ON
CITRON_CONF_OPTS += -DENABLE_QT6=ON
CITRON_CONF_OPTS += -DCITRON_USE_EXTERNAL_SDL2=OFF
CITRON_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
CITRON_CONF_OPTS += -DCITRON_TESTS=OFF
CITRON_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
CITRON_CONF_OPTS += -DUSE_SANITIZERS=OFF
ifeq ($(BR2_aarch64),y)
CITRON_CONF_ENV += ARCHITECTURE_arm64=1
CITRON_CONF_OPTS += -DARCHITECTURE_arm64=ON
CITRON_CONF_OPTS += -DENABLE_LIBUSB=OFF
else ifeq ($(BR2_x86_64),y)
CITRON_CONF_ENV += ARCHITECTURE_x86_64=1
CITRON_CONF_OPTS += -DARCHITECTURE_x86_64=ON
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),yy)
    CITRON_DEPENDENCIES += host-glslang vulkan-headers vulkan-loader
endif

define CITRON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    mkdir -p $(TARGET_DIR)/usr/lib/citron
    $(INSTALL) -D $(@D)/buildroot-build/bin/citron $(TARGET_DIR)/usr/bin/
    $(INSTALL) -D $(@D)/buildroot-build/bin/citron-cmd $(TARGET_DIR)/usr/bin/
    $(INSTALL) -D $(@D)/buildroot-build/bin/citron-room $(TARGET_DIR)/usr/bin/
    #evmap config
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp -prn $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/citron/switch.citron.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

# Ugly hack because lz4 is not installed with CMake and pkgconfig returns
# $(STAGING_DIR)/usr/local/include which does NOT exist
define CITRON_CREATE_STAGING_USR_LOCAL_INCLUDE
    mkdir -p $(STAGING_DIR)/usr/local/include
endef
CITRON_PRE_CONFIGURE_HOOKS += CITRON_CREATE_STAGING_USR_LOCAL_INCLUDE

$(eval $(cmake-package))
