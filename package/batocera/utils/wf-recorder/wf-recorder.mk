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

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
WF_RECORDER_CONF_OPTS = -Dpulse=enabled
else
WF_RECORDER_CONF_OPTS = -Dpulse=disabled
endif

$(eval $(meson-package))
