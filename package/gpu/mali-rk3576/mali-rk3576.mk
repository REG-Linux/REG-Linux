################################################################################
#
# mali-rk3576
#
# Mali Bifrost G52 MC3 (g24p0) userspace libraries for Rockchip RK3576
# Extracted from Anbernic RG Vita Pro BSP (kernel 6.1.99)
#
################################################################################

MALI_RK3576_VERSION = 1.0
MALI_RK3576_SITE_METHOD = local
MALI_RK3576_SITE = $(BR2_EXTERNAL_REGLINUX_PATH)/package/gpu/mali-rk3576/files
MALI_RK3576_INSTALL_STAGING = YES
MALI_RK3576_PROVIDES = libegl libgles libgbm
MALI_RK3576_LICENSE = Rockchip End User Licence Agreement
MALI_RK3576_DEPENDENCIES = wayland libdrm

define MALI_RK3576_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig $(STAGING_DIR)/usr/include

	# Headers
	cp -rf $(@D)/include/* $(STAGING_DIR)/usr/include/

	# Main Mali blob
	$(INSTALL) -D -m 0755 $(@D)/lib/libmali.so.1.9.0 $(STAGING_DIR)/usr/lib/libmali.so.1.9.0
	ln -sf libmali.so.1.9.0 $(STAGING_DIR)/usr/lib/libmali.so.1
	ln -sf libmali.so.1 $(STAGING_DIR)/usr/lib/libmali.so

	# Hook lib
	$(INSTALL) -D -m 0755 $(@D)/lib/libmali-hook.so.1.9.0 $(STAGING_DIR)/usr/lib/libmali-hook.so.1.9.0
	ln -sf libmali-hook.so.1.9.0 $(STAGING_DIR)/usr/lib/libmali-hook.so.1
	ln -sf libmali-hook.so.1 $(STAGING_DIR)/usr/lib/libmali-hook.so

	# API symlinks (all point to libmali.so)
	ln -sf libmali.so.1 $(STAGING_DIR)/usr/lib/libEGL.so.1
	ln -sf libEGL.so.1 $(STAGING_DIR)/usr/lib/libEGL.so
	ln -sf libmali.so.1 $(STAGING_DIR)/usr/lib/libGLESv1_CM.so.1
	ln -sf libGLESv1_CM.so.1 $(STAGING_DIR)/usr/lib/libGLESv1_CM.so
	ln -sf libmali.so.1 $(STAGING_DIR)/usr/lib/libGLESv2.so.2
	ln -sf libGLESv2.so.2 $(STAGING_DIR)/usr/lib/libGLESv2.so
	ln -sf libmali.so.1 $(STAGING_DIR)/usr/lib/libgbm.so.1
	ln -sf libgbm.so.1 $(STAGING_DIR)/usr/lib/libgbm.so
	ln -sf libmali.so.1 $(STAGING_DIR)/usr/lib/libwayland-egl.so.1
	ln -sf libwayland-egl.so.1 $(STAGING_DIR)/usr/lib/libwayland-egl.so
	ln -sf libmali.so.1 $(STAGING_DIR)/usr/lib/libOpenCL.so.1
	ln -sf libOpenCL.so.1 $(STAGING_DIR)/usr/lib/libOpenCL.so
	ln -sf libmali.so.1.9.0 $(STAGING_DIR)/usr/lib/libMaliVulkan.so.1
	ln -sf libMaliVulkan.so.1 $(STAGING_DIR)/usr/lib/libMaliVulkan.so
	ln -sf libmali.so.1 $(STAGING_DIR)/usr/lib/libmali-bifrost-g52-g24p0-wayland-gbm.so

	# pkg-config files
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_REGLINUX_PATH)/package/gpu/mali-rk3576/egl.pc \
		$(STAGING_DIR)/usr/lib/pkgconfig/egl.pc
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_REGLINUX_PATH)/package/gpu/mali-rk3576/glesv2.pc \
		$(STAGING_DIR)/usr/lib/pkgconfig/glesv2.pc
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_REGLINUX_PATH)/package/gpu/mali-rk3576/gbm.pc \
		$(STAGING_DIR)/usr/lib/pkgconfig/gbm.pc
endef

define MALI_RK3576_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib $(TARGET_DIR)/usr/include

	# Headers
	cp -rf $(@D)/include/* $(TARGET_DIR)/usr/include/

	# Main Mali blob
	$(INSTALL) -D -m 0755 $(@D)/lib/libmali.so.1.9.0 $(TARGET_DIR)/usr/lib/libmali.so.1.9.0
	ln -sf /usr/lib/libmali.so.1.9.0 $(TARGET_DIR)/usr/lib/libmali.so.1
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libmali.so

	# Hook lib
	$(INSTALL) -D -m 0755 $(@D)/lib/libmali-hook.so.1.9.0 $(TARGET_DIR)/usr/lib/libmali-hook.so.1.9.0
	ln -sf /usr/lib/libmali-hook.so.1.9.0 $(TARGET_DIR)/usr/lib/libmali-hook.so.1
	ln -sf /usr/lib/libmali-hook.so.1 $(TARGET_DIR)/usr/lib/libmali-hook.so

	# API symlinks (all point to libmali.so)
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libEGL.so.1
	ln -sf /usr/lib/libEGL.so.1 $(TARGET_DIR)/usr/lib/libEGL.so
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libGLESv1_CM.so.1
	ln -sf /usr/lib/libGLESv1_CM.so.1 $(TARGET_DIR)/usr/lib/libGLESv1_CM.so
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libGLESv2.so.2
	ln -sf /usr/lib/libGLESv2.so.2 $(TARGET_DIR)/usr/lib/libGLESv2.so
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libgbm.so.1
	ln -sf /usr/lib/libgbm.so.1 $(TARGET_DIR)/usr/lib/libgbm.so
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libwayland-egl.so.1
	ln -sf /usr/lib/libwayland-egl.so.1 $(TARGET_DIR)/usr/lib/libwayland-egl.so
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libOpenCL.so.1
	ln -sf /usr/lib/libOpenCL.so.1 $(TARGET_DIR)/usr/lib/libOpenCL.so
	ln -sf /usr/lib/libmali.so.1.9.0 $(TARGET_DIR)/usr/lib/libMaliVulkan.so.1
	ln -sf /usr/lib/libMaliVulkan.so.1 $(TARGET_DIR)/usr/lib/libMaliVulkan.so
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libmali-bifrost-g52-g24p0-wayland-gbm.so

	# Mali CSF firmware
	mkdir -p $(TARGET_DIR)/lib/firmware/arm/mali/arch10.8
	$(INSTALL) -D -m 0644 $(@D)/firmware/arm/mali/arch10.8/mali_csffw.bin \
		$(TARGET_DIR)/lib/firmware/arm/mali/arch10.8/mali_csffw.bin
endef

# Force Mali symlinks AFTER all packages (wayland overwrites libwayland-egl.so.1)
define MALI_RK3576_FIXUP_SYMLINKS
	ln -sf /usr/lib/libmali.so.1.9.0 $(TARGET_DIR)/usr/lib/libmali.so.1
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libEGL.so.1
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libGLESv1_CM.so.1
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libGLESv2.so.2
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libgbm.so.1
	ln -sf /usr/lib/libmali.so.1 $(TARGET_DIR)/usr/lib/libwayland-egl.so.1
endef
MALI_RK3576_TARGET_FINALIZE_HOOKS += MALI_RK3576_FIXUP_SYMLINKS

$(eval $(generic-package))
