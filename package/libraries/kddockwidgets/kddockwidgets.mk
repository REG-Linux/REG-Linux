################################################################################
#
# KDDockWigets
#
################################################################################

KDDOCKWIDGETS_VERSION = v2.4.0
KDDOCKWIDGETS_SITE = $(call github,KDAB,KDDockWidgets,$(KDDOCKWIDGETS_VERSION))
KDDOCKWIDGETS_DEPENDENCIES = reglinux-qt6 spdlog fmt json-for-modern-cpp
KDDOCKWIDGETS_SUPPORTS_IN_SOURCE_BUILD = NO
KDDOCKWIDGETS_INSTALL_STAGING = YES

KDDOCKWIDGETS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
KDDOCKWIDGETS_CONF_OPTS += -DKDDockWidgets_QT6=true

$(eval $(cmake-package))
