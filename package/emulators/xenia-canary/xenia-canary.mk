################################################################################
#
# xenia-canary
#
################################################################################
# Version: Commits on Jul 29, 2025
XENIA_CANARY_VERSION = 43d206d2e99ada38804fa68c20def23bdf6e1c3f
XENIA_CANARY_SITE = https://github.com/xenia-canary/xenia-canary
XENIA_CANARY_SITE_METHOD = git
XENIA_CANARY_GIT_SUBMODULES = YES
XENIA_CANARY_LICENSE = BSD
XENIA_CANARY_LICENSE_FILE = LICENSE

XENIA_CANARY_DEPENDENCIES = python-toml llvm clang libgtk3 sdl2 host-sdl2
# Extra for WIP posix stack walker
#XENIA_CANARY_DEPENDENCIES += libunwind binutils

# Hack for d3d12 WIP
#XENIA_CANARY_DEPENDENCIES += vkd3d-proton dxvk pevents
#MESON="$(HOST_DIR)/bin/meson" \
#NINJA="$(HOST_DIR)/bin/ninja" \

define XENIA_CANARY_CONFIGURE_CMDS
	mkdir -p $(@D) && cd $(@D) && \
	PKGCONFIG="$(HOST_DIR)/bin/pkg-config" \
	PKGCONFIG_CONFIG=$(STAGING_DIR)/usr/lib/pkgconfig \
	SYSROOT="$(STAGING_DIR)" \
	SDL2CONFIG="$(HOST_DIR)/bin/sdl2-config" \
	CMAKE_MAKE_PROGRAM="$(HOST_DIR)/bin/ninja" \
	CC="$(HOST_DIR)/bin/clang" \
	./xb premake
endef

define XENIA_CANARY_BUILD_CMDS
	mkdir -p $(@D) && cd $(@D) && \
	PKGCONFIG="$(HOST_DIR)/bin/pkg-config" \
	PKGCONFIG_CONFIG=$(STAGING_DIR)/usr/lib/pkgconfig \
	SYSROOT="$(STAGING_DIR)" \
	SDL2CONFIG="$(HOST_DIR)/bin/sdl2-config" \
	NINJA="$(HOST_DIR)/bin/ninja" \
	CC="$(HOST_DIR)/bin/clang" \
	CXX="$(HOST_DIR)/bin/clang++" \
	./xb build --config release
endef

define XENIA_CANARY_INSTALL_TARGET_CMDS
	# Copy stripped binary
	mkdir -p $(TARGET_DIR)/usr/bin
	$(TARGET_STRIP) $(@D)/build/bin/Linux/Release/xenia_canary
	cp $(@D)/build/bin/Linux/Release/xenia_canary $(TARGET_DIR)/usr/bin/
endef

define XENIA_CANARY_POST_PROCESS
	# get the latest patches
	mkdir -p $(TARGET_DIR)/usr/share/xenia-canary/patches
	mkdir -p $(@D)/temp
	( cd $(@D)/temp && $(BR2_GIT) init && \
	  $(BR2_GIT) remote add origin https://github.com/xenia-canary/game-patches.git && \
	  $(BR2_GIT) config core.sparsecheckout true && \
	  echo "patches/*.toml" >> .git/info/sparse-checkout && \
	  $(BR2_GIT) pull --depth=1 origin main && \
	  mv -f patches/*.toml $(TARGET_DIR)/usr/share/xenia-canary/patches \
	)

	# Clean up the temporary directory
	rm -rf $(@D)/temp

	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/xenia-canary/xbox360.xenia-canary.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

XENIA_CANARY_POST_INSTALL_TARGET_HOOKS = XENIA_CANARY_POST_PROCESS

# Hack for d3d12 patch
#define XENIA_CANARY_FIX_SUBMODULES
#	rm -f $(@D)/third_party/vkd3d-proton
#	rm -f $(@D)/third_party/dxvk
#	$(BR2_GIT) -C $(@D)/third_party/ clone https://github.com/HansKristian-Work/vkd3d-proton.git
#	$(BR2_GIT) -C $(@D)/third_party/ clone https://github.com/doitsujin/dxvk.git
#	$(BR2_GIT) -C $(@D)/third_party/ clone https://github.com/neosmart/pevents.git
#	cd $(@D)/third_party/vkd3d-proton && patch -p1 < $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/xenia-canary/xxx-vkd3d-proton.diff
#endef
#XENIA_CANARY_PRE_CONFIGURE_HOOKS += XENIA_CANARY_FIX_SUBMODULES

$(eval $(generic-package))
