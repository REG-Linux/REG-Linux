################################################################################
#
# nvidia470-legacy-driver
#
################################################################################

NVIDIA470_LEGACY_DRIVER_VERSION = 470.256.02
NVIDIA470_LEGACY_DRIVER_SUFFIX = $(if $(BR2_x86_64),_64)
NVIDIA470_LEGACY_DRIVER_SITE = \
    http://download.nvidia.com/XFree86/Linux-x86$(NVIDIA470_LEGACY_DRIVER_SUFFIX)/$(NVIDIA470_LEGACY_DRIVER_VERSION)
NVIDIA470_LEGACY_DRIVER_SOURCE = \
    NVIDIA-Linux-x86$(NVIDIA470_LEGACY_DRIVER_SUFFIX)-$(NVIDIA470_LEGACY_DRIVER_VERSION).run
NVIDIA470_LEGACY_DRIVER_LICENSE = NVIDIA Software License
NVIDIA470_LEGACY_DRIVER_LICENSE_FILES = LICENSE
NVIDIA470_LEGACY_DRIVER_REDISTRIBUTE = NO
NVIDIA470_LEGACY_DRIVER_INSTALL_STAGING = YES
NVIDIA470_LEGACY_DRIVER_EXTRACT_DEPENDENCIES = host-xz

# The userspace libraries below are NOT X.org-specific: REG-Linux runs a Wayland
# compositor and reaches the GPU through libglvnd (EGL/GLES), GBM and Vulkan.
# libGLX_nvidia in particular carries NVIDIA's Vulkan ICD, which nvidia_icd.json
# points at, so it is required even with no X server at all. Keeping these lists
# behind the X.org conditional left the target with no NVIDIA userspace whatsoever
# while system-drivers-nvidia still expected to find and symlink them at runtime.

# Since nvidia-driver are binary blobs, the below dependencies are not
# strictly speaking build dependencies of nvidia-driver. However, they
# are build dependencies of packages that depend on nvidia-driver, so
# they should be built prior to those packages, and the only simple
# way to do so is to make nvidia-driver depend on them.
#batocera enable nvidia-driver and mesa3d to coexist in the same fs
NVIDIA470_LEGACY_DRIVER_DEPENDENCIES = mesa3d xlib_libX11 xlib_libXext libglvnd kmod
# NVIDIA470_LEGACY_DRIVER_PROVIDES = libgl libegl libgles

# batocera modified to suport the vendor-neutral "dispatching" API/ABI
#   https://github.com/aritger/linux-opengl-abi-proposal/blob/master/linux-opengl-abi-proposal.txt
#batocera generic GL libraries are provided by libglvnd
#batocera only vendor version are installed
NVIDIA470_LEGACY_DRIVER_LIBS_GL = \
	libGLX_nvidia.so.$(NVIDIA470_LEGACY_DRIVER_VERSION)

NVIDIA470_LEGACY_DRIVER_LIBS_EGL = \
	libEGL_nvidia.so.$(NVIDIA470_LEGACY_DRIVER_VERSION)

NVIDIA470_LEGACY_DRIVER_LIBS_GLES = \
	libGLESv1_CM_nvidia.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libGLESv2_nvidia.so.$(NVIDIA470_LEGACY_DRIVER_VERSION)

#batocera libnvidia-egl-wayland soname bump
NVIDIA470_LEGACY_DRIVER_LIBS_MISC = \
	libnvidia-eglcore.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libnvidia-glcore.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libnvidia-glsi.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libnvidia-tls.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libnvidia-ml.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libnvidia-glvkspirv.so.$(NVIDIA470_LEGACY_DRIVER_VERSION)

NVIDIA470_LEGACY_DRIVER_LIBS += \
	$(NVIDIA470_LEGACY_DRIVER_LIBS_GL) \
	$(NVIDIA470_LEGACY_DRIVER_LIBS_EGL) \
	$(NVIDIA470_LEGACY_DRIVER_LIBS_GLES) \
	$(NVIDIA470_LEGACY_DRIVER_LIBS_MISC)

# batocera 32bit libraries (only usable with a 32-bit runtime; see
# BR2_PACKAGE_REGLINUX_NVIDIA_32BIT)
ifeq ($(BR2_PACKAGE_REGLINUX_NVIDIA_32BIT),y)
NVIDIA470_LEGACY_DRIVER_32 = \
	$(NVIDIA470_LEGACY_DRIVER_LIBS_GL) \
	$(NVIDIA470_LEGACY_DRIVER_LIBS_EGL) \
	$(NVIDIA470_LEGACY_DRIVER_LIBS_GLES) \
	$(NVIDIA470_LEGACY_DRIVER_LIBS_MISC)
