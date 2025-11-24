################################################################################
#
# slang-shaders
#
################################################################################
# Version: Commits on Nov 23, 2025
SLANG_SHADERS_VERSION = 2907b8d9e49ec2e2f23ce8ed3a360e77917a8f26
SLANG_SHADERS_SITE = $(call github,libretro,slang-shaders,$(SLANG_SHADERS_VERSION))
SLANG_SHADERS_LICENSE = GPL

define SLANG_SHADERS_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" \
	CXXFLAGS="$(TARGET_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" \
	    CC="$(TARGET_CC)" -C $(@D)/ -f Makefile
endef

define SLANG_SHADERS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/shaders
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) \
	    INSTALLDIR=$(TARGET_DIR)/usr/share/reglinux/shaders install
endef

# No Mega Bezel / koko-aio for non-x86 systems
define SLANG_SHADERS_DELETE_BEZEL
    rm -Rf $(TARGET_DIR)/usr/share/reglinux/shaders/bezel/Mega_Bezel
    rm -Rf $(TARGET_DIR)/usr/share/reglinux/shaders/bezel/koko-aio
endef
ifneq ($(BR2_x86_64),y)
    SLANG_SHADERS_POST_INSTALL_TARGET_HOOKS += SLANG_SHADERS_DELETE_BEZEL
endif

$(eval $(generic-package))
