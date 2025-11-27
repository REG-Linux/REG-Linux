################################################################################
#
# xenia-canary
#
################################################################################
# Version: Commits on Aug 12, 2025
#XENIA_CANARY_VERSION = 7d379952f19bded6931f821fad7df29166ec2cc3
#XENIA_CANARY_SITE = https://github.com/xenia-canary/xenia-canary
# Version: Custom
XENIA_CANARY_VERSION = 3911cc33018bcd96284ffa43285aa387d409e0db
XENIA_CANARY_SITE = https://github.com/xenia-canary/xenia-canary
XENIA_CANARY_SITE_METHOD = git
XENIA_CANARY_GIT_SUBMODULES = YES
XENIA_CANARY_LICENSE = BSD
XENIA_CANARY_LICENSE_FILE = LICENSE

XENIA_CANARY_DEPENDENCIES = python-toml llvm clang libgtk3 sdl2 host-sdl2

# Remove linker flags wrongly passed to clang compile stage
XENIA_CANARY_CONF_ENV += CFLAGS="$(filter-out -Wl,-z,max-page-size=4096 -Wl,-z,common-page-size=4096,$(CFLAGS))"
XENIA_CANARY_CONF_ENV += CXXFLAGS="$(filter-out -Wl,-z,max-page-size=4096 -Wl,-z,common-page-size=4096,$(CXXFLAGS))"

# Skip fatal warnings
XENIA_CANARY_CONF_OPTS += -DCMAKE_CXX_FLAGS="-Wno-unused-command-line-argument"

# Fix C++ standard library visibility for Clang cross ARM64

# Ensure linker flags go to the linker only
XENIA_CANARY_CONF_ENV += LDFLAGS="$(LDFLAGS) -Wl,-z,max-page-size=4096 -Wl,-z,common-page-size=4096"

define XENIA_CANARY_CONFIGURE_CMDS
	mkdir -p $(@D) && cd $(@D) && \
	XENIA_ARCHITECTURE=$(BR2_ARCH) \
	PKGCONFIG="$(HOST_DIR)/bin/pkg-config" \
	PKGCONFIG_CONFIG=$(STAGING_DIR)/usr/lib/pkgconfig \
	SYSROOT="$(STAGING_DIR)" \
	SDL2CONFIG="$(HOST_DIR)/bin/sdl2-config" \
	CMAKE_MAKE_PROGRAM="$(HOST_DIR)/bin/ninja" \
	PREMAKE_NO_VERSION=1 \
	./xenia-build.py premake
#	CC="$(HOST_DIR)/bin/clang"
endef

define XENIA_CANARY_BUILD_CMDS
	mkdir -p $(@D) && cd $(@D) && \
	XENIA_ARCHITECTURE=$(BR2_ARCH) \
	PKGCONFIG="$(HOST_DIR)/bin/pkg-config" \
	PKGCONFIG_CONFIG=$(STAGING_DIR)/usr/lib/pkgconfig \
	SYSROOT="$(STAGING_DIR)" \
	SDL2CONFIG="$(HOST_DIR)/bin/sdl2-config" \
	NINJA="$(HOST_DIR)/bin/ninja" \
	CC="$(HOST_DIR)/bin/clang" \
	CXX="$(HOST_DIR)/bin/clang++" \
	CXXFLAGS="$(CXXFLAGS)  -I$(STAGING_DIR)/usr/include/c++/14.3.0 -I$(STAGING_DIR)/usr/include/c++/14.3.0/aarch64-buildroot-linux-gnu -stdlib=libstdc++ --gcc-toolchain=$(HOST_DIR)/aarch64-buildroot-linux-gnu --sysroot=$(HOST_DIR)/aarch64-buildroot-linux-gnu/sysroot" \
	LDFLAGS="--target=aarch64-linux-gnu --gcc-toolchain=$(HOST_DIR)/aarch64-buildroot-linux-gnu --sysroot=$(HOST_DIR)/aarch64-buildroot-linux-gnu/sysroot -stdlib=libstdc++ $(LDFLAGS)" \
	./xenia-build.py build --config release
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

$(eval $(generic-package))
