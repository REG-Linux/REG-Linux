################################################################################
#
# xa
#
################################################################################

XA_VERSION = xa-2.4.1
XA_SITE = $(call github,fachat,xa65,$(XA_VERSION))

define HOST_XA_BUILD_CMDS
	$(HOST_MAKE_ENV) $(MAKE) -C $(@D)/xa -f Makefile
endef

define HOST_XA_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(@D)/xa/xa $(HOST_DIR)/usr/bin/xa ;
endef

$(eval $(host-generic-package))
