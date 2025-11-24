################################################################################
#
# glsl-shaders
#
################################################################################
# Version: Commits on Nov 16, 2025
GLSL_SHADERS_VERSION = 468f67b6f6788e2719d1dd28dfb2c9b7c3db3cc7
GLSL_SHADERS_SITE = $(call github,libretro,glsl-shaders,$(GLSL_SHADERS_VERSION))
GLSL_SHADERS_LICENSE = GPL

define GLSL_SHADERS_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" \
	CXXFLAGS="$(TARGET_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile
endef

define GLSL_SHADERS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/shaders
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) \
	    INSTALLDIR=$(TARGET_DIR)/usr/share/reglinux/shaders install
	sed -e "s:^//#define CURVATURE:#define CURVATURE:" \
	    $(TARGET_DIR)/usr/share/reglinux/shaders/crt/shaders/crt-pi.glsl > \
		    $(TARGET_DIR)/usr/share/reglinux/shaders/crt/shaders/crt-pi-curvature.glsl
	sed -e 's:^shader0 = "shaders/crt-pi.glsl":shader0 = "shaders/crt-pi-curvature.glsl":' \
	    $(TARGET_DIR)/usr/share/reglinux/shaders/crt/crt-pi.glslp > \
		    $(TARGET_DIR)/usr/share/reglinux/shaders/crt/crt-pi-curvature.glslp
endef

# No Mega Bezel / koko-aio for non-x86 systems
define GLSL_SHADERS_DELETE_BEZEL
    rm -Rf $(TARGET_DIR)/usr/share/reglinux/shaders/bezel/Mega_Bezel
    rm -Rf $(TARGET_DIR)/usr/share/reglinux/shaders/bezel/koko-aio
endef
ifneq ($(BR2_x86_64),y)
    GLSL_SHADERS_POST_INSTALL_TARGET_HOOKS += GLSL_SHADERS_DELETE_BEZEL
endif

# No beefy shaders for weak devices (can be improved)
define GLSL_SHADERS_DELETE_BEEFY_SHADERS
    rm -Rf $(TARGET_DIR)/usr/share/reglinux/shaders/crt/shaders/crt-royale
    rm -Rf $(TARGET_DIR)/usr/share/reglinux/shaders/crt/shaders/crt-yo6
    rm -Rf $(TARGET_DIR)/usr/share/reglinux/shaders/procedural
endef
ifeq ($(BR2_arm)$(BR2_mipsel)$(BR2_riscv),y)
    GLSL_SHADERS_POST_INSTALL_TARGET_HOOKS += GLSL_SHADERS_DELETE_BEEFY_SHADERS
endif

$(eval $(generic-package))
