################################################################################
#
# cemu
#
################################################################################

# Unstable because of WIP aarch64 upstreamed support
CEMU_VERSION = 4fe73a3582187e721619eb728c7c1ae3e28c0375
CEMU_SITE = https://github.com/cemu-project/Cemu
CEMU_LICENSE = GPLv2
CEMU_SITE_METHOD=git
CEMU_GIT_SUBMODULES=YES
CEMU_DEPENDENCIES = sdl2 host-pugixml pugixml rapidjson boost libpng libcurl \
                    libzip host-glslang glslang zlib zstd wxwidgets fmt glm upower \
                    host-nasm host-zstd host-libusb libusb bluez5_utils webp

CEMU_SUPPORTS_IN_SOURCE_BUILD = NO

CEMU_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CEMU_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
CEMU_CONF_OPTS += -DENABLE_DISCORD_RPC=OFF
CEMU_CONF_OPTS += -DENABLE_VCPKG=OFF
CEMU_CONF_OPTS += -DUNIX=ON -DENABLE_SDL=ON -DENABLE_CUBEB=ON -DENABLE_BLUEZ=ON
CEMU_CONF_OPTS += -DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) -I$(STAGING_DIR)/usr/include/glslang"

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

# REG enable gamemode
ifeq ($(BR2_PACKAGE_GAMEMODE),y)
    CEMU_DEPENDENCIES += gamemode
    CEMU_CONF_OPTS += -DENABLE_FERAL_GAMEMODE=ON
else
    CEMU_CONF_OPTS += -DENABLE_FERAL_GAMEMODE=OFF
endif

# REG enable HIDAPI
ifeq ($(BR2_PACKAGE_HIDAPI),y)
    CEMU_DEPENDENCIES += hidapi
    CEMU_CONF_OPTS += -DENABLE_HIDAPI=ON
else
    CEMU_CONF_OPTS += -DENABLE_HIDAPI=OFF
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
    CEMU_CONF_OPTS += -DENABLE_WAYLAND=ON
    CEMU_DEPENDENCIES += wayland wayland-protocols
else
    CEMU_CONF_OPTS += -DENABLE_WAYLAND=OFF
endif

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
	$(INSTALL) -m 0755 -D \
	    $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/cemu/get-audio-device \
	    $(TARGET_DIR)/usr/bin/cemu/
	# keys.txt
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/bios/cemu
	touch $(TARGET_DIR)/usr/share/reglinux/datainit/bios/cemu/keys.txt
	#evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -pr $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/cemu/wiiu.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
