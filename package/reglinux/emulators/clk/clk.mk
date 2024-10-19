################################################################################
#
# CLK - Clock Signal emulator
#
################################################################################
# Version.: Release 2024-10-19 on Oct 19, 2024
CLK_VERSION = 2024-10-19
CLK_SITE = https://github.com/TomHarte/CLK
CLK_SITE_METHOD=git
CLK_LICENSE = GPLv3
CLK_DEPENDENCIES = sdl2 libgl zlib

CLK_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

define CLK_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/clksignal $(TARGET_DIR)/usr/bin/clksignal
endef
$(eval $(cmake-package))
