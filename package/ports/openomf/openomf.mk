################################################################################
#
# OpenOMF - One Must Fall 2097 open source engine
#
################################################################################

# Release on Sep 11, 2025
OPENOMF_VERSION = 0.8.5
OPENOMF_SITE = $(call github,omf2097,openomf,$(OPENOMF_VERSION))
OPENOMF_DEPENDENCIES = sdl2 sdl2_mixer enet libconfuse libminiupnpc libnatpmp libepoxy

OPENOMF_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
OPENOMF_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
OPENOMF_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
# TODO : localization / build languages does not cross-compile
OPENOMF_CONF_OPTS += -DBUILD_LANGUAGES=OFF

$(eval $(cmake-package))
