################################################################################
#
# DHEWM3
#
################################################################################

DHEWM3_VERSION = 1.5.3
DHEWM3_SITE = https://github.com/dhewm/dhewm3
DHEWM3_SITE_METHOD=git
DHEWM3_DEPENDENCIES = zlib openal sdl2
DHEWM3_SUPPORTS_IN_SOURCE_BUILD = NO

DHEWM3_SUBDIR = neo

DHEWM3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
DHEWM3_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
DHEWM3_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
DHEWM3_CONF_OPTS += -DENABLE_TEST=OFF

$(eval $(cmake-package))
