################################################################################
#
# tqftpserv
#
################################################################################

# Commits on Sep 2, 2026
TQFTPSERV_VERSION = c2559a26098f6d2b36a946ef0b6ad02223264c3e
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

# meson.build needs a unit dir when systemd is absent; the units are
# not used with sysvinit
TQFTPSERV_CONF_OPTS = -Dsystemd-unit-prefix=/usr/lib/systemd/system

define TQFTPSERV_REMOVE_SYSTEMD_UNITS
	rm -f $(TARGET_DIR)/usr/lib/systemd/system/tqftpserv*.service
endef
TQFTPSERV_POST_INSTALL_TARGET_HOOKS += TQFTPSERV_REMOVE_SYSTEMD_UNITS

$(eval $(meson-package))
