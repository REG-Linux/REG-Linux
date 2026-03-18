################################################################################
#
# fallout2-ce
#
################################################################################

FALLOUT2_CE_VERSION = v1.3.0
FALLOUT2_CE_SITE = $(call github,alexbatalov,fallout2-ce,$(FALLOUT2_CE_VERSION))
FALLOUT2_CE_DEPENDENCIES = sdl2

FALLOUT2_CE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
FALLOUT2_CE_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
FALLOUT2_CE_CONF_OPTS += -DBUILD_STATIC_LIBS=ON

define FALLOUT2_CE_INSTALL_TARGET_CMDS
        cp $(@D)/fallout2-ce $(TARGET_DIR)/usr/bin/fallout2-ce
endef

$(eval $(cmake-package))
