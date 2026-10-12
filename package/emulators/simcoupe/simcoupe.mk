################################################################################
#
# simcoupe
#
################################################################################
SIMCOUPE_VERSION = v1.2.17
SIMCOUPE_SITE = $(call github,simonowen,simcoupe,$(SIMCOUPE_VERSION))
SIMCOUPE_LICENSE = GPL-3.0

SIMCOUPE_SUPPORTS_IN_SOURCE_BUILD = YES

SIMCOUPE_DEPENDENCIES = sdl2

SIMCOUPE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SIMCOUPE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
# GCC 16 defaults to C++20, where fmt checks format strings at compile
# time and rejects the runtime ones simcoupe passes
SIMCOUPE_CONF_OPTS += -DCMAKE_CXX_STANDARD=17

SIMCOUPE_BIOS_AND_RESOURCES = /usr/share/simcoupe

define SIMCOUPE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/simcoupe $(TARGET_DIR)/usr/bin/simcoupe
	cp -d $(@D)/_deps/saasound-build/libSAASound* $(TARGET_DIR)/usr/lib/
	mkdir -p $(TARGET_DIR)$(SIMCOUPE_BIOS_AND_RESOURCES)
	cp -R $(@D)/Resource/* $(TARGET_DIR)$(SIMCOUPE_BIOS_AND_RESOURCES)
endef

$(eval $(cmake-package))
