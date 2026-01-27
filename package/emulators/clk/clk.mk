################################################################################
#
# CLK - Clock Signal emulator
#
################################################################################
CLK_VERSION = 2026-01-06
CLK_SITE = https://github.com/TomHarte/CLK
CLK_SITE_METHOD=git
CLK_LICENSE = GPLv3
CLK_DEPENDENCIES = sdl2 zlib

# OpenGL
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
CLK_DEPENDENCIES += libgl
endif

# OpenGL ES
ifeq ($(BR2_PACKAGE_HAS_GLES3),y)
CLK_DEPENDENCIES += libgles
endif

CLK_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

define CLK_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/clksignal $(TARGET_DIR)/usr/bin/clksignal
endef
$(eval $(cmake-package))
