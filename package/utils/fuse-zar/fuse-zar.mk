################################################################################
#
# FUSE ZArchive mounter
#
################################################################################

FUSE_ZAR_VERSION = master
FUSE_ZAR_SITE = $(call github,REG-Linux,fuse-zar,$(FUSE_ZAR_VERSION))
FUSE_ZAR_LICENSE = GPL-3.0
FUSE_ZAR_DEPENDENCIES += zstd libfuse3

FUSE_ZAR_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

define FUSE_ZAR_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D $(@D)/fuse-zar $(TARGET_DIR)/usr/bin/fuse-zar
	$(INSTALL) -D $(@D)/zarchive/zarchive $(TARGET_DIR)/usr/bin/zarchive
endef

$(eval $(cmake-package))
