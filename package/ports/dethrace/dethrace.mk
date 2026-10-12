################################################################################
#
# dethrace — Carmageddon engine reimplementation
#
################################################################################

DETHRACE_VERSION = v0.10.1
DETHRACE_SITE = https://github.com/dethrace-labs/dethrace
DETHRACE_SITE_METHOD = git
DETHRACE_GIT_SUBMODULES = YES
DETHRACE_LICENSE = MIT
DETHRACE_LICENSE_FILES = LICENSE

DETHRACE_SUPPORTS_IN_SOURCE_BUILD = NO

DETHRACE_DEPENDENCIES = sdl2

DETHRACE_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DDETHRACE_PLATFORM_SDL2=ON \
	-DDETHRACE_INSTALL=ON \
	-DBUILD_TESTS=OFF \
	-DBUILD_SHARED_LIBS=OFF

$(eval $(cmake-package))
