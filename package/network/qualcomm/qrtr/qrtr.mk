################################################################################
#
# qrtr
#
################################################################################

# Commits on Mar 1, 2025
QRTR_VERSION = 5923eea97377f4a3ed9121b358fd919e3659db7b
QRTR_SITE = $(call github,linux-msm,qrtr,$(QRTR_VERSION))
QRTR_LICENSE = BSD-3-Clause license
QRTR_LICENSE_FILE = LICENSE
QRTR_DEPENDENCIES = linux-headers
QRTR_INSTALL_STAGING = YES

#define QRTR_BUILD_CMDS
#    $(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D) all
#endef

#define QRTR_INSTALL_STAGING_CMDS
#    $(INSTALL) -D -m 0755 $(@D)/qrtr-ns $(STAGING_DIR)/usr/bin
#    $(INSTALL) -D -m 0755 $(@D)/qrtr-cfg $(STAGING_DIR)/usr/bin
#    $(INSTALL) -D -m 0755 $(@D)/qrtr-lookup $(STAGING_DIR)/usr/bin
#    cp $(@D)/libqrtr.so $(STAGING_DIR)/usr/lib
#    cp $(@D)/lib/libqrtr.h $(STAGING_DIR)/usr/include
#    ln -sf libqrtr.so $(STAGING_DIR)/usr/lib/libqrtr.so.1
#    ln -sf libqrtr.so.1 $(STAGING_DIR)/usr/lib/libqrtr.so.1.0
#endef

#define QRTR_INSTALL_TARGET_CMDS
#    $(INSTALL) -D -m 0755 $(@D)/qrtr-ns $(TARGET_DIR)/usr/bin
#    $(INSTALL) -D -m 0755 $(@D)/qrtr-cfg $(TARGET_DIR)/usr/bin
#    $(INSTALL) -D -m 0755 $(@D)/qrtr-lookup $(TARGET_DIR)/usr/bin
#    cp $(@D)/libqrtr.so $(TARGET_DIR)/usr/lib
#    ln -sf libqrtr.so $(TARGET_DIR)/usr/lib/libqrtr.so.1
#    ln -sf libqrtr.so.1 $(TARGET_DIR)/usr/lib/libqrtr.so.1.0
#endef

$(eval $(meson-package))
