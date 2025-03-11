################################################################################
#
# panda3ds
#
################################################################################
# Version: Release on Dec 25, 2024
PANDA3DS_VERSION = v0.9
PANDA3DS_SITE = https://github.com/wheremyfoodat/Panda3DS.git
PANDA3DS_SITE_METHOD=git
PANDA3DS_GIT_SUBMODULES=YES
PANDA3DS_LICENSE = GPLv2
PANDA3DS_DEPENDENCIES = sdl2

PANDA3DS_SUPPORTS_IN_SOURCE_BUILD = NO

PANDA3DS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
PANDA3DS_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr"
PANDA3DS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
PANDA3DS_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
PANDA3DS_CONF_OPTS += -DENABLE_OPENGL=ON
PANDA3DS_CONF_OPTS += -DENABLE_LTO=ON
PANDA3DS_CONF_OPTS += -DENABLE_DISCORD_RPC=OFF
PANDA3DS_CONF_OPTS += -DENABLE_GIT_VERSIONING=OFF
PANDA3DS_CONF_OPTS += -DENABLE_RENDERDOC_API=OFF
PANDA3DS_CONF_OPTS += -DUSE_SYSTEM_SDL2=ON

# AArch64 build crashes in cryptopp due to AES intrinsics and PMULL instructions
# Disable for now
# No RISC-V support / cross-compiling AArch64 support in vendored LuaJIT
# Disable for now
ifeq ($(BR2_riscv)$(BR2_aarch64),y)
PANDA3DS_CONF_OPTS += -DCRYPTOPP_OPT_DISABLE_ASM=ON
PANDA3DS_CONF_OPTS += -DENABLE_LUAJIT=OFF
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    PANDA3DS_CONF_OPTS += -DENABLE_VULKAN=ON
    PANDA3DS_DEPENDENCIES += glslang vulkan-headers
else
    PANDA3DS_CONF_OPTS += -DENABLE_VULKAN=OFF
endif

#option(ENABLE_QT_GUI "Enable the Qt GUI. If not selected then the emulator uses a minimal SDL-based UI instead" OFF)

define PANDA3DS_INSTALL_TARGET_CMDS
    # Strip
    $(TARGET_STRIP) $(@D)/buildroot-build/Alber
    # Install
    $(INSTALL) -D $(@D)/buildroot-build/Alber \
		$(TARGET_DIR)/usr/bin/panda3ds
endef

define PANDA3DS_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
#	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/panda3ds/3ds.panda3ds.keys \
#	    $(TARGET_DIR)/usr/share/evmapy
endef

PANDA3DS_POST_INSTALL_TARGET_HOOKS += PANDA3DS_POST_PROCESS

$(eval $(cmake-package))
