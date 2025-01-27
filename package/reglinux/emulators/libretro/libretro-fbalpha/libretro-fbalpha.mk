################################################################################
#
# libretro-fbalpha
#
################################################################################
# Version.: Commits on Oct 21, 2024
LIBRETRO_FBALPHA_VERSION = 77167cea72e808384c136c8c163a6b4975ce7a84
LIBRETRO_FBALPHA_SITE = $(call github,libretro,fbalpha2012,$(LIBRETRO_FBALPHA_VERSION))
LIBRETRO_FBALPHA_LICENSE = Non-commercial

LIBRETRO_FBALPHA_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_arm),y)
LIBRETRO_FBALPHA_PLATFORM = armv
endif

define LIBRETRO_FBALPHA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
        $(@D)/svn-current/trunk/ -f makefile.libretro platform="$(LIBRETRO_FBALPHA_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_FBALPHA_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_FBALPHA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/svn-current/trunk/fbalpha2012_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fbalpha_libretro.so
endef

$(eval $(generic-package))
