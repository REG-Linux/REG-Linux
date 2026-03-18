################################################################################
#
# tegra-bsp
#
# NVIDIA Tegra BSP proprietary userspace libraries for L4T R32.3.1 (T210)
# Based on Lakka-LibreELEC's tegra-bsp package
#
################################################################################

TEGRA_BSP_VERSION = 32.3.1
TEGRA_BSP_SOURCE = Tegra210_Linux_R32.3.1_aarch64.tbz2
TEGRA_BSP_SITE = https://developer.nvidia.com/embedded/dlc/r32-3-1_Release_v1.0/t210ref_release_aarch64
TEGRA_BSP_LICENSE = NVIDIA Proprietary
TEGRA_BSP_LICENSE_FILES =
TEGRA_BSP_REDISTRIBUTE = NO
TEGRA_BSP_DEPENDENCIES = mesa3d libglvnd

# The BSP tarball contains a nv_tegra/ directory with sub-tarballs
define TEGRA_BSP_EXTRACT_CMDS
	$(TAR) xf $(TEGRA_BSP_DL_DIR)/$(TEGRA_BSP_SOURCE) -C $(@D)
endef

define TEGRA_BSP_INSTALL_TARGET_CMDS
	# Create working directory
	rm -rf $(@D)/target_install
	mkdir -p $(@D)/target_install
	cd $(@D)/target_install && \
	\
	# Extract BSP sub-archives
	tar xf $(@D)/nv_tegra/config.tbz2 && \
	tar xf $(@D)/nv_tegra/nvidia_drivers.tbz2 && \
	tar xf $(@D)/nv_tegra/nv_tools.tbz2 && \
	tar xf $(@D)/nv_tegra/nv_sample_apps/nvgstapps.tbz2 && \
	\
	# Move lib/* to usr/lib to avoid /lib symlink conflicts
	mv lib/* usr/lib/ && \
	rm -r lib && \
	\
	# Create symlinks from vendor-specific dirs to standard locations
	cd usr/lib/aarch64-linux-gnu/tegra && \
	for filename in *; do \
		if [ ! -h "$${filename}" ]; then \
			ln -sf aarch64-linux-gnu/tegra/$${filename} ../../$${filename}; \
		fi; \
	done && \
	cd ../tegra-egl && \
	for filename in *; do \
		if [ ! -h "$${filename}" ]; then \
			ln -sf aarch64-linux-gnu/tegra-egl/$${filename} ../../$${filename}; \
		fi; \
	done && \
	cd .. && \
	for filename in *; do \
		if [ ! -h "$${filename}" ]; then \
			ln -sf aarch64-linux-gnu/$${filename} ../$${filename}; \
		fi; \
	done && \
	cd ../../../ && \
	\
	# Remove unneeded files
	rm -rf usr/lib/ld.so.conf usr/lib/ubiquity \
		etc/systemd etc/NetworkManager etc/fstab etc/lightdm \
		etc/nv-oem-config.conf.t210 etc/skel etc/wpa_supplicant.conf \
		etc/enctune.conf etc/nv etc/nvphsd.conf etc/nvpmodel etc/xdg \
		etc/sysctl.d etc/hostname etc/hosts etc/modprobe.d etc/modules-load.d \
		var usr/lib/systemd usr/lib/nvidia usr/bin usr/sbin \
		usr/share/backgrounds usr/share/doc usr/share/nvpmodel_indicator \
		usr/share/polkit-1 opt && \
	\
	# Remove unneeded symlinks
	rm -f usr/lib/libv4l usr/lib/tegra usr/lib/tegra-egl usr/lib/nvidia.json && \
	\
	# Move udev rules from etc/ to usr/lib/
	if [ -d etc/udev ]; then \
		cp -PRv etc/udev usr/lib/; \
		rm -rf etc/udev; \
	fi && \
	\
	# Refresh symlinks
	cd usr/lib/ && \
	ln -sfn libcuda.so.1.1 libcuda.so && \
	ln -sfn libdrm.so.2 libdrm_nvdc.so && \
	ln -sfn libnvbufsurface.so.1.0.0 libnvbufsurface.so && \
	ln -sfn libnvbufsurftransform.so.1.0.0 libnvbufsurftransform.so && \
	ln -sfn libnvbuf_utils.so.1.0.0 libnvbuf_utils.so && \
	ln -sfn libnvdsbufferpool.so.1.0.0 libnvdsbufferpool.so && \
	ln -sfn libnvid_mapper.so.1.0.0 libnvid_mapper.so && \
	ln -sfn libnvv4l2.so libv4l2.so.0.0.999999 && \
	ln -sfn libnvv4lconvert.so libv4lconvert.so.0.0.999999 && \
	ln -sfn libv4l2.so.0.0.999999 libv4l2.so.0 && \
	ln -sfn libv4l2.so.0 libv4l2.so && \
	ln -sfn libv4lconvert.so.0.0.999999 libv4lconvert.so.0 && \
	ln -sfn libv4lconvert.so.0 libv4lconvert.so && \
	ln -sfn libnvgbm.so libgbm.so.1 && \
	ln -sfn libnvidia-egl-wayland.so libnvidia-egl-wayland.so.1 && \
	\
	# Fix Vulkan ICD path
	if [ -f aarch64-linux-gnu/tegra/nvidia_icd.json ]; then \
		sed -i 's:libGLX_nvidia.so.0:/usr/lib/libGLX_nvidia.so.0:g' \
			aarch64-linux-gnu/tegra/nvidia_icd.json; \
	fi && \
	\
	# Fix glvnd EGL vendor config
	sed -i 's:libEGL_nvidia.so.0:/usr/lib/libEGL_nvidia.so.0:g' \
		aarch64-linux-gnu/tegra-egl/nvidia.json && \
	rm -f ../share/glvnd/egl_vendor.d/* && \
	mv aarch64-linux-gnu/tegra-egl/nvidia.json \
		../share/glvnd/egl_vendor.d/10_nvidia.json && \
	\
	# Fix EGL external platform config
	if [ -f ../share/egl/egl_external_platform.d/nvidia_wayland.json ]; then \
		sed -i 's:libnvidia-egl-wayland.so.1:/usr/lib/libnvidia-egl-wayland.so.1:g' \
			../share/egl/egl_external_platform.d/nvidia_wayland.json; \
	fi && \
	\
	# Setup firmware symlinks
	cd firmware && \
	rm -rf gm20b && \
	ln -sfn tegra21x gm20b && \
	cd tegra21x && \
	if [ -f nv_acr_ucode_prod.bin ]; then \
		ln -sfn nv_acr_ucode_prod.bin acr_ucode.bin; \
	fi && \
	cd ../../../../ && \
	\
	# Setup Vulkan ICD
	if [ -d etc/vulkan/icd.d ]; then \
		cd etc/vulkan/icd.d && \
		rm -f nvidia_icd.json && \
		ln -sfn /usr/lib/nvidia_icd.json nvidia_icd.json && \
		cd ../../../; \
	fi && \
	\
	# Setup ALSA config
	cd etc && \
	ln -sfn asound.conf.tegrasndt210ref asound.conf && \
	cd .. && \
	\
	# Install everything to target
	cp -PRv $(@D)/target_install/* $(TARGET_DIR)/ && \
	\
	# Remove Mesa's libgbm.so.1 - tegra-bsp provides its own via libnvgbm
	rm -f $(TARGET_DIR)/usr/lib/libgbm.so.1 && \
	\
	# Remove Mesa's libdrm.so.2 - tegra-bsp provides its own
	rm -f $(TARGET_DIR)/usr/lib/libdrm.so.2
endef

$(eval $(generic-package))
