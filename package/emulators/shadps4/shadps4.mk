################################################################################
#
# shadps4
#
################################################################################

SHADPS4_VERSION = v.0.15.0
SHADPS4_SITE = https://github.com/shadps4-emu/shadPS4.git
SHADPS4_SITE_METHOD=git
SHADPS4_GIT_SUBMODULES=YES
SHADPS4_LICENSE = GPLv2
SHADPS4_LICENSE_FILE = LICENSE
SHADPS4_DEPENDENCIES += alsa-lib pulseaudio openal openssl zlib libedit udev
SHADPS4_DEPENDENCIES += libevdev jack2 ffmpeg
SHADPS4_DEPENDENCIES += vulkan-headers vulkan-loader vulkan-validationlayers
SHADPS4_DEPENDENCIES += boost fmt glslang sdl3
SHADPS4_DEPENDENCIES += xlib_libX11 xlib_libXext xlib_libXcursor xlib_libXi
SHADPS4_DEPENDENCIES += xlib_libXrandr xlib_libXScrnSaver xlib_libXtst

SHADPS4_SUPPORTS_IN_SOURCE_BUILD = NO

SHADPS4_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SHADPS4_CONF_OPTS += -DCMAKE_INSTALL_PREFIX=/usr
SHADPS4_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
SHADPS4_CONF_OPTS += -DENABLE_DISCORD_RPC=OFF
SHADPS4_CONF_OPTS += -DENABLE_UPDATER=OFF
SHADPS4_CONF_OPTS += -DSDL_X11_XSCRNSAVER=OFF

define SHADPS4_INSTALL_TARGET_CMDS
	 mkdir -p $(TARGET_DIR)/usr/bin/shadps4
	 $(INSTALL) -m 0755 $(@D)/buildroot-build/shadps4 $(TARGET_DIR)/usr/bin/shadps4/
endef

$(eval $(cmake-package))
