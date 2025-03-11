################################################################################
#
# SugarBoxV2
#
################################################################################
# Version: Release on Nov 29, 2024
SUGARBOX_VERSION = v2.0.4
SUGARBOX_SITE = https://github.com/Tom1975/SugarboxV2.git
SUGARBOX_SITE_METHOD=git
SUGARBOX_GIT_SUBMODULES=YES
SUGARBOX_LICENSE = MIT
SUGARBOX_DEPENDENCIES = reglinux-qt6

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
SUGARBOX_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
SUGARBOX_DEPENDENCIES += libgles
endif

SUGARBOX_SUPPORTS_IN_SOURCE_BUILD = NO

SUGARBOX_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
SUGARBOX_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
SUGARBOX_CONF_OPTS += -DALSOFT_UPDATE_BUILD_VERSION=OFF
SUGARBOX_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/sugarbox/"

SUGARBOX_CONF_ENV += LDFLAGS=-lpthread

define SUGARBOX_QT6_FIX_CMAKE
    cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/sugarbox/CMakeLists.txt $(@D)/Sugarbox/CMakeLists.txt
endef

SUGARBOX_PRE_CONFIGURE_HOOKS += SUGARBOX_QT6_FIX_CMAKE

$(eval $(cmake-package))
