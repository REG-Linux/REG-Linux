################################################################################
#
# duckstation (GPL version v0.1-7294)
#
################################################################################

DUCKSTATION_GPL_VERSION = v0.1-7294
DUCKSTATION_GPL_SITE = https://github.com/stenzek/duckstation.git
DUCKSTATION_GPL_SITE_METHOD=git
DUCKSTATION_GPL_GIT_SUBMODULES=YES
DUCKSTATION_GPL_LICENSE = GPLv2
DUCKSTATION_GPL_SUPPORTS_IN_SOURCE_BUILD = NO

DUCKSTATION_GPL_DEPENDENCIES = fmt boost ffmpeg libcurl ecm shaderc webp
DUCKSTATION_GPL_DEPENDENCIES += reglinux-qt6 libbacktrace wayland
DUCKSTATION_GPL_DEPENDENCIES += cpuinfo spirv-cross libsoundtouch lunasvg

DUCKSTATION_GPL_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
DUCKSTATION_GPL_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
DUCKSTATION_GPL_CONF_OPTS += -DENABLE_DISCORD_PRESENCE=OFF
DUCKSTATION_GPL_CONF_OPTS += -DBUILD_QT_FRONTEND=ON
DUCKSTATION_GPL_CONF_OPTS += -DENABLE_WAYLAND=ON
DUCKSTATION_GPL_CONF_OPTS += -DSHADERC_INCLUDE_DIR=$(STAGING_DIR)/shaderc/include
DUCKSTATION_GPL_CONF_OPTS += -DSHADERC_LIBRARY=$(STAGING_DIR)/shaderc/lib/libshaderc_shared.so

# Use clang (if available) for performance
ifeq ($(BR2_PACKAGE_CLANG),y)
DUCKSTATION_GPL_DEPENDENCIES += host-clang
DUCKSTATION_GPL_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang
DUCKSTATION_GPL_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++
DUCKSTATION_GPL_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-no-pie -lm -lstdc++"
endif

DUCKSTATION_GPL_CONF_ENV += LDFLAGS=-lpthread

ifeq ($(BR2_PACKAGE_XORG7),y)
    DUCKSTATION_GPL_CONF_OPTS += -DENABLE_X11=ON
else
    DUCKSTATION_GPL_CONF_OPTS += -DENABLE_X11=OFF
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    DUCKSTATION_GPL_DEPENDENCIES += glslang
    DUCKSTATION_GPL_CONF_OPTS += -DENABLE_VULKAN=ON
else
    DUCKSTATION_GPL_CONF_OPTS += -DENABLE_VULKAN=OFF
endif

define DUCKSTATION_GPL_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    mkdir -p $(TARGET_DIR)/usr/lib
    mkdir -p $(TARGET_DIR)/usr/share/duckstation

    $(INSTALL) -D $(@D)/buildroot-build/bin/duckstation* \
        $(TARGET_DIR)/usr/bin/
    cp -R $(@D)/buildroot-build/bin/resources \
        $(TARGET_DIR)/usr/share/duckstation/
    rm -f $(TARGET_DIR)/usr/share/duckstation/resources/gamecontrollerdb.txt

    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/duckstation-gpl/psx.duckstation-gpl.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

define DUCKSTATION_GPL_PREPARE_TRANSLATIONS
    mkdir -p $(@D)/buildroot-build/bin/resources
endef

define DUCKSTATION_GPL_TRANSLATIONS
    mkdir -p $(TARGET_DIR)/usr/share/duckstation
    cp -R $(@D)/buildroot-build/bin/translations \
        $(TARGET_DIR)/usr/share/duckstation/
endef

DUCKSTATION_GPL_POST_CONFIGURE_HOOKS += DUCKSTATION_GPL_PREPARE_TRANSLATIONS
DUCKSTATION_GPL_POST_INSTALL_TARGET_HOOKS += DUCKSTATION_GPL_TRANSLATIONS

$(eval $(cmake-package))
