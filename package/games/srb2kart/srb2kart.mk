################################################################################
#
# srb2kart — Sonic Robo Blast 2 Kart (kart racing spinoff)
#
################################################################################

SRB2KART_VERSION = v1.6
SRB2KART_SITE = https://github.com/STJr/Kart-Public
SRB2KART_SITE_METHOD = git
SRB2KART_LICENSE = GPL-2.0
SRB2KART_LICENSE_FILES = LICENSE
SRB2KART_SUPPORTS_IN_SOURCE_BUILD = NO

SRB2KART_DEPENDENCIES = sdl2 sdl2_mixer libpng zlib libcurl

define SRB2KART_FIX_INSOURCE_CHECK
	sed -i '/In-source builds will bring you a world of pain/d' $(@D)/CMakeLists.txt
	sed -i '/CMAKE_SOURCE_DIR.*STREQUAL.*CMAKE_BINARY_DIR/,+3d' $(@D)/CMakeLists.txt
endef
SRB2KART_POST_PATCH_HOOKS += SRB2KART_FIX_INSOURCE_CHECK

SRB2KART_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DSRB2_CONFIG_ENABLE_TESTS=OFF

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
SRB2KART_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
SRB2KART_DEPENDENCIES += libgles
endif

define SRB2KART_INSTALL_TARGET_CMDS
	find $(@D) -name "srb2kart" -type f -executable | head -1 | xargs -I{} $(INSTALL) -D -m 0755 {} $(TARGET_DIR)/usr/bin/srb2kart
endef

$(eval $(cmake-package))
