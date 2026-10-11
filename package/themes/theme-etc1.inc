################################################################################
#
# Shared ETC1 compression hook for ES themes (GLES2 targets only)
#
# Loaded via external.mk. Usage in a theme .mk file:
#   $(eval $(call THEME_ETC1_HOOK,ES_THEME_CANVAS,es-theme-canvas))
#
################################################################################

# ETC1 compressed textures for GLES2 targets
define THEME_ETC1_HOOK
ifeq ($$(BR2_PACKAGE_HAS_LIBGLES),y)
$(1)_DEPENDENCIES += host-uberetc1 host-webp

define $(1)_COMPRESS_ETC1
	$$(BR2_EXTERNAL_REGLINUX_PATH)/scripts/linux/compress-theme-etc1.sh \
		$$(TARGET_DIR)/usr/share/regstation/themes/$(2) \
		$$(HOST_DIR)/bin/uberetc1 \
		$$(HOST_DIR)/bin/dwebp \
		100
endef

$(1)_POST_INSTALL_TARGET_HOOKS += $(1)_COMPRESS_ETC1
endif
endef
