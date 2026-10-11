################################################################################
#
# serioussam — Serious Sam TFE + TSE (Serious Engine 1, ptitSeb ARM fork)
#
################################################################################

SERIOUSSAM_VERSION = e6d0536908a815bc33bc119aa2e9a56c58d61653
SERIOUSSAM_SITE = https://github.com/ptitSeb/Serious-Engine
SERIOUSSAM_SITE_METHOD = git
SERIOUSSAM_LICENSE = GPL-2.0
SERIOUSSAM_LICENSE_FILES = LICENSE
SERIOUSSAM_SUBDIR = Sources

SERIOUSSAM_DEPENDENCIES = host-serioussam sdl2 zlib libvorbis libogg

# TSE (The Second Encounter) build
SERIOUSSAM_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DTFE=FALSE \
	-DUSE_SYSTEM_SDL2=ON \
	-DUSE_SYSTEM_ZLIB=ON \
	-DUSE_SINGLE_THREAD=TRUE \
	-DECC=$(HOST_DIR)/usr/bin/ecc

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
SERIOUSSAM_DEPENDENCIES += libgl
endif

# Host build: only need the ecc (Entity Class Compiler) tool
HOST_SERIOUSSAM_SUBDIR = Sources

HOST_SERIOUSSAM_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DTFE=FALSE

HOST_SERIOUSSAM_BUILD_OPTS = ecc

define HOST_SERIOUSSAM_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(HOST_SERIOUSSAM_BUILDDIR)/ecc \
		$(HOST_DIR)/usr/bin/ecc
endef

# Also build TFE variant after TSE
define SERIOUSSAM_BUILD_TFE
	$(CMAKE) -S $(@D)/Sources -B $(@D)/build-tfe \
		-DCMAKE_TOOLCHAIN_FILE=$(HOST_DIR)/share/buildroot/toolchainfile.cmake \
		-DCMAKE_BUILD_TYPE=Release \
		-DTFE=TRUE \
		-DUSE_SYSTEM_SDL2=ON \
		-DUSE_SYSTEM_ZLIB=ON \
		-DUSE_SINGLE_THREAD=TRUE \
		-DECC=$(HOST_DIR)/usr/bin/ecc
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/build-tfe -j$(PARALLEL_JOBS)
endef
SERIOUSSAM_POST_BUILD_HOOKS += SERIOUSSAM_BUILD_TFE

define SERIOUSSAM_INSTALL_TARGET_CMDS
	# TSE binaries
	-find $(@D)/buildroot-build -name "ssam" -exec $(INSTALL) -D -m 0755 {} $(TARGET_DIR)/usr/bin/ssam-tse \;
	-find $(@D)/buildroot-build -name "*.so" -exec cp {} $(TARGET_DIR)/usr/lib/ \;
	# TFE binaries
	-find $(@D)/build-tfe -name "ssam-tfe" -exec $(INSTALL) -D -m 0755 {} $(TARGET_DIR)/usr/bin/ssam-tfe \;
	-find $(@D)/build-tfe -name "*.so" -exec cp {} $(TARGET_DIR)/usr/lib/ \;
endef

$(eval $(cmake-package))
$(eval $(host-cmake-package))
