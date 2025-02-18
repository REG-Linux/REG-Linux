################################################################################
#
# taradino
#
################################################################################
# Version: Commits on Feb 11, 2025
TARADINO_VERSION = 3d081a26e39b8456820951f44b8a93b90d7e970a
TARADINO_SITE = https://github.com/fabiangreffrath/taradino.git
TARADINO_SITE_METHOD=git
TARADINO_GIT_SUBMODULES=YES
TARADINO_LICENSE = GPLv2
TARADINO_LICENSE_FILE = README.md

TARADINO_DEPENDENCIES = sdl2 sdl2_mixer

TARADINO_SUPPORTS_IN_SOURCE_BUILD = NO

TARADINO_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
TARADINO_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

define TARADINO_EVMAPY
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/reglinux/ports/taradino/rott.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

TARADINO_POST_INSTALL_TARGET_HOOKS += TARADINO_EVMAPY

$(eval $(cmake-package))
