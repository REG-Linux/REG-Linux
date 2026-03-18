################################################################################
#
# zftpd
#
################################################################################
ZFTPD_VERSION = v1.4.0
ZFTPD_SITE = $(call github,seregonwar,zftpd,$(ZFTPD_VERSION))
ZFTPD_LICENSE = MIT
ZFTPD_LICENSE_FILES = LICENSE

define ZFTPD_BUILD_CMDS
	$(SED) 's/-Werror//' $(@D)/Makefile
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/utils/zftpd/event_loop_epoll.c $(@D)/src/
	$(MAKE) -C $(@D) TARGET=linux CC="$(TARGET_CC)" ENABLE_ZHTTPD=1
endef

define ZFTPD_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 \
		$$(find $(@D)/build/linux -maxdepth 2 -name '*.elf' | head -1) \
		$(TARGET_DIR)/usr/bin/zftpd
endef

$(eval $(generic-package))
