################################################################################
#
# libretro-scummvm
#
################################################################################
# Version: 2026.1.0
LIBRETRO_SCUMMVM_VERSION = v2026.1.0
LIBRETRO_SCUMMVM_SITE = $(call github,scummvm,scummvm,$(LIBRETRO_SCUMMVM_VERSION))
LIBRETRO_SCUMMVM_LICENSE = GPLv2

LIBRETRO_SCUMMVM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2835),y)
LIBRETRO_SCUMMVM_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2836),y)
LIBRETRO_SCUMMVM_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2837),y)
LIBRETRO_SCUMMVM_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2711),y)
LIBRETRO_SCUMMVM_PLATFORM = rpi4_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2712),y)
LIBRETRO_SCUMMVM_PLATFORM = rpi5_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S812),y)
LIBRETRO_SCUMMVM_PLATFORM = armv cortexa9 neon hardfloat
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_XU4),y)
LIBRETRO_SCUMMVM_PLATFORM = armv neon hardfloat
LIBRETRO_SCUMMVM_MAKE_OPTS += FORCE_OPENGLES2=1
else
LIBRETRO_SCUMMVM_PLATFORM = unix
ifeq ($(BR2_ARCH_IS_64),y)
LIBRETRO_SCUMMVM_MAKE_OPTS += TARGET_64BIT=1
endif
# TODO GL does not work for some reason, force GLES2
#ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
#LIBRETRO_SCUMMVM_MAKE_OPTS += FORCE_OPENGL=1
#else
LIBRETRO_SCUMMVM_MAKE_OPTS += FORCE_OPENGLES2=1
#endif
endif

define LIBRETRO_CLONE_AND_INIT
	mkdir -p $(@D)/backends/platform/libretro/deps/$(1)
	$(BR2_GIT) -C $(@D)/backends/platform/libretro/deps/$(1) init
	$(BR2_GIT) -C $(@D)/backends/platform/libretro/deps/$(1) remote add origin https://github.com/libretro/$(1)
	$(BR2_GIT) -C $(@D)/backends/platform/libretro/deps/$(1) fetch --depth 1 origin $(2)
	$(BR2_GIT) -C $(@D)/backends/platform/libretro/deps/$(1) checkout FETCH_HEAD
	$(BR2_GIT) -C $(@D)/backends/platform/libretro/deps/$(1) submodule update --init --recursive --depth 1
endef

# Details from backends/platform/libretro/dependencies.mk
define LIBRETRO_SCUMMVM_DEPS
	$(call LIBRETRO_CLONE_AND_INIT,libretro-deps,abf5246b016569759e7d1b0ea91bb98c2e34d160)
	$(call LIBRETRO_CLONE_AND_INIT,libretro-common,70ed90c42ddea828f53dd1b984c6443ddb39dbd6)
endef

define LIBRETRO_SCUMMVM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/backends/platform/libretro \
        platform="$(LIBRETRO_SCUMMVM_PLATFORM)" $(LIBRETRO_SCUMMVM_MAKE_OPTS)
endef

define LIBRETRO_SCUMMVM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/backends/platform/libretro/scummvm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/scummvm_libretro.so
endef

# workaround script issue
LIBRETRO_SCUMMVM_PRE_CONFIGURE_HOOKS += LIBRETRO_SCUMMVM_DEPS

$(eval $(generic-package))
