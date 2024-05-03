################################################################################
#
# Goofy
#
################################################################################
GOOFY_VERSION = 891f425a037ba1ad347cb7cf8bc78d1780642c03
GOOFY_SITE = https://github.com/rtissera/Goofy.git
GOOFY_SITE_METHOD=git
GOOFY_GIT_SUBMODULES=YES
GOOFY_LICENSE = GPLv2
GOOFY_DEPENDENCIES =

GOOFY_SUPPORTS_IN_SOURCE_BUILD = NO

GOOFY_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
GOOFY_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

GOOFY_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
