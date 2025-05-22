################################################################################
#
# uMTP-responder
#
################################################################################
UMTP_RESPONDER_VERSION = umtprd-1.6.8
UMTP_RESPONDER_SITE = $(call github,viveris,uMTP-Responder,$(UMTP_RESPONDER_VERSION))
UMTP_RESPONDER_DEPENDENCIES = libusb libglib2 inih

define UMTP_RESPONDER_BUILD_CMDS
	cd $(@D) && make -f Makefile CC=$(TARGET_CC)
endef

define UMTP_RESPONDER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/etc/umtprd
	$(INSTALL) -D $(@D)/umtprd $(TARGET_DIR)/usr/bin/umtprd
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/utils/umtp-responder/umtprd.conf $(TARGET_DIR)/etc/umtprd
endef

$(eval $(generic-package))
