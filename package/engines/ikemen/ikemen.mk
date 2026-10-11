################################################################################
#
# ikemen
#
################################################################################
# Version: Commits on Sep 21, 2024
# This version has native SDL2 support (stable, no go.mod issues)
IKEMEN_VERSION = b58b000896b7d9e111727b109a0d4eca1b4bfe33
IKEMEN_SITE = https://github.com/ikemen-engine/Ikemen-GO.git
IKEMEN_SITE_METHOD = git
IKEMEN_GIT_SUBMODULES = YES
IKEMEN_LICENSE = MIT
IKEMEN_LICENSE_FILES = LICENSE

IKEMEN_DEPENDENCIES = libgtk3 sdl2 libgl

# GOFLAGS="-modcacherw" is used to fix directory permissions to make sure cleanbuild works.
# For details see: https://github.com/golang/go/issues/27161 https://github.com/golang/go/issues/27455
HOST_GO_COMMON_ENV = GOFLAGS="-mod=mod -modcacherw" \
		     GO111MODULE=on \
		     GOPROXY=direct \
		     GOROOT="$(HOST_GO_ROOT)" \
		     GOPATH="$(HOST_GO_GOPATH)" \
		     GOCACHE="$(HOST_GO_TARGET_CACHE)" \
		     GOMODCACHE="$(@D)" \
		     PATH=$(BR_PATH) \
		     GOBIN= \
		     CGO_ENABLED=$(HOST_GO_CGO_ENABLED)

define IKEMEN_BUILD_CMDS
	$(HOST_GO_TARGET_ENV) $(MAKE) -C $(@D) -f Makefile Ikemen_GO_Linux
endef

define IKEMEN_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D $(@D)/bin/Ikemen_GO_Linux $(TARGET_DIR)/usr/bin/ikemen
endef

$(eval $(golang-package))
