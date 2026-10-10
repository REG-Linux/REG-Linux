################################################################################
#
# reglinux-pipewire
#
################################################################################

REGLINUX_PIPEWIRE_VERSION = 6.9
REGLINUX_PIPEWIRE_LICENSE = GPL
REGLINUX_PIPEWIRE_SOURCE=

# this one is important because the package erase the default pipewire config files
# so it must be built after it
REGLINUX_PIPEWIRE_DEPENDENCIES = pipewire wireplumber alsa-ucm-conf

define REGLINUX_PIPEWIRE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR) \
		$(TARGET_DIR)/usr/bin \
		$(TARGET_DIR)/usr/share/sounds \
		$(TARGET_DIR)/etc/init.d \
		$(TARGET_DIR)/etc/dbus-1/system.d \
		$(TARGET_DIR)/etc/alsa/conf.d \
		$(TARGET_DIR)/usr/share/pipewire/media-session.d

	# sample audio files
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/audio/reglinux-pipewire/*.wav \
	    $(TARGET_DIR)/usr/share/sounds

	# init script
	install -m 0755 $(BR2_EXTERNAL_REGLINUX_PATH)/package/audio/reglinux-pipewire/Saudio \
		$(TARGET_DIR)/etc/init.d/S06audio

	# Boot restore of audio device/profile/volume is handled natively by
	# regmsgd (audio::apply_boot); S27audioconfig is no longer installed.
	# The ALSA mixer setup that used to live here (soundconfig, driven by a
	# udev rule on controlC*, plus the asoundrc templates) is gone with it:
	# WirePlumber owns the cards now and applies its own route volumes.

	# pipewire-pulse policy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/audio/reglinux-pipewire/pulseaudio-system.conf \
		$(TARGET_DIR)/etc/dbus-1/system.d

	# pipewire-alsa: this is the BRIDGE, not the ALSA stack -- it is what lets
	# an emulator that only speaks ALSA reach PipeWire, so it stays.
	ln -sft $(TARGET_DIR)/etc/alsa/conf.d \
		/usr/share/alsa/alsa.conf.d/{50-pipewire,99-pipewire-default}.conf

	# wireplumber config: disable dbus device reservation
	mkdir -p $(TARGET_DIR)/usr/share/wireplumber/wireplumber.conf.d
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/audio/reglinux-pipewire/80-disable-device-reservation.conf \
		$(TARGET_DIR)/usr/share/wireplumber/wireplumber.conf.d/80-disable-device-reservation.conf
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/audio/reglinux-pipewire/51-hdmi-audio-format.conf \
		$(TARGET_DIR)/usr/share/wireplumber/wireplumber.conf.d/51-hdmi-audio-format.conf

	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/audio/reglinux-pipewire/pipewire.conf \
		$(TARGET_DIR)/usr/share/pipewire/pipewire.conf
endef

define REGLINUX_PIPEWIRE_X86_INTEL_DSP
	mkdir -p $(TARGET_DIR)/etc/modprobe.d
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/audio/reglinux-pipewire/intel-dsp.conf \
	    $(TARGET_DIR)/etc/modprobe.d/intel-dsp.conf
endef

# Steam Deck OLED SOF files are not in the sound-open-firmware package yet
# Steam Deck LCD still requires their own UCM2 conf files too
define REGLINUX_PIPEWIRE_STEAM_DECK
	mkdir -p $(TARGET_DIR)/lib/firmware/amd/sof
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/audio/reglinux-pipewire/sof-vangogh-*.* \
	    $(TARGET_DIR)/lib/firmware/amd/sof/
	mkdir -p $(TARGET_DIR)/lib/firmware/amd/sof-tplg
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/audio/reglinux-pipewire/sof-vangogh-nau8821-max.tplg \
	    $(TARGET_DIR)/lib/firmware/amd/sof-tplg/sof-vangogh-nau8821-max.tplg
	# extra ucm files
	mkdir -p $(TARGET_DIR)/usr/share/alsa/ucm2
	cp -pr $(BR2_EXTERNAL_REGLINUX_PATH)/package/audio/reglinux-pipewire/ucm2/* \
	    $(TARGET_DIR)/usr/share/alsa/ucm2/
endef

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86_ANY),y)
    REGLINUX_PIPEWIRE_DEPENDENCIES += sound-open-firmware
    REGLINUX_PIPEWIRE_POST_INSTALL_TARGET_HOOKS += REGLINUX_PIPEWIRE_X86_INTEL_DSP
    REGLINUX_PIPEWIRE_POST_INSTALL_TARGET_HOOKS += REGLINUX_PIPEWIRE_STEAM_DECK
endif

$(eval $(generic-package))
