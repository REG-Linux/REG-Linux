################################################################################
#
# wf-recorder
#
################################################################################

WF_RECORDER_VERSION = v0.5.0
WF_RECORDER_SITE = $(call github,ammen99,wf-recorder,$(WF_RECORDER_VERSION))
WF_RECORDER_LICENSE = MIT
WF_RECORDER_LICENSE_FILES = LICENSE
WF_RECORDER_DEPENDENCIES = ffmpeg

ifeq ($(BR2_PACKAGE_X264),y)
WF_RECORDER_DEPENDENCIES += x264
endif

ifeq ($(BR2_PACKAGE_X265),y)
WF_RECORDER_DEPENDENCIES += x265
endif

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
WF_RECORDER_CONF_OPTS = -Dpulse=enabled
WF_RECORDER_DEPENDENCIES += pulseaudio
else
WF_RECORDER_CONF_OPTS = -Dpulse=disabled
endif

ifeq ($(BR2_PACKAGE_PIPEWIRE),y)
WF_RECORDER_CONF_OPTS = -Dpipewire=enabled
WF_RECORDER_CONF_OPTS = -Ddefault_audio_backend=pipewire
WF_RECORDER_DEPENDENCIES += pipewire
else
WF_RECORDER_CONF_OPTS = -Dpipewire=disabled
endif

$(eval $(meson-package))
