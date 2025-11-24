################################################################################
#
# tqftpserv
#
################################################################################

# Commits on Aug 1, 2025
TQFTPSERV_VERSION = 408ca1ed5e4e0a9ac3650b13d3f3c60079b3e2a3
TQFTPSERV_SITE = $(call github,linux-msm,tqftpserv,$(TQFTPSERV_VERSION))
TQFTPSERV_LICENSE = BSD-3-Clause license
TQFTPSERV_LICENSE_FILE = LICENSE
TQFTPSERV_DEPENDENCIES = qrtr zstd

#define TQFTPSERV_BUILD_CMDS
#    $(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS) CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include" \
#        LDFLAGS="$(TARGET_LDFLAGS) -L$(STAGING_DIR)/usr/lib -lqrtr" -C $(@D)
#endef

#define TQFTPSERV_INSTALL_TARGET_CMDS
#    $(INSTALL) -D -m 0755 $(@D)/tqftpserv $(TARGET_DIR)/usr/bin
#endef

$(eval $(meson-package))
