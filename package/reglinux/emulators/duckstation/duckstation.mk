################################################################################
#
# duckstation
#
################################################################################

DUCKSTATION_VERSION = e499f9052af95f17ecd38e0422b49fee1d9c8222
DUCKSTATION_SITE = https://github.com/stenzek/duckstation.git
DUCKSTATION_SITE_METHOD=git
DUCKSTATION_GIT_SUBMODULES=YES
DUCKSTATION_LICENSE = GPLv2
DUCKSTATION_SUPPORTS_IN_SOURCE_BUILD = NO

DUCKSTATION_DEPENDENCIES = fmt boost ffmpeg libcurl ecm shaderc webp
DUCKSTATION_DEPENDENCIES += qt6base qt6tools qt6svg libbacktrace
DUCKSTATION_DEPENDENCIES += cpuinfo spirv-cross libsoundtouch

DUCKSTATION_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
DUCKSTATION_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
DUCKSTATION_CONF_OPTS += -DENABLE_DISCORD_PRESENCE=OFF
DUCKSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=ON

DUCKSTATION_CONF_ENV += LDFLAGS=-lpthread

DUCKSTATION_CONF_OPTS += -DENABLE_WAYLAND=ON
DUCKSTATION_DEPENDENCIES += wayland qt6wayland

ifeq ($(BR2_PACKAGE_XORG7),y)
    DUCKSTATION_CONF_OPTS += -DENABLE_X11=ON
else
    DUCKSTATION_CONF_OPTS += -DENABLE_X11=OFF
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    DUCKSTATION_DEPENDENCIES += glslang
    DUCKSTATION_CONF_OPTS += -DENABLE_VULKAN=ON
else
    DUCKSTATION_CONF_OPTS += -DENABLE_VULKAN=OFF
endif

define DUCKSTATION_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    mkdir -p $(TARGET_DIR)/usr/lib
    mkdir -p $(TARGET_DIR)/usr/share/duckstation

    $(INSTALL) -D $(@D)/buildroot-build/bin/duckstation* \
        $(TARGET_DIR)/usr/bin/
    cp -R $(@D)/buildroot-build/bin/resources \
        $(TARGET_DIR)/usr/share/duckstation/
    rm -f $(TARGET_DIR)/usr/share/duckstation/resources/gamecontrollerdb.txt

    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/emulators/duckstation/psx.duckstation.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

define DUCKSTATION_PREPARE_TRANSLATIONS
    mkdir -p $(@D)/buildroot-build/bin/resources
endef

define DUCKSTATION_TRANSLATIONS
    mkdir -p $(TARGET_DIR)/usr/share/duckstation
    cp -R $(@D)/buildroot-build/bin/translations \
        $(TARGET_DIR)/usr/share/duckstation/
endef

DUCKSTATION_POST_CONFIGURE_HOOKS += DUCKSTATION_PREPARE_TRANSLATIONS
DUCKSTATION_POST_INSTALL_TARGET_HOOKS += DUCKSTATION_TRANSLATIONS

$(eval $(cmake-package))
