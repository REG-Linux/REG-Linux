################################################################################
#
# Azahar
#
################################################################################

AZAHAR_VERSION = 2126.2
AZAHAR_SITE = https://github.com/azahar-emu/azahar.git
AZAHAR_SITE_METHOD = git
AZAHAR_GIT_SUBMODULES = YES
AZAHAR_LICENSE = GPLv2
AZAHAR_SUPPORTS_IN_SOURCE_BUILD = NO

# Core dependencies
AZAHAR_DEPENDENCIES += fmt boost ffmpeg sdl2 fdk-aac cubeb
AZAHAR_DEPENDENCIES += openssl libzip lz4 zstd
AZAHAR_DEPENDENCIES += libdrm libinput libxkbcommon

# Qt6 is the only frontend: upstream dropped the SDL2 one (citra_meta,
# which produces the azahar binary, is only built with ENABLE_QT)
AZAHAR_DEPENDENCIES += reglinux-qt6

# Vulkan and graphics dependencies
ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    AZAHAR_DEPENDENCIES += vulkan-headers vulkan-loader
endif

# Not needed since 2126.1
#ifeq ($(BR2_PACKAGE_XWAYLAND),y)
#    AZAHAR_DEPENDENCIES += xwayland
#endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
    AZAHAR_DEPENDENCIES += wayland wayland-protocols
endif

# OpenGL dependencies
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    AZAHAR_DEPENDENCIES += libgl
endif

AZAHAR_BUILD_TYPE = Release

AZAHAR_CONF_OPTS += -DCMAKE_BUILD_TYPE=$(AZAHAR_BUILD_TYPE)
AZAHAR_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
AZAHAR_CONF_OPTS += -DENABLE_SDL2=ON
AZAHAR_CONF_OPTS += -DENABLE_TESTS=OFF
AZAHAR_CONF_OPTS += -DENABLE_ROOM_STANDALONE=OFF
AZAHAR_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
AZAHAR_CONF_OPTS += -DENABLE_OPENAL=OFF
AZAHAR_CONF_OPTS += -DENABLE_CUBEB=ON
AZAHAR_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
AZAHAR_CONF_OPTS += -DUSE_SYSTEM_BOOST=ON
AZAHAR_CONF_OPTS += -DUSE_SYSTEM_SDL2=ON
AZAHAR_CONF_OPTS += -DENABLE_LTO=ON

# Use SSE 4.2 code paths on x86_64_v3 build
ifeq ($(BR2_x86_x86_64_v3),y)
    AZAHAR_CONF_OPTS += -DENABLE_SSE42=ON
else
    AZAHAR_CONF_OPTS += -DENABLE_SSE42=OFF
endif

# Qt frontend (SDL2 stays enabled above for input)
AZAHAR_BIN = azahar
AZAHAR_CONF_OPTS += -DENABLE_QT=ON
AZAHAR_CONF_OPTS += -DENABLE_QT_TRANSLATION=ON
AZAHAR_CONF_OPTS += -DENABLE_QT_UPDATE_CHECKER=OFF

# Vulkan support
ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    AZAHAR_CONF_OPTS += -DENABLE_VULKAN=ON
else
    AZAHAR_CONF_OPTS += -DENABLE_VULKAN=OFF
endif

# Silence Qt private module warning (we know about the version coupling)
AZAHAR_CONF_ENV += QT_NO_PRIVATE_MODULE_WARNING=ON

AZAHAR_CONF_ENV += LDFLAGS="-lpthread -ldl"

define AZAHAR_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/bin/$(AZAHAR_BUILD_TYPE)/$(AZAHAR_BIN) \
    	$(TARGET_DIR)/usr/bin/
endef

$(eval $(cmake-package))
