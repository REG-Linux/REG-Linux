################################################################################
#
# Felix86 emulator
#
################################################################################
# Version.: Release on Jan 31, 2026
FELIX86_VERSION = 26.03
FELIX86_SITE = $(call github,OFFTKP,felix86,$(FELIX86_VERSION))
FELIX86_LICENSE = GPLv3
FELIX86_DEPENDENCIES = vulkan-headers vulkan-loader

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
FELIX86_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
FELIX86_DEPENDENCIES += libgles
endif

ifeq ($(BR2_PACKAGE_HAS_LIBEGL),y)
FELIX86_DEPENDENCIES += libegl
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
FELIX86_DEPENDENCIES += vulkan-headers vulkan-loader
endif

# Thunking requires gl + vulkan + x11 at the moment
ifeq ($(BR2_PACKAGE_HAS_LIBGL)$(BR2_PACKAGE_REGLINUX_VULKAN)$(BR2_PACKAGE_XORG7),yyy)
FELIX86_CONF_OPTS += -DBUILD_THUNKING=ON
else
FELIX86_CONF_OPTS += -DBUILD_THUNKING=OFF
endif

FELIX86_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
FELIX86_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

# We need to install manually those binaries
define FELIX86_INSTALL_BINARIES
	$(INSTALL) -D -m 0755 $(@D)/felix86           $(TARGET_DIR)/usr/bin/felix86
endef

FELIX86_POST_INSTALL_TARGET_HOOKS += FELIX86_INSTALL_BINARIES

$(eval $(cmake-package))
