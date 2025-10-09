################################################################################
#
# applewin
#
################################################################################
# Version: Commits on Oct 5, 2025
APPLEWIN_VERSION = f7eb91462d7f2e8d5aff35bcf9852f51015584c7
APPLEWIN_SITE = https://github.com/audetto/AppleWin
APPLEWIN_SITE_METHOD=git
APPLEWIN_GIT_SUBMODULES=YES
APPLEWIN_LICENSE = GPLv2
APPLEWIN_DEPENDENCIES = sdl2 sdl2_image minizip-zlib
APPLEWIN_DEPENDENCIES += host-xxd libyaml slirp libpcap boost

APPLEWIN_SUPPORTS_IN_SOURCE_BUILD = NO

APPLEWIN_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
APPLEWIN_CONF_OPTS += -DBUILD_SA2=ON
APPLEWIN_CONF_OPTS += -DBUILD_LIBRETRO=OFF

ifeq ($(BR2_PACKAGE_HAS_OPENGL),y)
APPLEWIN_CONF_OPTS += -DSA2_OPENGL=ON
else
APPLEWIN_CONF_OPTS += -DSA2_OPENGL=OFF
endif

define APPLEWIN_INSTALL_TARGET_CMDS
	cp -avf $(@D)/buildroot-build/sa2 $(TARGET_DIR)/usr/bin/applewin
	mkdir -p $(TARGET_DIR)/usr/share/applewin

	cp -R $(@D)/resource/* $(TARGET_DIR)/usr/share/applewin/
	rm $(TARGET_DIR)/usr/share/applewin/resource.h

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/applewin/evmapy/* \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
