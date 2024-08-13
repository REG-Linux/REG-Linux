################################################################################
#
# vcmi
#
################################################################################

VCMI_VERSION = 1.5.6
VCMI_SITE = https://github.com/vcmi/vcmi.git
VCMI_SITE_METHOD=git
VCMI_GIT_SUBMODULES=YES
VCMI_DEPENDENCIES = minizip sdl2 sdl2_image sdl2_mixer sdl2_ttf ffmpeg tbb boost
VCMI_SUPPORTS_IN_SOURCE_BUILD = NO

VCMI_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
VCMI_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
VCMI_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
VCMI_CONF_OPTS += -DENABLE_TEST=OFF
VCMI_CONF_OPTS += -DENABLE_EDITOR=OFF
VCMI_CONF_OPTS += -DENABLE_MONOLITHIC_INSTALL=ON
VCMI_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/vcmi/"

# Launcher requires Qt6
ifeq ($(BR2_PACKAGE_REGLINUX_HAS_QT6),y)
VCMI_DEPENDENCIES += reglinux-qt6
VCMI_CONF_OPTS += -DENABLE_LAUNCHER=ON
VCMI_CONF_OPTS += -DQT_VERSION_MAJOR=6
else
VCMI_CONF_OPTS += -DENABLE_LAUNCHER=OFF
endif

$(eval $(cmake-package))
