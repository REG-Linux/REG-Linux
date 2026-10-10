################################################################################
#
# hatari
#
################################################################################

HATARI_VERSION = v2.6.1
HATARI_SOURCE = hatari-$(HATARI_VERSION).tar.gz
HATARI_SITE = https://github.com/hatari/hatari.git
HATARI_SITE_METHOD = git
HATARI_LICENSE = GPL-3.0+
HATARI_LICENSE_FILES = COPYING
HATARI_DEPENDENCIES = sdl2 zlib libpng libcapsimage

HATARI_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HATARI_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
HATARI_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
HATARI_CONF_OPTS += -DCAPSIMAGE_INCLUDE_DIR="$(STAGING_DIR)/usr/include"
HATARI_CONF_OPTS += -DENABLE_MAN_PAGES=OFF
HATARI_CONF_OPTS += -DENABLE_OSX_BUNDLE=OFF

# ARM NEON optimizations for ARM architectures
ifeq ($(BR2_arm),y)
ifeq ($(BR2_ARM_FPU_NEON),y)
HATARI_CONF_OPTS += -DCMAKE_C_FLAGS="$(TARGET_CFLAGS) -mfpu=neon -mfloat-abi=hard"
endif
endif
ifeq ($(BR2_aarch64),y)
HATARI_CONF_OPTS += -DCMAKE_C_FLAGS="$(TARGET_CFLAGS) -march=armv8-a+simd"
endif

# Installation: main emulator only (space saving)
define HATARI_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/src/hatari $(TARGET_DIR)/usr/bin/hatari
endef

$(eval $(cmake-package))
