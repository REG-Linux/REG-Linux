################################################################################
#
# libretro-melonds-ds
#
################################################################################

# Using specific commit - stable releases have issues
LIBRETRO_MELONDS_DS_SITE = https://github.com/JesseTG/melonds-ds.git
LIBRETRO_MELONDS_DS_VERSION = e1391cc10a53b205963b7d1bd2b1f8d87d0d2cc7
LIBRETRO_MELONDS_DS_SITE_METHOD = git
LIBRETRO_MELONDS_DS_LICENSE = GPLv2
LIBRETRO_MELONDS_DS_DEPENDENCIES = libpcap

LIBRETRO_MELONDS_DS_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_MELONDS_DS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_MELONDS_DS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
#LIBRETRO_MELONDS_DS_CONF_OPTS += -DBUILD_QT_SDL=OFF

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
