################################################################################
#
# rmtfs
#
################################################################################

# Commits on Sep 26, 2025
RMTFS_VERSION = f7566e4c8262c618c09173b93282bec6a340663c
RMTFS_SITE = $(call github,linux-msm,rmtfs,$(RMTFS_VERSION))
RMTFS_LICENSE = BSD-3-Clause license
RMTFS_LICENSE_FILE = LICENSE
RMTFS_DEPENDENCIES = qrtr eudev
RMTFS_INSTALL_STAGING = YES

define RMTFS_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS)  \
        CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include" \
        LDFLAGS="$(TARGET_LDFLAGS) -L$(STAGING_DIR)/usr/lib -lqrtr -ludev -lpthread" -C $(@D)
endef

define RMTFS_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/rmtfs $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
