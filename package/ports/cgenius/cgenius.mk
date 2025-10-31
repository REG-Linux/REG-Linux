################################################################################
#
# cgenius
#
################################################################################

CGENIUS_VERSION = v3.6.1
CGENIUS_SITE = $(call github,gerstrong,Commander-Genius,$(CGENIUS_VERSION))
CGENIUS_CONF_LICENSE = GPL-2.0
CGENIUS_CONF_LICENSE_FILES = LICENSE
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

define CGENIUS_GET_COSMOS
    cd $(@D); \
        git clone https://gitlab.com/Dringgstein/cosmos.git src/engine/cosmos; \
        cd src/engine/cosmos; \
        git checkout d25d1923656341bda6a40a76769eb699a67816d5; \
        cd ../../..
endef

define CGENIUS_POST_PROCESS
        mkdir -p $(TARGET_DIR)/usr/share/evmapy
        cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/cgenius/cgenius.cgenius.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

CGENIUS_POST_EXTRACT_HOOKS += CGENIUS_GET_COSMOS
CGENIUS_POST_INSTALL_TARGET_HOOKS += CGENIUS_POST_PROCESS

$(eval $(cmake-package))
