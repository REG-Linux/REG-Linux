################################################################################
#
# ikemen
#
################################################################################
# Version: Commits on Sep 21, 2024
# Commit 462397b0d244bfa7d6b010f594cb4ca40520d274 on Sep 22, 2024 breaks build
IKEMEN_VERSION = b58b000896b7d9e111727b109a0d4eca1b4bfe33
IKEMEN_SITE = https://github.com/ikemen-engine/Ikemen-GO
IKEMEN_LICENSE = MIT
IKEMEN_DEPENDENCIES = libgtk3 libgl openal libglfw

IKEMEN_SITE_METHOD = git
IKEMEN_GIT_SUBMODULES = YES

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

define IKEMEN_BUILD_CMDS
	$(HOST_GO_TARGET_ENV) $(MAKE) -C $(@D) -f Makefile Ikemen_GO_Linux
endef

define IKEMEN_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D $(@D)/bin/Ikemen_GO_Linux $(TARGET_DIR)/usr/bin/ikemen
	# evmapy
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/ikemen/ikemen.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(golang-package))
