################################################################################
#
# GS+
#
################################################################################
GSPLUS_VERSION = v1.38.0
GSPLUS_SITE = $(call github,digarok,gsplus,$(GSPLUS_VERSION))
GSPLUS_LICENSE = GPLv2
GSPLUS_DEPENDENCIES = sdl3 libpcap host-re2c readline freetype
#sdl2_image

GSPLUS_SUBDIR = gsplus/src

define GSPLUS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gsplus/src/gsplus $(TARGET_DIR)/usr/bin/
endef

$(eval $(cmake-package))
