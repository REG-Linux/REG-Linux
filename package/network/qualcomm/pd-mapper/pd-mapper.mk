################################################################################
#
# pd-mapper
#
################################################################################

# Commits on Nov 3, 2025
PD_MAPPER_VERSION = 0a43c8be564feae0493b6e24b2e3e98459a4f9b6
PD_MAPPER_SITE = $(call github,linux-msm,pd-mapper,$(PD_MAPPER_VERSION))
PD_MAPPER_LICENSE_FILE = LICENSE
PD_MAPPER_DEPENDENCIES = qrtr xz

define PD_MAPPER_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS) CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include" \
        LDFLAGS="$(TARGET_LDFLAGS) -L$(STAGING_DIR)/usr/lib -lqrtr -llzma" -C $(@D)
endef

define PD_MAPPER_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/pd-mapper $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
