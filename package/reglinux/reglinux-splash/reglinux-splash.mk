################################################################################
#
# REG-Linux splash
#
################################################################################
REGLINUX_SPLASH_VERSION = 5.4
REGLINUX_SPLASH_SOURCE=

REGLINUX_SPLASH_TGVERSION=$(BATOCERA_SYSTEM_VERSION) $(BATOCERA_SYSTEM_DATE)

# video or image
ifeq ($(BR2_PACKAGE_REGLINUX_SPLASH_OMXPLAYER),y)
    REGLINUX_SPLASH_SCRIPT=Ssplash-omx
    REGLINUX_SPLASH_MEDIA=video
else ifeq ($(BR2_PACKAGE_REGLINUX_SPLASH_FFPLAY),y)
    REGLINUX_SPLASH_SCRIPT=Ssplash-ffplay
    REGLINUX_SPLASH_DEPENDENCIES=ffmpeg
    REGLINUX_SPLASH_MEDIA=video
else
    REGLINUX_SPLASH_SCRIPT=Ssplash-image
    REGLINUX_SPLASH_MEDIA=image
endif

# FFPLAY options
ifeq ($(BR2_PACKAGE_REGLINUX_SPLASH_FFPLAY),y)
	# None so far
        REGLINUX_SPLASH_PLAYER_OPTIONS=
endif

REGLINUX_SPLASH_POST_INSTALL_TARGET_HOOKS += REGLINUX_SPLASH_INSTALL_SCRIPT

ifeq ($(REGLINUX_SPLASH_MEDIA),image)
    REGLINUX_SPLASH_POST_INSTALL_TARGET_HOOKS += REGLINUX_SPLASH_INSTALL_IMAGE
endif

ifeq ($(REGLINUX_SPLASH_MEDIA),video)
    REGLINUX_SPLASH_POST_INSTALL_TARGET_HOOKS += REGLINUX_SPLASH_INSTALL_VIDEO
    REGLINUX_SPLASH_POST_INSTALL_TARGET_HOOKS += REGLINUX_SPLASH_INSTALL_BOOT_LOGO

    # Capcom video only for H3 build (for CHA)
    ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
        REGLINUX_SPLASH_POST_INSTALL_TARGET_HOOKS += REGLINUX_SPLASH_INSTALL_VIDEO_CAPCOM
    endif

    # alternative video
    ifeq ($(BR2_PACKAGE_BATOCERA_RPI_ANY)$(BR2_PACKAGE_BATOCERA_TARGET_RK3326)$(BR2_PACKAGE_BATOCERA_TARGET_RK3128)$(BR2_PACKAGE_BATOCERA_TARGET_H3),y)
        BATO_SPLASH=$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/videos/splash720p.mp4
    else
        BATO_SPLASH=$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/videos/splash.mp4
    endif
endif

define REGLINUX_SPLASH_INSTALL_SCRIPT
    mkdir -p $(TARGET_DIR)/etc/init.d
    install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/scripts/Ssystem-splash            $(TARGET_DIR)/etc/init.d/S03system-splash
    install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/scripts/Ssplashscreencontrol      $(TARGET_DIR)/etc/init.d/S30splashscreencontrol
    install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/scripts/$(REGLINUX_SPLASH_SCRIPT) $(TARGET_DIR)/etc/init.d/S28splash
    sed -i -e s+"%PLAYER_OPTIONS%"+"$(REGLINUX_SPLASH_PLAYER_OPTIONS)"+g $(TARGET_DIR)/etc/init.d/S28splash
endef

define REGLINUX_SPLASH_INSTALL_BOOT_LOGO
    mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo.png"		"${TARGET_DIR}/usr/share/batocera/splash/boot-logo.png"
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-240.png"	"${TARGET_DIR}/usr/share/batocera/splash/boot-logo-320x240.png"
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-480p.png"	"${TARGET_DIR}/usr/share/batocera/splash/boot-logo-640x480.png"
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-720p.png"	"${TARGET_DIR}/usr/share/batocera/splash/boot-logo-1280x720.png"

    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-240-rotate.png"		"${TARGET_DIR}/usr/share/batocera/splash/boot-logo-240x320.png"
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-3-2-480-rotate.png"		"${TARGET_DIR}/usr/share/batocera/splash/boot-logo-320x480.png"
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-16-9-480-rotate.png"		"${TARGET_DIR}/usr/share/batocera/splash/boot-logo-480x854.png"
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-720p-rotate.png"		"${TARGET_DIR}/usr/share/batocera/splash/boot-logo-720x1280.png"
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-1152-rotate.png"		"${TARGET_DIR}/usr/share/batocera/splash/boot-logo-1152x1920.png"
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-1080p-rotate.png"		"${TARGET_DIR}/usr/share/batocera/splash/boot-logo-1080x1920.png"
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-1080p-rotate-left.png"	"${TARGET_DIR}/usr/share/batocera/splash/boot-logo-1080x1920-left.png"
endef

define REGLINUX_SPLASH_INSTALL_VIDEO
    mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
    cp $(BATO_SPLASH) $(TARGET_DIR)/usr/share/batocera/splash/splash.mp4
    echo -e "1\n00:00:00,000 --> 00:00:02,000\n$(REGLINUX_SPLASH_TGVERSION)" > "${TARGET_DIR}/usr/share/batocera/splash/splash.srt"
endef

# Hack for CHA, custom Capcom splash video
define REGLINUX_SPLASH_INSTALL_VIDEO_CAPCOM
    mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
    rm $(TARGET_DIR)/usr/share/batocera/splash/splash.mp4
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/videos/Capcom.mp4 $(TARGET_DIR)/usr/share/batocera/splash/splash.mp4
    echo -e "1\n00:00:00,000 --> 00:00:02,000\n$(REGLINUX_SPLASH_TGVERSION)" > "${TARGET_DIR}/usr/share/batocera/splash/splash.srt"
endef

define REGLINUX_SPLASH_INSTALL_IMAGE
    mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
    convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo.png" -fill white -pointsize 30 -annotate +50+1020 "$(REGLINUX_SPLASH_TGVERSION)" "${TARGET_DIR}/usr/share/batocera/splash/logo-version.png"
    convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-3-2-480-rotate.png" -fill white -pointsize 15 -annotate 270x270+300+440 "$(REGLINUX_SPLASH_TGVERSION)" "${TARGET_DIR}/usr/share/batocera/splash/logo-version-320x480.png"
    convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-16-9-480-rotate.png" -fill white -pointsize 20 -annotate 270x270+440+814 "$(REGLINUX_SPLASH_TGVERSION)" "${TARGET_DIR}/usr/share/batocera/splash/logo-version-480x854.png"
    convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-480p.png" -fill white -pointsize 20 -annotate +40+440 "$(REGLINUX_SPLASH_TGVERSION)" "${TARGET_DIR}/usr/share/batocera/splash/logo-version-640x480.png"
    convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-240.png" -fill white -pointsize 15 -annotate +20+220 "$(REGLINUX_SPLASH_TGVERSION)" "${TARGET_DIR}/usr/share/batocera/splash/logo-version-320x240.png"
    convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-splash/images/logo-480-dmg.png" -fill white -pointsize 20 -annotate +40+440 "$(REGLINUX_SPLASH_TGVERSION)" "${TARGET_DIR}/usr/share/batocera/splash/logo-version-640x480-dmg.png"
endef

$(eval $(generic-package))
