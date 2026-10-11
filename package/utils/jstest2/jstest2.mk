################################################################################
#
# jstest2
#
################################################################################

JSTEST2_VERSION = c3bb98945be0c6cb4ef54e9bbc1647a2b1bb4a6c
JSTEST2_SITE = https://github.com/Grumbel/sdl-jstest
JSTEST2_SITE_METHOD = git
JSTEST2_GIT_SUBMODULES = YES
JSTEST2_DEPENDENCIES = sdl2 ncurses

JSTEST2_CONF_ENV = LIBS="-ncurses -ltinfo"

$(eval $(cmake-package))
