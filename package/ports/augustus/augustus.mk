################################################################################
#
# Augustus (Caesar III engine)
#
################################################################################
# Version : Commits on Jul 25, 2025
AUGUSTUS_VERSION = 80be54b615892c9642b4903320482b745d851afb
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
