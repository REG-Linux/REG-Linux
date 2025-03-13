################################################################################
#
# reglinux-test
#
################################################################################
REGLINUX_TEST_VERSION = 0.1
REGLINUX_TEST_LICENSE = GPL
REGLINUX_TEST_SOURCE=
REGLINUX_TEST_DEPENDENCIES = python-requests

define REGLINUX_TEST_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-test/src/reglinux-test $(TARGET_DIR)/usr/bin/reglinux-test
endef

$(eval $(generic-package))
