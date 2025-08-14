################################################################################
#
# taradino
#
################################################################################
# Version: Commits on Aug 12, 2025
TARADINO_VERSION = f4fddab06e4cc8521512abe4eb0004a294886c97
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
    cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/taradino/rott.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

TARADINO_POST_INSTALL_TARGET_HOOKS += TARADINO_EVMAPY

$(eval $(cmake-package))
