################################################################################
#
# libretro-fbneo
#
################################################################################
# Version: Commits on Nov 23, 2025
LIBRETRO_FBNEO_VERSION = ff295ebb49dbe5f2aa8b245c09b90db8b3d20669
LIBRETRO_FBNEO_SITE = $(call github,libretro,FBNeo,$(LIBRETRO_FBNEO_VERSION))
LIBRETRO_FBNEO_LICENSE = Non-commercial

LIBRETRO_FBNEO_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_FBNEO_EXTRA_ARGS =

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2835),y)
LIBRETRO_FBNEO_PLATFORM = unix-rpi1
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2836),y)
LIBRETRO_FBNEO_PLATFORM = unix-rpi2
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2837),y)
LIBRETRO_FBNEO_PLATFORM = unix-rpi3_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2711),y)
LIBRETRO_FBNEO_PLATFORM = unix-rpi4_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2712),y)
LIBRETRO_FBNEO_PLATFORM = unix-rpi5_64
else ifeq ($(BR2_cortex_a7),y)
LIBRETRO_FBNEO_PLATFORM = classic_armv7_a7
endif

ifeq ($(BR2_arm),y)
LIBRETRO_FBNEO_EXTRA_ARGS += USE_CYCLONE=1
endif

ifeq ($(BR2_ARM_FPU_NEON_VFPV4)$(BR2_ARM_FPU_NEON)$(BR2_ARM_FPU_NEON_FP_ARMV8),y)
LIBRETRO_FBNEO_EXTRA_ARGS += HAVE_NEON=1
else
LIBRETRO_FBNEO_EXTRA_ARGS += HAVE_NEON=0
endif

ifeq ($(BR2_x86_64),y)
LIBRETRO_FBNEO_EXTRA_ARGS += USE_X64_DRC=1 profile=accuracy
else
LIBRETRO_FBNEO_EXTRA_ARGS += profile=performance
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3326),y)
LIBRETRO_FBNEO_EXTRA_ARGS += USE_EXPERIMENTAL_FLAGS=0
endif

define LIBRETRO_FBNEO_BUILD_CMDS
	# Let's clean-up a bit unused stuff in FBNeo (non-arcade, non-MD)
	rm $(@D)/src/burn/drv/coleco/d_coleco.cpp
	rm $(@D)/src/burn/drv/msx/d_msx.cpp
	rm $(@D)/src/burn/drv/nes/d_nes.cpp
	rm $(@D)/src/burn/drv/pce/d_pce.cpp
	rm $(@D)/src/burn/drv/pst90s/d_ngp.cpp
	rm $(@D)/src/burn/drv/sg1000/d_sg1000.cpp
	rm -Rf $(@D)/src/burn/drv/spectrum/*
	rm -Rf $(@D)/src/burn/drv/sms/*
	rm $(@D)/src/burn/drv/snes/d_snes.cpp
	# Regenerate proper driver list and gamelist.txt
	cd $(@D) && ./src/dep/scripts/gamelist.pl -o src/dep/generated/driverlist.h -l gamelist.txt src/burn/drv/*/
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/src/burner/libretro -f Makefile \
		platform="$(LIBRETRO_FBNEO_PLATFORM)" $(LIBRETRO_FBNEO_EXTRA_ARGS) \
        GIT_VERSION="$(shell echo $(LIBRETRO_FBNEO_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_FBNEO_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/burner/libretro/fbneo_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fbneo_libretro.so

	# Bios
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/bios/fbneo/samples
	cp -r $(@D)/metadata/* \
		$(TARGET_DIR)/usr/share/reglinux/datainit/bios/fbneo

    # Copy only relevant DAT files
	rsync -a $(@D)/dats/*Arcade* \
		$(TARGET_DIR)/usr/share/reglinux/datainit/bios/fbneo --exclude light
	rsync -a $(@D)/dats/*Megadrive* \
		$(TARGET_DIR)/usr/share/reglinux/datainit/bios/fbneo --exclude light
endef

$(eval $(generic-package))
