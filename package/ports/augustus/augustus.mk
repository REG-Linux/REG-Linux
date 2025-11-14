################################################################################
#
# Augustus (Caesar III engine)
#
################################################################################
# Version : Commits on Nov 13, 2025
AUGUSTUS_VERSION = 1bacfa923504294d81e2258b9e7b1da8e38cfd0c
AUGUSTUS_SITE = https://github.com/Keriew/augustus.git
AUGUSTUS_SITE_METHOD = git
AUGUSTUS_GIT_SUBMODULES = YES
AUGUSTUS_LICENSE = GPL-3.0
AUGUSTUS_LICENSE_FILE = LICENSE

AUGUSTUS_DEPENDENCIES += sdl2 sdl2_mixer libpng

ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
AUGUSTUS_DEPENDENCIES += libbacktrace libexecinfo
endif

AUGUSTUS_SUPPORTS_IN_SOURCE_BUILD = NO

AUGUSTUS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
AUGUSTUS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

$(eval $(cmake-package))
