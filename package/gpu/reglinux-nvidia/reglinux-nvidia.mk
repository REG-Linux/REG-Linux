################################################################################
#
# reglinux-nvidia
#
################################################################################

REGLINUX_NVIDIA_VERSION = 1.5
REGLINUX_NVIDIA_SOURCE =

define REGLINUX_NVIDIA_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	install -m 0755 \
	    $(BR2_EXTERNAL_REGLINUX_PATH)/package/gpu/reglinux-nvidia/system-drivers-nvidia \
	    $(TARGET_DIR)/usr/bin/

	# [Blacklist & Modprobe]
	mkdir -p $(TARGET_DIR)/etc/modprobe.d
	ln -sf /var/run/nvidia/modprobe/blacklist-nouveau.conf \
	    $(TARGET_DIR)/etc/modprobe.d/blacklist-nouveau.conf
	ln -sf /var/run/nvidia/modprobe/nvidia-drm.conf \
	    $(TARGET_DIR)/etc/modprobe.d/nvidia-drm.conf
endef

$(eval $(generic-package))
