################################################################################
#
# taradino
#
################################################################################
# Version: Stable 20251222 release
TARADINO_VERSION = 20251222
TARADINO_SITE = https://github.com/fabiangreffrath/taradino.git
TARADINO_SITE_METHOD=git
TARADINO_GIT_SUBMODULES=YES
TARADINO_LICENSE = GPLv2
TARADINO_LICENSE_FILE = README.md

TARADINO_DEPENDENCIES = sdl2 sdl2_mixer

TARADINO_SUPPORTS_IN_SOURCE_BUILD = NO

TARADINO_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
TARADINO_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

$(eval $(cmake-package))
