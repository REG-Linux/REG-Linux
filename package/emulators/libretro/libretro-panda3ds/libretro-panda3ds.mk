################################################################################
#
# libretro-panda3ds
#
################################################################################
# Version: Release on Dec 25, 2024 + REG fix
LIBRETRO_PANDA3DS_VERSION = v0.9-fix
LIBRETRO_PANDA3DS_SITE = https://github.com/REG-Linux/Panda3DS.git
#REG forked https://github.com/wheremyfoodat/Panda3DS.git
LIBRETRO_PANDA3DS_SITE_METHOD=git
LIBRETRO_PANDA3DS_GIT_SUBMODULES=YES
LIBRETRO_PANDA3DS_LICENSE = GPLv2
LIBRETRO_PANDA3DS_DEPENDENCIES = sdl2

LIBRETRO_PANDA3DS_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_PANDA3DS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_PANDA3DS_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr"
LIBRETRO_PANDA3DS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
LIBRETRO_PANDA3DS_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
LIBRETRO_PANDA3DS_CONF_OPTS += -DENABLE_OPENGL=ON
LIBRETRO_PANDA3DS_CONF_OPTS += -DENABLE_LTO=ON
LIBRETRO_PANDA3DS_CONF_OPTS += -DENABLE_DISCORD_RPC=OFF
LIBRETRO_PANDA3DS_CONF_OPTS += -DENABLE_GIT_VERSIONING=OFF
LIBRETRO_PANDA3DS_CONF_OPTS += -DENABLE_RENDERDOC_API=OFF
LIBRETRO_PANDA3DS_CONF_OPTS += -DUSE_SYSTEM_SDL2=ON
LIBRETRO_PANDA3DS_CONF_OPTS += -DBUILD_LIBRETRO_CORE=ON
LIBRETRO_PANDA3DS_CONF_OPTS += -DSDL_VIDEO=OFF
LIBRETRO_PANDA3DS_CONF_OPTS += -DSDL_AUDIO=OFF

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
LIBRETRO_PANDA3DS_CONF_OPTS += -DOPENGL_PROFILE=OpenGL
LIBRETRO_PANDA3DS_DEPENDENCIES += libgl
else
LIBRETRO_PANDA3DS_CONF_OPTS += -DOPENGL_PROFILE=OpenGLES
LIBRETRO_PANDA3DS_DEPENDENCIES += libgles
endif

# AArch64 build crashes in cryptopp due to AES intrinsics and PMULL instructions
# Disable for now
# No RISC-V support / cross-compiling AArch64 support in vendored LuaJIT
# Disable for now
ifeq ($(BR2_riscv)$(BR2_aarch64),y)
LIBRETRO_PANDA3DS_CONF_OPTS += -DCRYPTOPP_OPT_DISABLE_ASM=ON
LIBRETRO_PANDA3DS_CONF_OPTS += -DENABLE_LUAJIT=OFF
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    LIBRETRO_PANDA3DS_CONF_OPTS += -DENABLE_VULKAN=ON
    LIBRETRO_PANDA3DS_DEPENDENCIES += host-glslang glslang vulkan-headers
else
    LIBRETRO_PANDA3DS_CONF_OPTS += -DENABLE_VULKAN=OFF
endif

define LIBRETRO_PANDA3DS_INSTALL_TARGET_CMDS
    # Strip
    $(TARGET_STRIP) $(@D)/buildroot-build/panda3ds_libretro.so
    # Install
    mkdir -p $(TARGET_DIR)/usr/lib/libretro
    $(INSTALL) -D $(@D)/buildroot-build/panda3ds_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/
    mkdir -p $(TARGET_DIR)/usr/share/libretro/info
    $(INSTALL) -D $(@D)/docs/libretro/panda3ds_libretro.info \
		$(TARGET_DIR)/usr/share/libretro/info/
endef

$(eval $(cmake-package))
