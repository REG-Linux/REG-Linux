################################################################################
#
# spacecadetpinball — Reverse-engineered Windows Space Cadet Pinball
#
################################################################################

SPACECADETPINBALL_VERSION = Release_2.1.0
SPACECADETPINBALL_SITE = https://github.com/k4zmu2a/SpaceCadetPinball
SPACECADETPINBALL_SITE_METHOD = git
SPACECADETPINBALL_LICENSE = MIT
SPACECADETPINBALL_LICENSE_FILES = LICENSE

SPACECADETPINBALL_DEPENDENCIES = sdl2 sdl2_mixer

SPACECADETPINBALL_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release

define SPACECADETPINBALL_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bin/SpaceCadetPinball \
		$(TARGET_DIR)/usr/bin/spacecadetpinball
endef

$(eval $(cmake-package))
