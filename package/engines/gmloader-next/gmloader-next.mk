################################################################################
#
# gmloader-next
#
################################################################################

GMLOADER_NEXT_VERSION = e31ecea4bf1b5d88c99286dc336fb9d12037d4c1
GMLOADER_NEXT_SITE = https://github.com/JohnnyonFlame/gmloader-next
GMLOADER_NEXT_SITE_METHOD = git
GMLOADER_NEXT_GIT_SUBMODULES = YES

GMLOADER_NEXT_LICENSE = GPL-2.0
GMLOADER_NEXT_LICENSE_FILES = LICENSE

GMLOADER_NEXT_DEPENDENCIES = sdl2 zlib

ifeq ($(BR2_aarch64),y)
GMLOADER_NEXT_ARCH = aarch64-linux-gnu
GMLOADER_NEXT_DEVICE_ARCH = aarch64
else ifeq ($(BR2_arm),y)
GMLOADER_NEXT_ARCH = arm-linux-gnueabihf
GMLOADER_NEXT_DEVICE_ARCH = armhf
endif

# Pre-generated thunk headers (avoids LLVM/libclang host dependency).
# Regenerate with: python3 scripts/generate_libc.py <arch> --llvm-library-file <libclang.so> --llvm-includes <sysroot/include>
define GMLOADER_NEXT_INSTALL_GENERATED_HEADERS
	mkdir -p $(@D)/build/$(GMLOADER_NEXT_ARCH)/thunks/libc
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/gmloader-next/impl_tab.h \
		$(@D)/build/$(GMLOADER_NEXT_ARCH)/thunks/libc/
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/gmloader-next/impl_header.h \
		$(@D)/build/$(GMLOADER_NEXT_ARCH)/thunks/libc/
	touch $(@D)/build/$(GMLOADER_NEXT_ARCH)/thunks/libc/impl_tab.h \
		$(@D)/build/$(GMLOADER_NEXT_ARCH)/thunks/libc/impl_header.h
endef
GMLOADER_NEXT_POST_EXTRACT_HOOKS += GMLOADER_NEXT_INSTALL_GENERATED_HEADERS

# Copy pre-generated config headers for vendored libs
define GMLOADER_NEXT_SETUP_VENDORED_CONFIGS
	cp $(@D)/3rdparty/libzip-config/zipconf.$(GMLOADER_NEXT_ARCH).h \
		$(@D)/3rdparty/libzip/lib/zipconf.h
	cp $(@D)/3rdparty/libzip-config/config.h \
		$(@D)/3rdparty/libzip/lib/config.h 2>/dev/null || true
	cp $(@D)/3rdparty/libbsd-config/libbsd.$(GMLOADER_NEXT_ARCH).h \
		$(@D)/3rdparty/libbsd/include/bsd/config.h 2>/dev/null || true
	cp $(@D)/3rdparty/libbsd-config/libmd.$(GMLOADER_NEXT_ARCH).h \
		$(@D)/3rdparty/libmd/config.h 2>/dev/null || true
endef
GMLOADER_NEXT_POST_EXTRACT_HOOKS += GMLOADER_NEXT_SETUP_VENDORED_CONFIGS

define GMLOADER_NEXT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -f Makefile.gmloader -C $(@D) \
		ARCH=$(GMLOADER_NEXT_ARCH) \
		CC="$(TARGET_CC)" \
		CXX="$(TARGET_CXX)" \
		LD="$(TARGET_LD)" \
		PKG_CONFIG="$(PKG_CONFIG_HOST_BINARY)" \
		OPTM="$(TARGET_OPTIMIZATION)" \
		-j$(PARALLEL_JOBS)
endef

define GMLOADER_NEXT_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 \
		$(@D)/build/$(GMLOADER_NEXT_ARCH)/gmloader/gmloadernext.$(GMLOADER_NEXT_DEVICE_ARCH) \
		$(TARGET_DIR)/usr/bin/gmloadernext
endef

$(eval $(generic-package))
