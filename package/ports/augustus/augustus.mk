################################################################################
#
# Augustus (Caesar III engine)
#
################################################################################
# Version : Commits on Apr 2, 2025
AUGUSTUS_VERSION = 958869e70e02b064dfc051371c1067dca74a7a93
AUGUSTUS_SITE = https://github.com/Keriew/augustus.git
AUGUSTUS_SITE_METHOD = git
AUGUSTUS_GIT_SUBMODULES = YES
AUGUSTUS_LICENSE = GPL-3.0
AUGUSTUS_LICENSE_FILE = LICENSE

AUGUSTUS_DEPENDENCIES += sdl2 sdl2_mixer libpng

AUGUSTUS_SUPPORTS_IN_SOURCE_BUILD = NO

AUGUSTUS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
AUGUSTUS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

$(eval $(cmake-package))
