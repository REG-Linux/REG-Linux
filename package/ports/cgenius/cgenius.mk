################################################################################
#
# cgenius
#
################################################################################

CGENIUS_VERSION = v3.6.4
CGENIUS_SITE = https://github.com/gerstrong/Commander-Genius.git
CGENIUS_SITE_METHOD = git
# The Cosmos engine is a submodule (src/engine/cosmos, Dringgstein/cosmos
# "testing" branch), fetched at the commit this release pins
CGENIUS_GIT_SUBMODULES = YES
CGENIUS_LICENSE = GPL-2.0
CGENIUS_LICENSE_FILES = LICENSE
CGENIUS_DEPENDENCIES += sdl2 sdl2_mixer sdl2_image sdl2_ttf
CGENIUS_DEPENDENCIES += boost libcurl host-xxd python3-configobj

ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
CGENIUS_DEPENDENCIES += libbacktrace libexecinfo
endif

ifeq ($(BR2_CCACHE),y)
CGENIUS_CONF_OPTS += -DUSE_CCACHE=ON
# No dependencies needed, it's into toolchain
else
CGENIUS_CONF_OPTS += -DUSE_CCACHE=OFF
endif

CGENIUS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CGENIUS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

# compile the cosmos engine too
CGENIUS_CONF_OPTS += -DBUILD_COSMOS=1

$(eval $(cmake-package))
