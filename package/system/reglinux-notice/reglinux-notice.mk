################################################################################
#
# REG-Linux notice
#
################################################################################
REGLINUX_NOTICE_SOURCE =

define REGLINUX_NOTICE_INSTALL_TARGET_CMDS
    $(INSTALL) -m 0644 -D $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-notice/notice.pdf $(TARGET_DIR)/usr/share/reglinux/doc/notice.pdf
endef

$(eval $(generic-package))
