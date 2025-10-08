################################################################################
#
# Rclone
#
################################################################################

RCLONE_VERSION = v1.69.1
RCLONE_SITE = $(call github,rclone,rclone,$(RCLONE_VERSION))
RCLONE_LICENSE = GPLv2
RCLONE_DEPENDENCIES =

define RCLONE_BUILD_CMDS
	cd $(@D) && $(HOST_GO_TARGET_ENV) CGO_ENABLED=0 GO111MODULE=on $(GO_BIN) build -trimpath -gcflags="all=-l -B" -ldflags="-s -w"
endef

define RCLONE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin

	$(INSTALL) -D $(@D)/rclone $(TARGET_DIR)/usr/bin/rclone
endef

$(eval $(golang-package))
