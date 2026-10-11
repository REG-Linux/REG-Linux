################################################################################
#
# libretro-same-cdi
#
################################################################################
# Version: Commits on Sep 1, 2026
LIBRETRO_SAME_CDI_VERSION = 9a589f6ba8c35f5310853f63420d9dab1df63492
LIBRETRO_SAME_CDI_SITE = $(call github,libretro,same_cdi,$(LIBRETRO_SAME_CDI_VERSION))
LIBRETRO_SAME_CDI_LICENSE = GPL

LIBRETRO_SAME_CDI_MAX_JOBS = 6
LIBRETRO_SAME_CDI_JOBS = $(shell if [ $(PARALLEL_JOBS) -gt $(LIBRETRO_SAME_CDI_MAX_JOBS) ]; then echo $(LIBRETRO_SAME_CDI_MAX_JOBS); else echo $(PARALLEL_JOBS); fi)

# Upstream dropped GENie/regenie: it's a plain arch-agnostic GNU make build
# (no CPU-specific flags, no bundled 3rdparty libs to select) with a single
# "unix" platform bucket covering all Linux targets.
define LIBRETRO_SAME_CDI_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -j$(LIBRETRO_SAME_CDI_JOBS) \
		CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" AR="$(TARGET_AR)" \
		platform="unix" -C $(@D) -f Makefile.libretro
endef

define LIBRETRO_SAME_CDI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/same_cdi_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/same_cdi_libretro.so
endef

$(eval $(generic-package))
