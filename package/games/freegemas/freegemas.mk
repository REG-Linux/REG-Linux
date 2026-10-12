################################################################################
#
# freegemas — Open-source Bejeweled clone
#
################################################################################

FREEGEMAS_VERSION = 22.02
FREEGEMAS_SITE = https://github.com/JoseTomasTocino/freegemas
FREEGEMAS_SITE_METHOD = git
FREEGEMAS_LICENSE = GPL-2.0
FREEGEMAS_LICENSE_FILES = LICENSE

FREEGEMAS_DEPENDENCIES = sdl2 sdl2_image sdl2_mixer sdl2_ttf jsoncpp

FREEGEMAS_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release

define FREEGEMAS_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/freegemas $(TARGET_DIR)/usr/bin/freegemas
	cp -r $(@D)/media $(TARGET_DIR)/usr/share/freegemas
endef

$(eval $(cmake-package))
