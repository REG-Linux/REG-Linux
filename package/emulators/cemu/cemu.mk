################################################################################
#
# cemu
#
################################################################################

# Unstable because of WIP aarch64 upstreamed support
CEMU_VERSION = a04eb53822d306435f4efaba36225bc3bd297f5d
CEMU_SITE = https://github.com/cemu-project/Cemu
CEMU_LICENSE = GPLv2
CEMU_SITE_METHOD=git
CEMU_GIT_SUBMODULES=YES

# Target dependencies
# hidapi and bluez5_utils are required for Wiimote support (selected in Config.in)
CEMU_DEPENDENCIES = sdl2 pugixml rapidjson boost libpng libcurl libzip zlib zstd \
                    wxwidgets fmt glm upower libusb bluez5_utils webp cubeb hidapi \
                    host-glslang glslang host-nasm host-zstd host-libusb

CEMU_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CEMU_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
CEMU_CONF_OPTS += -DENABLE_DISCORD_RPC=OFF
CEMU_CONF_OPTS += -DENABLE_VCPKG=OFF
CEMU_CONF_OPTS += -DUNIX=ON -DENABLE_SDL=ON -DENABLE_CUBEB=ON -DENABLE_BLUEZ=ON -DENABLE_HIDAPI=ON
CEMU_CONF_OPTS += -DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) -I$(STAGING_DIR)/usr/include/glslang"
# Suppress unused Buildroot variables warnings
CEMU_CONF_OPTS += -DBUILD_DOC=OFF -DBUILD_DOCS=OFF -DBUILD_EXAMPLE=OFF
CEMU_CONF_OPTS += -DBUILD_EXAMPLES=OFF -DBUILD_TEST=OFF -DBUILD_TESTS=OFF
CEMU_CONF_OPTS += -DBUILD_TESTING=OFF -DCMAKE_POLICY_DEFAULT_CMP0069=NEW

# Ensure CMake finds system cubeb (not bundled submodule)
CEMU_CONF_ENV += PKG_CONFIG_PATH=$(STAGING_DIR)/usr/lib/pkgconfig

# Suppress hidapi find_package warning (name mismatch)
CEMU_CONF_OPTS += -Wno-dev

# aarch64 requires lax vector conversions
ifeq ($(BR2_aarch64),y)
    CEMU_CONF_OPTS += -DCEMU_CXX_FLAGS=-flax-vector-conversions
endif

# REG configure OpenGL
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    CEMU_DEPENDENCIES += libgl
    CEMU_CONF_OPTS += -DENABLE_OPENGL=ON
else
    CEMU_CONF_OPTS += -DENABLE_OPENGL=OFF
endif

# REG enable gamemode (optional)
ifeq ($(BR2_PACKAGE_GAMEMODE),y)
    CEMU_DEPENDENCIES += gamemode
    CEMU_CONF_OPTS += -DENABLE_FERAL_GAMEMODE=ON
else
    CEMU_CONF_OPTS += -DENABLE_FERAL_GAMEMODE=OFF
endif

# REG enable Wayland support
ifeq ($(BR2_PACKAGE_WAYLAND),y)
    CEMU_CONF_OPTS += -DENABLE_WAYLAND=ON
    CEMU_DEPENDENCIES += wayland wayland-protocols
else
    CEMU_CONF_OPTS += -DENABLE_WAYLAND=OFF
endif

# REG enable Vulkan support
ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    CEMU_CONF_OPTS += -DENABLE_VULKAN=ON
    CEMU_DEPENDENCIES += vulkan-headers vulkan-loader
else
    CEMU_CONF_OPTS += -DENABLE_VULKAN=OFF
endif

define CEMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/cemu/
	mv -f $(@D)/bin/Cemu_release $(@D)/bin/cemu
	cp -pr $(@D)/bin/{cemu,gameProfiles,resources} $(TARGET_DIR)/usr/bin/cemu/
endef

$(eval $(cmake-package))
