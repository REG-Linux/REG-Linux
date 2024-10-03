################################################################################
#
# xxd
#
################################################################################
# Version.: Commits on Feb 19, 2024
XXD_VERSION = v1.1
XXD_SITE =  $(call github,ckormanyos,xxd,$(XXD_VERSION))
XXD_LICENSE = GPL-2.0
XXD_LICENSE_FILE = LICENSE

define XXD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/xxd	$(TARGET_DIR)/usr/bin/xxd
endef

$(eval $(cmake-package))

define HOST_XXD_INSTALL_CMDS
	$(INSTALL) -D $(@D)/xxd	$(HOST_DIR)/usr/bin/xxd
endef

$(eval $(host-cmake-package))
