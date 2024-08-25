################################################################################
#
# wf-recorder
#
################################################################################

WF_RECORDER_VERSION = v0.5.0
WF_RECORDER_SITE = $(call github,ammen99,wf-recorder,$(WF_RECORDER_VERSION))
WF_RECORDER_LICENSE = MIT
WF_RECORDER_LICENSE_FILES = LICENSE
WF_RECORDER_DEPENDENCIES = ffmpeg pipewire


$(eval $(meson-package))
