################################################################################
#
# libretro-melonds-ds
#
################################################################################

LIBRETRO_MELONDS_DS_VERSION = v1.1.8
LIBRETRO_MELONDS_DS_SITE = $(call github,JesseTG,melonds-ds,$(LIBRETRO_MELONDS_DS_VERSION))
LIBRETRO_MELONDS_DS_LICENSE = GPLv2
LIBRETRO_MELONDS_DS_DEPENDENCIES = libpcap

LIBRETRO_MELONDS_DS_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_MELONDS_DS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_MELONDS_DS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
LIBRETRO_MELONDS_DS_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
LIBRETRO_MELONDS_DS_DEPENDENCIES += libgles
endif

define LIBRETRO_MELONDS_DS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/src/libretro/melondsds_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/melondsds_libretro.so
	mkdir -p $(TARGET_DIR)/usr/share/libretro/info
	cp $(@D)/buildroot-build/melondsds_libretro.info \
	    $(TARGET_DIR)/usr/share/libretro/info/melondsds_libretro.info
endef

$(eval $(cmake-package))