endif

# Install the gl.pc file
define NVIDIA470_LEGACY_DRIVER_INSTALL_GL_DEV
	$(INSTALL) -D -m 0644 $(@D)/libGL.la $(STAGING_DIR)/usr/lib/libGL.la
	$(SED) 's:__GENERATED_BY__:Buildroot:' $(STAGING_DIR)/usr/lib/libGL.la
	$(SED) 's:__LIBGL_PATH__:/usr/lib:' $(STAGING_DIR)/usr/lib/libGL.la
	$(SED) 's:-L[^[:space:]]\+::' $(STAGING_DIR)/usr/lib/libGL.la
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_REGLINUX_PATH)/package/nvidia-driver/gl.pc $(STAGING_DIR)/usr/lib/pkgconfig/gl.pc
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_REGLINUX_PATH)/package/nvidia-driver/egl.pc $(STAGING_DIR)/usr/lib/pkgconfig/egl.pc
endef

# Those libraries are 'private' libraries requiring an agreement with
# NVidia to develop code for those libs. There seems to be no restriction
# on using those libraries (e.g. if the user has such an agreement, or
# wants to run a third-party program developped under such an agreement).
ifeq ($(BR2_PACKAGE_NVIDIA470_LEGACY_DRIVER_PRIVATE_LIBS),y)
NVIDIA470_LEGACY_DRIVER_LIBS += \
	libnvidia-ifr.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libnvidia-fbc.so.$(NVIDIA470_LEGACY_DRIVER_VERSION)
endif

# We refer to the destination path; the origin file has no directory component
# batocera libnvidia-wfb removed in 418.43
NVIDIA470_LEGACY_DRIVER_X_MODS = \
	/nvidia_drv.so
#	libnvidia-wfb.so.$(NVIDIA470_LEGACY_DRIVER_VERSION)

ifeq ($(BR2_PACKAGE_NVIDIA470_LEGACY_DRIVER_CUDA),y)
NVIDIA470_LEGACY_DRIVER_LIBS += \
	libcuda.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libnvidia-compiler.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libnvcuvid.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libnvidia-fatbinaryloader.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libnvidia-ptxjitcompiler.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	libnvidia-encode.so.$(NVIDIA470_LEGACY_DRIVER_VERSION)
ifeq ($(BR2_PACKAGE_NVIDIA470_LEGACY_DRIVER_CUDA_PROGS),y)
NVIDIA470_LEGACY_DRIVER_PROGS = nvidia-cuda-mps-control nvidia-cuda-mps-server
endif
endif

ifeq ($(BR2_PACKAGE_NVIDIA470_LEGACY_DRIVER_OPENCL),y)
NVIDIA470_LEGACY_DRIVER_LIBS += \
	libOpenCL.so.1.0.0 \
	libnvidia-opencl.so.$(NVIDIA470_LEGACY_DRIVER_VERSION)
NVIDIA470_LEGACY_DRIVER_DEPENDENCIES += mesa3d-headers
NVIDIA470_LEGACY_DRIVER_PROVIDES += libopencl
endif

# Build and install the kernel modules if needed
ifeq ($(BR2_PACKAGE_NVIDIA470_LEGACY_DRIVER_MODULE),y)

NVIDIA470_LEGACY_DRIVER_MODULES = nvidia nvidia-modeset nvidia-drm
ifeq ($(BR2_x86_64),y)
NVIDIA470_LEGACY_DRIVER_MODULES += nvidia-uvm
endif

# They can't do everything like everyone. They need those variables,
# because they don't recognise the usual variables set by the kernel
# build system. We also need to tell them what modules to build.
NVIDIA470_LEGACY_DRIVER_MODULE_MAKE_OPTS = \
	NV_KERNEL_SOURCES="$(LINUX_DIR)" \
	NV_KERNEL_OUTPUT="$(LINUX_DIR)" \
	NV_KERNEL_MODULES="$(NVIDIA470_LEGACY_DRIVER_MODULES)" \
	IGNORE_CC_MISMATCH="1" \
	NV_SPECTRE_V2="0"

NVIDIA470_LEGACY_DRIVER_MODULE_SUBDIRS = kernel

$(eval $(kernel-module))

endif # NVIDIA470_LEGACY_DRIVER_MODULE == y

