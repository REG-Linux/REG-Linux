################################################################################
#
# EKA2L1
#
################################################################################
EKA2L1_VERSION = e67f84dc605ea30afc1ab6f4f43c0f855eec79a5
EKA2L1_SITE = https://github.com/EKA2L1/EKA2L1.git
EKA2L1_SITE_METHOD=git
EKA2L1_GIT_SUBMODULES=YES
EKA2L1_LICENSE = GPLv2
EKA2L1_DEPENDENCIES = reglinux-qt6 ffmpeg

EKA2L1_SUPPORTS_IN_SOURCE_BUILD = NO

# Choose X11 or Wayland
ifeq ($(BR2_PACKAGE_REGLINUX_XWAYLAND),y)
EKA2L1_CONF_OPTS += -DEKA2L1_UNIX_USE_X11=ON
EKA2L1_CONF_OPTS += -DEKA2L1_UNIX_USE_WAYLAND=OFF
else
EKA2L1_CONF_OPTS += -DEKA2L1_UNIX_USE_X11=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_UNIX_USE_WAYLAND=ON
endif

# Makes GCC14 happy
EKA2L1_CONF_ENV = CFLAGS="-Wno-error=incompatible-pointer-types -Wno-error=int-conversion" CXXFLAGS="-Wno-error=incompatible-pointer-types -Wno-error=int-conversion"

EKA2L1_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
EKA2L1_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
EKA2L1_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
EKA2L1_CONF_OPTS += -DEKA2L1_ENABLE_SCRIPTING_ABILITY=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_BUILD_TOOLS=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_BUILD_TESTS=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_USE_SYSTEM_FFMPEG=ON
EKA2L1_CONF_OPTS += -DENABLE_PROGRAMS=OFF # for mbedtls

define EKA2L1_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/eka2l1
    $(TARGET_STRIP) $(@D)/buildroot-build/bin/eka2l1_qt
    cp -R $(@D)/buildroot-build/bin/* \
                $(TARGET_DIR)/usr/eka2l1/
endef


$(eval $(cmake-package))
