################################################################################
#
# moonlight-embedded
#
################################################################################

MOONLIGHT_EMBEDDED_VERSION = v2.7.1
MOONLIGHT_EMBEDDED_SITE = https://github.com/irtimmer/moonlight-embedded.git
MOONLIGHT_EMBEDDED_SITE_METHOD = git
MOONLIGHT_EMBEDDED_GIT_SUBMODULES=y
MOONLIGHT_EMBEDDED_LICENSE = GPLv3
MOONLIGHT_EMBEDDED_DEPENDENCIES = opus expat libevdev avahi alsa-lib udev \
                                  libcurl libcec ffmpeg sdl2 libenet

MOONLIGHT_EMBEDDED_CONF_OPTS = "-DCMAKE_INSTALL_SYSCONFDIR=/etc"

ifeq ($(BR2_PACKAGE_XORG7),y)
    MOONLIGHT_EMBEDDED_CONF_OPTS += -DENABLE_X11=ON
else
    MOONLIGHT_EMBEDDED_CONF_OPTS += -DENABLE_X11=OFF
endif

# Only enable those on x86 targets
ifeq ($(BR2_PACKAGE_LIBVA)$(BR2_x86_64),yy)
    MOONLIGHT_EMBEDDED_DEPENDENCIES += libva-intel-driver intel-mediadriver
endif

define MOONLIGHT_EMBEDDED_INSTALL_SCRIPTS
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    mkdir -p $(TARGET_DIR)/usr/share/moonlight-embedded
	cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/moonlight-embedded/moonlight.moonlight.keys \
        $(TARGET_DIR)/usr/share/evmapy
    cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/moonlight-embedded/moonlight.conf \
        $(TARGET_DIR)/usr/share/moonlight-embedded/
    install -m 0755 \
	    $(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/moonlight-embedded/system-moonlight \
	    $(TARGET_DIR)/usr/bin/
endef

MOONLIGHT_EMBEDDED_POST_INSTALL_TARGET_HOOKS += MOONLIGHT_EMBEDDED_INSTALL_SCRIPTS

$(eval $(cmake-package))
