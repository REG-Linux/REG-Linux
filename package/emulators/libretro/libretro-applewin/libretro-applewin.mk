################################################################################
#
# libretro-applewin
#
################################################################################
# Version: Commits on May 31, 2025
LIBRETRO_APPLEWIN_VERSION = $(APPLEWIN_VERSION)
LIBRETRO_APPLEWIN_SITE = https://github.com/audetto/AppleWin
LIBRETRO_APPLEWIN_SITE_METHOD=git
LIBRETRO_APPLEWIN_GIT_SUBMODULES=YES
LIBRETRO_APPLEWIN_LICENSE = GPLv2
LIBRETRO_APPLEWIN_DEPENDENCIES = minizip-zlib
LIBRETRO_APPLEWIN_DEPENDENCIES += host-xxd libyaml slirp libpcap boost

LIBRETRO_APPLEWIN_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_APPLEWIN_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
LIBRETRO_APPLEWIN_CONF_OPTS += -DBUILD_SA2=OFF
LIBRETRO_APPLEWIN_CONF_OPTS += -DBUILD_LIBRETRO=ON

# TODO libretro core build as static
# fails on minizip.a (-fPIC issue)
#LIBRETRO_APPLEWIN_CONF_OPTS += -DSTATIC_LINKING=ON

ifeq ($(BR2_PACKAGE_HAS_OPENGL),y)
LIBRETRO_APPLEWIN_CONF_OPTS += -DSA2_OPENGL=ON
else
LIBRETRO_APPLEWIN_CONF_OPTS += -DSA2_OPENGL=OFF
endif

define LIBRETRO_APPLEWIN_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/lib/libretro
    $(INSTALL) -D $(@D)/buildroot-build/source/frontends/libretro/applewin_libretro.so \
        $(TARGET_DIR)/usr/lib/libretro/
    mkdir -p $(TARGET_DIR)/usr/share/applewin
    cp -R $(@D)/resource/* $(TARGET_DIR)/usr/share/applewin/
    rm $(TARGET_DIR)/usr/share/applewin/resource.h
endef

$(eval $(cmake-package))
