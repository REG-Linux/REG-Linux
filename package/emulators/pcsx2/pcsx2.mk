################################################################################
#
# pcsx2
#
################################################################################
# Version v2.6.3 on Jan 29, 2025
PCSX2_VERSION = v2.6.3
PCSX2_SITE = https://github.com/pcsx2/pcsx2.git
PCSX2_SITE_METHOD = git
PCSX2_GIT_SUBMODULES = YES
PCSX2_LICENSE = GPLv3
PCSX2_LICENSE_FILE = COPYING.GPLv3

PCSX2_SUPPORTS_IN_SOURCE_BUILD = NO

PCSX2_DEPENDENCIES += xorgproto alsa-lib freetype zlib libpng shaderc ecm
PCSX2_DEPENDENCIES += libaio portaudio libsoundtouch sdl3 libpcap yaml-cpp
PCSX2_DEPENDENCIES += libsamplerate fmt reglinux-qt6 libcurl kddockwidgets
PCSX2_DEPENDENCIES += libbacktrace jpeg webp plutosvg

# Use clang for performance if available
ifeq ($(BR2_PACKAGE_CLANG),y)
PCSX2_DEPENDENCIES += clang
PCSX2_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang
PCSX2_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++
PCSX2_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-lm -lstdc++"
endif

PCSX2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
PCSX2_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
PCSX2_CONF_OPTS += -DENABLE_TESTS=OFF
PCSX2_CONF_OPTS += -DUSE_SYSTEM_LIBS=AUTO
# The following flag is misleading and *needed* ON to avoid doing -march=native
ifeq ($(BR2_x86_64),y)
PCSX2_CONF_OPTS += -DDISABLE_ADVANCE_SIMD=ON
endif

# Since v2.3.168 Wayland is ON by default, should disable X11 but does not build yet
PCSX2_CONF_OPTS += -DWAYLAND_API=ON
PCSX2_CONF_OPTS += -DX11_API=ON

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    PCSX2_CONF_OPTS += -DUSE_OPENGL=ON
    PCSX2_DEPENDENCIES += libgl
else
    PCSX2_CONF_OPTS += -DUSE_OPENGL=OFF
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    PCSX2_CONF_OPTS += -DUSE_VULKAN=ON
    PCSX2_DEPENDENCIES += vulkan-headers
else
    PCSX2_CONF_OPTS += -DUSE_VULKAN=OFF
endif

define PCSX2_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/buildroot-build/bin/pcsx2-qt \
        $(TARGET_DIR)/usr/pcsx2/bin/pcsx2-qt
	cp -pr  $(@D)/bin/resources $(TARGET_DIR)/usr/pcsx2/bin/
    cp -pr  $(@D)/buildroot-build/bin/translations $(TARGET_DIR)/usr/pcsx2/bin/
    # use our SDL config
    rm $(TARGET_DIR)/usr/pcsx2/bin/resources/game_controller_db.txt
endef

define PCSX2_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/pcsx2/ps2.pcsx2.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_EVMAPY

define PCSX2_TEXTURES
	mkdir -p $(TARGET_DIR)/usr/pcsx2/bin/resources/textures
	cp -pr $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/pcsx2/textures/ \
        $(TARGET_DIR)/usr/pcsx2/bin/resources/
endef

# Download and copy PCSX2 patches.zip to BIOS folder
define PCSX2_PATCHES
    mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/bios/ps2
    curl -L \
        https://github.com/PCSX2/pcsx2_patches/releases/download/latest/patches.zip -o \
        $(TARGET_DIR)/usr/share/reglinux/datainit/bios/ps2/patches.zip
endef

PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_TEXTURES
PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_PATCHES

define PCSX2_CROSSHAIRS
	mkdir -p $(TARGET_DIR)/usr/pcsx2/bin/resources/crosshairs
	cp -pr $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/pcsx2/crosshairs/ \
        $(TARGET_DIR)/usr/pcsx2/bin/resources/
endef

PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_CROSSHAIRS

$(eval $(cmake-package))
