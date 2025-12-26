################################################################################
#
# vcmi
#
################################################################################

VCMI_VERSION = 1.7.0
VCMI_SITE = https://github.com/vcmi/vcmi.git
VCMI_SITE_METHOD=git
VCMI_GIT_SUBMODULES=YES
VCMI_DEPENDENCIES =  sdl2 sdl2_image sdl2_mixer sdl2_ttf libsquish
VCMI_DEPENDENCIES += minizip-zlib ffmpeg tbb boost zstd
VCMI_SUPPORTS_IN_SOURCE_BUILD = NO

VCMI_CMAKE_BACKEND = ninja

VCMI_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
VCMI_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
VCMI_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
VCMI_CONF_OPTS += -DENABLE_TEST=OFF
VCMI_CONF_OPTS += -DENABLE_DEBUG_CONSOLE=OFF
VCMI_CONF_OPTS += -DENABLE_EDITOR=OFF
VCMI_CONF_OPTS += -DENABLE_GITVERSION=OFF
VCMI_CONF_OPTS += -DENABLE_GOLDMASTER=ON
VCMI_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/vcmi/"
VCMI_CONF_OPTS += -DENABLE_MONOLITHIC_INSTALL=ON

# TODO fix onnxruntime to enable MMAI as it depends on it
VCMI_CONF_OPTS += -DENABLE_MMAI=OFF

ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
VCMI_DEPENDENCIES += libexecinfo
endif

# Settings from CMakePresets.json for portmaster, might be interesting
# "VCMI_PORTMASTER": "ON" <= custom directories, let's follow XDG
# "CMAKE_INSTALL_PREFIX": ".",
# "FORCE_BUNDLED_FL": "ON",

# Launcher requires Qt6 and translations are only for launcher/editor
ifeq ($(BR2_PACKAGE_REGLINUX_HAS_QT6),y)
VCMI_DEPENDENCIES += reglinux-qt6
VCMI_CONF_OPTS += -DENABLE_LAUNCHER=ON
VCMI_CONF_OPTS += -DENABLE_TRANSLATIONS=ON
VCMI_CONF_OPTS += -DQT_VERSION_MAJOR=6
else
VCMI_CONF_OPTS += -DENABLE_LAUNCHER=OFF
VCMI_CONF_OPTS += -DENABLE_SERVER=OFF
VCMI_CONF_OPTS += -DENABLE_TRANSLATIONS=OFF
endif

$(eval $(cmake-package))
