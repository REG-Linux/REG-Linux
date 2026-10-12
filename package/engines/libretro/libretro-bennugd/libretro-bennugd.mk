################################################################################
#
# libretro-bennugd — BennuGD libretro core (runs SorR and other .dcb games)
#
################################################################################
# Version: Commits on Aug 14, 2026
LIBRETRO_BENNUGD_VERSION = 5fba764ac709545d4b0d3b28deff2ec0c7d1a91b
LIBRETRO_BENNUGD_SITE = https://github.com/diekleinekuh/BennuGD_libretro
LIBRETRO_BENNUGD_SITE_METHOD = git
LIBRETRO_BENNUGD_GIT_SUBMODULES = YES
LIBRETRO_BENNUGD_LICENSE = GPL-2.0
LIBRETRO_BENNUGD_SUPPORTS_IN_SOURCE_BUILD = NO

# Pre-download libretro-common so FetchContent doesn't need git at configure time
LIBRETRO_BENNUGD_LIBRETRO_COMMON_VERSION = 55ca668901e72eb885976c8c839e6903ecbb119d
LIBRETRO_BENNUGD_EXTRA_DOWNLOADS = \
	https://github.com/libretro/libretro-common/archive/$(LIBRETRO_BENNUGD_LIBRETRO_COMMON_VERSION).tar.gz

# Use system libs to avoid FetchContent in-source build issues
LIBRETRO_BENNUGD_DEPENDENCIES = freetype zlib libpng sdl2 libmikmod libogg libvorbis

define LIBRETRO_BENNUGD_EXTRACT_LIBRETRO_COMMON
	mkdir -p $(@D)/libretro-common-src
	$(TAR) --strip-components=1 -xzf $(LIBRETRO_BENNUGD_DL_DIR)/$(LIBRETRO_BENNUGD_LIBRETRO_COMMON_VERSION).tar.gz \
		-C $(@D)/libretro-common-src
endef
LIBRETRO_BENNUGD_POST_EXTRACT_HOOKS += LIBRETRO_BENNUGD_EXTRACT_LIBRETRO_COMMON

LIBRETRO_BENNUGD_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-Dlibretro_core=ON \
	-DNO_SYSTEM_DEPENDENCIES=OFF \
	-DBUILD_SHARED_LIBS=OFF \
	-DGIT_FAIL_IF_NONZERO_EXIT=FALSE \
	-DFETCHCONTENT_SOURCE_DIR_LIBRETRO-COMMON=$(@D)/libretro-common-src

define LIBRETRO_BENNUGD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/bennugd_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bennugd_libretro.so
endef

$(eval $(cmake-package))
