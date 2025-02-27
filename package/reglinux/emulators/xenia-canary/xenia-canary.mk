################################################################################
#
# xenia-canary
#
################################################################################
# Version: Commits on Feb 26, 2025
XENIA_CANARY_VERSION = 60318a5db66516614295146e5d455e4b6fda1be7
XENIA_CANARY_SITE = https://github.com/xenia-canary/xenia-canary
XENIA_CANARY_SITE_METHOD = git
XENIA_CANARY_GIT_SUBMODULES = YES
XENIA_CANARY_LICENSE = BSD
XENIA_CANARY_LICENSE_FILE = LICENSE

XENIA_CANARY_DEPENDENCIES = python-toml host-llvm host-clang libgtk3 sdl2 host-sdl2

define XENIA_CANARY_CONFIGURE_CMDS
	mkdir -p $(@D) && cd $(@D) && \
	PKGCONFIG="$(HOST_DIR)/bin/pkg-config" \
	PKGCONFIG_CONFIG=$(STAGING_DIR)/usr/lib/pkgconfig \
	SYSROOT="$(STAGING_DIR)" \
	SDL2CONFIG="$(HOST_DIR)/bin/sdl2-config" \
	CMAKE_MAKE_PROGRAM="$(HOST_DIR)/bin/ninja" \
	./xb premake #setup --target_os Linux
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
#PATH=$(HOST_DIR)/bin:$(PATH) 
	#TODO pass GCC, only Clang seems supported so far --cc gcc


endef

define XENIA_CANARY_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr
	rsync -av --exclude=".*" $(@D)/build/bin/Linux/Release/ $(TARGET_DIR)/usr/xenia-canary/
endef

define XENIA_CANARY_POST_PROCESS
	# get the latest patches
	mkdir -p $(TARGET_DIR)/usr/xenia-canary/patches
	mkdir -p $(@D)/temp
	( cd $(@D)/temp && $(GIT) init && \
	  $(GIT) remote add origin https://github.com/xenia-canary/game-patches.git && \
	  $(GIT) config core.sparsecheckout true && \
	  echo "patches/*.toml" >> .git/info/sparse-checkout && \
	  $(GIT) pull --depth=1 origin main && \
	  mv -f patches/*.toml $(TARGET_DIR)/usr/xenia-canary/patches \
	)

	# Clean up the temporary directory
	rm -rf $(@D)/temp

	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/reglinux/emulators/xenia-canary/xbox360.xenia-canary.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

XENIA_CANARY_POST_INSTALL_TARGET_HOOKS = XENIA_CANARY_POST_PROCESS

$(eval $(generic-package))
