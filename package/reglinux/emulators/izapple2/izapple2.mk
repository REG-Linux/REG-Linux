################################################################################
#
# izapple2
#
################################################################################
# Version: Release on Jan 25, 2025
IZAPPLE2_VERSION = v2.2
IZAPPLE2_SITE = $(call github,ivanizag,izapple2,$(IZAPPLE2_VERSION))
IZAPPLE2_LICENSE = GPLv3
IZAPPLE2_DEPENDENCIES = sdl2

HOST_GO_COMMON_ENV = GOFLAGS=-mod=mod \
		     GO111MODULE=on \
		     GOROOT="$(HOST_GO_ROOT)" \
		     GOPATH="$(HOST_GO_GOPATH)" \
		     GOCACHE="$(HOST_GO_TARGET_CACHE)" \
		     GOMODCACHE="$(@D)" \
		     GOFLAGS="-modcacherw" \
		     PATH=$(BR_PATH) \
		     GOBIN= \
		     CGO_ENABLED=$(HOST_GO_CGO_ENABLED)

define IZAPPLE2_BUILD_CMDS
	cd $(@D) && $(HOST_GO_TARGET_ENV) $(GO_BIN) build
	cd $(@D)/frontend/a2sdl && $(HOST_GO_TARGET_ENV) $(GO_BIN) build
endef

define IZAPPLE2_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D $(@D)/frontend/a2sdl/a2sdl $(TARGET_DIR)/usr/bin/izapple2
	$(TARGET_STRIP) $(TARGET_DIR)/usr/bin/izapple2
	# evmapy
	#mkdir -p $(TARGET_DIR)/usr/share/evmapy
	#cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/reglinux/emulators/izapple2/izapple2.keys \
	#    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(golang-package))
