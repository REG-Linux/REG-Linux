################################################################################
#
# Augustus (Caesar III engine)
#
################################################################################
# Version : Commits on Apr 15, 2025
AUGUSTUS_VERSION = 3cb10d6132a1b24694ede6268c615409181dd88e
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
