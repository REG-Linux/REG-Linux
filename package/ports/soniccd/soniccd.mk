################################################################################
#
# soniccd
#
################################################################################
# Version: Commits on Oct 31, 2025
SONICCD_VERSION = 7c6474eaaaa55ee70fda912ca10114d9a84cdc93
SONICCD_SITE = https://github.com/RSDKModding/RSDKv3-Decompilation.git
SONICCD_SITE_METHOD = git
SONICCD_GIT_SUBMODULES = YES
SONICCD_LICENSE = Custom

SONICCD_DEPENDENCIES = sdl2 libogg libvorbis libtheora

SONICCD_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SONICCD_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
SONICCD_CONF_OPTS += -DBUILD_STATIC_LIBS=ON

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    SONICCD_DEPENDENCIES += libgl libglew libglu
endif

define SONICCD_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile VERBOSE=1
endef

define SONICCD_INSTALL_TARGET_CMDS
	$(TARGET_STRIP) $(@D)/bin/RSDKv3
	$(INSTALL) -D -m 0755 $(@D)/bin/RSDKv3 $(TARGET_DIR)/usr/bin/soniccd
endef

define SONICCD_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy $(TARGET_DIR)/usr/share/soniccd
	cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/soniccd/sonicretro.soniccd.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

SONICCD_POST_INSTALL_TARGET_HOOKS += SONICCD_POST_PROCESS

$(eval $(generic-package))
