################################################################################
#
# Felix86 emulator
#
################################################################################
# Version.: Release on Jan 1st, 2026
FELIX86_VERSION = 26.01
FELIX86_SITE = https://github.com/OFFTKP/felix86
FELIX86_SITE_METHOD=git
FELIX86_LICENSE = GPLv3
FELIX86_DEPENDENCIES = libgl vulkan-headers vulkan-loader

FELIX86_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

# We need to install manually those binaries
define FELIX86_INSTALL_BINARIES
	$(INSTALL) -D -m 0755 $(@D)/felix86           $(TARGET_DIR)/usr/bin/felix86
	$(INSTALL) -D -m 0755 $(@D)/felix86-mounter   $(TARGET_DIR)/usr/bin/felix86-mounter
	$(INSTALL) -D -m 0755 $(@D)/libgit_version.so $(TARGET_DIR)/usr/lib/libgit_version.so
endef

FELIX86_POST_INSTALL_TARGET_HOOKS += FELIX86_INSTALL_BINARIES

$(eval $(cmake-package))