# The downloaded archive is in fact an auto-extract script. So, it can run
# virtually everywhere, and it is fine enough to provide useful options.
# Except it can't extract into an existing (even empty) directory.
define NVIDIA470_LEGACY_DRIVER_EXTRACT_CMDS
	PATH="$(HOST_DIR)/bin:$(PATH)" $(SHELL) $(NVIDIA470_LEGACY_DRIVER_DL_DIR)/$(NVIDIA470_LEGACY_DRIVER_SOURCE) \
		--extract-only --target $(@D)/tmp-extract
	chmod u+w -R $(@D)
	mv $(@D)/tmp-extract/* $(@D)/tmp-extract/.manifest $(@D)
	rm -rf $(@D)/tmp-extract
endef

# Helper to install libraries
# $1: destination directory (target or staging)
#
define NVIDIA470_LEGACY_DRIVER_INSTALL_LIBS
	$(foreach lib,$(NVIDIA470_LEGACY_DRIVER_LIBS),\
		$(INSTALL) -D -m 0644 $(@D)/$(lib) $(1)/usr/lib/nvidia-470-legacy/$(notdir $(lib))
		libsoname="$$( $(TARGET_READELF) -d "$(@D)/$(lib)" \
			|sed -r -e '/.*\(SONAME\).*\[(.*)\]$$/!d; s//\1/;' )"; \
		if [ -n "$${libsoname}" -a "$${libsoname}" != "$(notdir $(lib))" ]; then \
			ln -sf $(notdir $(lib)) \
				$(1)/usr/lib/nvidia-470-legacy/$${libsoname}; \
		fi
		baseso=$(firstword $(subst .,$(space),$(notdir $(lib)))).so; \
		if [ -n "$${baseso}" -a "$${baseso}" != "$(notdir $(lib))" ]; then \
			ln -sf $(notdir $(lib)) $(1)/usr/lib/nvidia-470-legacy/$${baseso}; \
		fi
	)
endef

# batocera install 32bit libraries
define NVIDIA470_LEGACY_DRIVER_INSTALL_32
	$(foreach lib,$(NVIDIA470_LEGACY_DRIVER_32),\
		$(INSTALL) -D -m 0644 $(@D)/32/$(lib) $(1)/lib32/nvidia-470-legacy/$(notdir $(lib))
		libsoname="$$( $(TARGET_READELF) -d "$(@D)/32/$(lib)" \
			|sed -r -e '/.*\(SONAME\).*\[(.*)\]$$/!d; s//\1/;' )"; \
		if [ -n "$${libsoname}" -a "$${libsoname}" != "$(notdir $(lib))" ]; then \
			ln -sf $(notdir $(lib)) \
				$(1)/lib32/nvidia-470-legacy/$${libsoname}; \
		fi
		baseso=$(firstword $(subst .,$(space),$(notdir $(lib)))).so; \
		if [ -n "$${baseso}" -a "$${baseso}" != "$(notdir $(lib))" ]; then \
			ln -sf $(notdir $(lib)) $(1)/lib32/nvidia-470-legacy/$${baseso}; \
		fi
	)
endef

# batocera nvidia libs are runtime linked via libglvnd
# For staging, install libraries and development files
# define NVIDIA470_LEGACY_DRIVER_INSTALL_STAGING_CMDS
# 	$(call NVIDIA470_LEGACY_DRIVER_INSTALL_LIBS,$(STAGING_DIR))
# 	$(NVIDIA470_LEGACY_DRIVER_INSTALL_GL_DEV)
# endef

# For target, install libraries and X.org modules
define NVIDIA470_LEGACY_DRIVER_INSTALL_TARGET_CMDS
	$(call NVIDIA470_LEGACY_DRIVER_INSTALL_LIBS,$(TARGET_DIR))
	$(call NVIDIA470_LEGACY_DRIVER_INSTALL_32,$(TARGET_DIR))
	$(INSTALL) -D -m 0644 $(@D)/nvidia_drv.so \
			$(TARGET_DIR)/usr/lib/xorg/modules/drivers/nvidia_legacy_drv.so
	$(foreach p,$(NVIDIA470_LEGACY_DRIVER_PROGS), \
		$(INSTALL) -D -m 0755 $(@D)/$(p) \
			$(TARGET_DIR)/usr/bin/$(p)
	)
	$(NVIDIA470_LEGACY_DRIVER_INSTALL_KERNEL_MODULE)

# batocera install files needed by Vulkan
	$(INSTALL) -D -m 0644 $(@D)/nvidia_layers.json \
		$(TARGET_DIR)/usr/share/vulkan/implicit_layer.d/nvidia470_legacy_layers.json

# batocera install files needed by libglvnd
	$(INSTALL) -D -m 0644 $(@D)/10_nvidia.json \
		$(TARGET_DIR)/usr/share/glvnd/egl_vendor.d/10_nvidia470_legacy.json

	mkdir -p $(TARGET_DIR)/usr/share/nvidia
	mkdir -p $(TARGET_DIR)/usr/share/nvidia/X11
	$(INSTALL) -D -m 0644 $(@D)/nvidia-drm-outputclass.conf \
		$(TARGET_DIR)/usr/share/nvidia/X11/10-nvidia470-legacy-drm-outputclass.conf

	$(INSTALL) -D -m 0644 $(@D)/libglxserver_nvidia.so.$(NVIDIA470_LEGACY_DRIVER_VERSION) \
	 	$(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglxserver_nvidia.so.$(NVIDIA470_LEGACY_DRIVER_VERSION)

# firmware
    mkdir -p $(TARGET_DIR)/lib/firmware/nvidia/$(NVIDIA470_LEGACY_DRIVER_VERSION)
	$(INSTALL) -D -m 0644 $(@D)/firmware/* $(TARGET_DIR)/lib/firmware/nvidia/$(NVIDIA470_LEGACY_DRIVER_VERSION)

endef

define NVIDIA470_LEGACY_DRIVER_VULKANJSON_X86_64
    mkdir -p $(TARGET_DIR)/usr/share/vulkan/nvidia
	$(INSTALL) -D -m 0644 $(@D)/nvidia_icd.json $(TARGET_DIR)/usr/share/vulkan/nvidia/nvidia470_legacy_icd.x86_64.json
        sed -i -e s+'"library_path": "libGLX_nvidia'+'"library_path": "/var/run/nvidia/lib/libGLX_nvidia'+ $(TARGET_DIR)/usr/share/vulkan/nvidia/nvidia470_legacy_icd.x86_64.json
endef

# The i686 ICD names /lib32/libGLX_nvidia, so it is only meaningful
# when the 32-bit libraries are installed.
define NVIDIA470_LEGACY_DRIVER_VULKANJSON_I686
    mkdir -p $(TARGET_DIR)/usr/share/vulkan/nvidia
	$(INSTALL) -D -m 0644 $(@D)/nvidia_icd.json $(TARGET_DIR)/usr/share/vulkan/nvidia/nvidia470_legacy_icd.i686.json
        sed -i -e s+'"library_path": "libGLX_nvidia'+'"library_path": "/var/run/nvidia/lib32/libGLX_nvidia'+ $(TARGET_DIR)/usr/share/vulkan/nvidia/nvidia470_legacy_icd.i686.json
endef

ifeq ($(BR2_x86_64),y)
	NVIDIA470_LEGACY_DRIVER_POST_INSTALL_TARGET_HOOKS += NVIDIA470_LEGACY_DRIVER_VULKANJSON_X86_64
endif
ifeq ($(BR2_x86_64)$(BR2_PACKAGE_REGLINUX_NVIDIA_32BIT),yy)
	NVIDIA470_LEGACY_DRIVER_POST_INSTALL_TARGET_HOOKS += NVIDIA470_LEGACY_DRIVER_VULKANJSON_I686
endif

# move to avoid the production driver
# Note: kernel modules may be compressed (.ko.zst) by Buildroot
define NVIDIA470_LEGACY_DRIVER_RENAME_KERNEL_MODULES
    mkdir -p $(TARGET_DIR)/usr/share/nvidia
	mkdir -p $(TARGET_DIR)/usr/share/nvidia/modules
	# rename the kernel modules to avoid conflict (handle both .ko and .ko.zst)
	if [ -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia.ko.zst ]; then \
		mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia.ko.zst \
		    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia470-legacy.ko.zst; \
	elif [ -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia.ko ]; then \
		mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia.ko \
		    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia470-legacy.ko; \
	fi
	if [ -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-modeset.ko.zst ]; then \
		mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-modeset.ko.zst \
		    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia470-modeset-legacy.ko.zst; \
	elif [ -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-modeset.ko ]; then \
		mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-modeset.ko \
		    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia470-modeset-legacy.ko; \
	fi
	if [ -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-drm.ko.zst ]; then \
		mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-drm.ko.zst \
		    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia470-drm-legacy.ko.zst; \
	elif [ -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-drm.ko ]; then \
		mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-drm.ko \
		    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia470-drm-legacy.ko; \
	fi
	if [ -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-uvm.ko.zst ]; then \
		mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-uvm.ko.zst \
		    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia470-uvm-legacy.ko.zst; \
	elif [ -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-uvm.ko ]; then \
		mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-uvm.ko \
		    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia470-uvm-legacy.ko; \
	fi
	# set the driver version file
	echo $(NVIDIA470_LEGACY_DRIVER_VERSION) > $(TARGET_DIR)/usr/share/nvidia/legacy470.version
endef

NVIDIA470_LEGACY_DRIVER_POST_INSTALL_TARGET_HOOKS += NVIDIA470_LEGACY_DRIVER_RENAME_KERNEL_MODULES

$(eval $(generic-package))
