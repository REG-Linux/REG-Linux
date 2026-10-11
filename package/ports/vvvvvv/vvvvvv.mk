################################################################################
#
# vvvvvv — VVVVVV puzzle platformer engine
#
################################################################################

VVVVVV_VERSION = 2.4.4
VVVVVV_SITE = https://github.com/TerryCavanagh/VVVVVV
VVVVVV_SITE_METHOD = git
VVVVVV_GIT_SUBMODULES = YES
VVVVVV_LICENSE = VVVVVV Source Code License v1.0
VVVVVV_LICENSE_FILES = LICENSE.md

VVVVVV_DEPENDENCIES = sdl2
VVVVVV_SUBDIR = desktop_version

VVVVVV_CONF_OPTS = \
	-DBUNDLE_DEPENDENCIES=ON \
	-DCMAKE_BUILD_TYPE=Release

define VVVVVV_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/desktop_version/VVVVVV \
		$(TARGET_DIR)/usr/bin/vvvvvv
endef

$(eval $(cmake-package))
