################################################################################
#
# panda3ds
#
################################################################################
# Version: Commits on Aug 28, 2024
PANDA3DS_VERSION = 4adc50039cc22de2ee730dc83074760d72a8f3ce
PANDA3DS_SITE = https://github.com/wheremyfoodat/Panda3DS.git
PANDA3DS_SITE_METHOD=git
PANDA3DS_GIT_SUBMODULES=YES
PANDA3DS_LICENSE = GPLv2
PANDA3DS_DEPENDENCIES = sdl2

PANDA3DS_SUPPORTS_IN_SOURCE_BUILD = NO

PANDA3DS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
PANDA3DS_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr"
PANDA3DS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
PANDA3DS_CONF_OPTS += -DENABLE_OPENGL=ON
PANDA3DS_CONF_OPTS += -DENABLE_VULKAN=OFF
PANDA3DS_CONF_OPTS += -DENABLE_LTO=ON
PANDA3DS_CONF_OPTS += -DENABLE_DISCORD_RPC=OFF
PANDA3DS_CONF_OPTS += -DENABLE_GIT_VERSIONING=OFF
PANDA3DS_CONF_OPTS += -DENABLE_RENDERDOC_API=OFF

# AArch64 build crashes in cryptopp due to AES intrinsics and PMULL instructions
# Disable for now
# No RISC-V support / cross-compiling AArch64 support in vendored LuaJIT
# Disable for no
ifeq ($(BR2_riscv)$(BR2_aarch64),y)
PANDA3DS_CONF_OPTS += -DCRYPTOPP_OPT_DISABLE_ASM=ON
PANDA3DS_CONF_OPTS += -DENABLE_LUAJIT=OFF
endif

#option(ENABLE_QT_GUI "Enable the Qt GUI. If not selected then the emulator uses a minimal SDL-based UI instead" OFF)
#option(BUILD_HYDRA_CORE "Build a Hydra core" OFF)
#option(BUILD_LIBRETRO_CORE "Build a Libretro core" OFF)

define PANDA3DS_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/Alber \
		$(TARGET_DIR)/usr/bin/panda3ds
endef

define PANDA3DS_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
#	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/emulators/panda3ds/3ds.panda3ds.keys \
#	    $(TARGET_DIR)/usr/share/evmapy
endef

PANDA3DS_POST_INSTALL_TARGET_HOOKS += PANDA3DS_POST_PROCESS

$(eval $(cmake-package))
