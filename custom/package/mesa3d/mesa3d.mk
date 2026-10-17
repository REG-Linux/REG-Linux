################################################################################
#
# mesa3d
#
################################################################################

MESA3D_VERSION = 26.2.4
MESA3D_SOURCE = mesa-$(MESA3D_VERSION).tar.xz
MESA3D_SITE = https://archive.mesa3d.org

MESA3D_LICENSE = MIT, SGI, Khronos
MESA3D_LICENSE_FILES = docs/license.rst
MESA3D_CPE_ID_VENDOR = mesa3d
MESA3D_CPE_ID_PRODUCT = mesa

MESA3D_INSTALL_STAGING = YES

MESA3D_PROVIDES =

MESA3D_DEPENDENCIES = \
	host-bison \
	host-flex \
	host-python-mako \
	expat \
	libdrm \
	zlib \
	host-python3 \
	host-python-pyyaml

# Build mesa3d host-side for clc compilers (needed by x86, asahi, panfrost, imagination, opencl)
#MESA3D_NEEDS_HOST_MESA3D = $(or $(BR2_x86_64),$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_ASAHI),$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_PANFROST),$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_IMAGINATION),$(BR2_PACKAGE_MESA3D_OPENCL))
#ifneq ($(MESA3D_NEEDS_HOST_MESA3D),)
MESA3D_DEPENDENCIES += host-mesa3d
#endif

# need host-python-pycparser built for etnaviv
ifeq ($(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_ETNAVIV),y)
MESA3D_DEPENDENCIES += host-python-pycparser
endif

# directx-headers
ifeq ($(BR2_PACKAGE_DIRECTX_HEADERS),y)
MESA3D_DEPENDENCIES += directx-headers
endif

# update
ifeq ($(BR2_PACKAGE_MESA3D_DRIVER)$(BR2_PACKAGE_XORG7),yy)
MESA3D_DEPENDENCIES += xlib_libxshmfence host-glslang
endif

ifeq ($(BR2_PACKAGE_MESA3D_LLVM),y)
MESA3D_DEPENDENCIES += llvm
MESA3D_MESON_EXTRA_BINARIES += llvm-config='$(STAGING_DIR)/usr/bin/llvm-config'
MESA3D_CONF_OPTS += -Dllvm=enabled
ifeq ($(BR2_PACKAGE_LLVM_RTTI),y)
MESA3D_CONF_OPTS += -Dcpp_rtti=true
else
MESA3D_CONF_OPTS += -Dcpp_rtti=false
endif
else
# Avoid automatic search of llvm-config
MESA3D_CONF_OPTS += -Dllvm=disabled
endif

# Disable opencl-icd: OpenCL lib will be named libOpenCL instead of
# libMesaOpenCL and CL headers are installed
ifeq ($(BR2_PACKAGE_MESA3D_OPENCL),y)
MESA3D_PROVIDES += libopencl
MESA3D_DEPENDENCIES += clang libclc
MESA3D_CONF_OPTS += -Dgallium-rusticl=true
endif

# prebuilt compilers from host-mesa3d - but only where host-mesa3d actually
# installs them, see HOST_MESA3D_CONF_OPTS below. Asking for =system elsewhere
# points meson at compilers that were never built. Omitting the options leaves
# them at their meson default of 'auto' ('disabled' is not a valid choice).
ifeq ($(BR2_PACKAGE_LLVM_ARCH_SUPPORTS),y)
MESA3D_CONF_OPTS += -Dmesa-clc=system -Dprecomp-compiler=system
endif

# x86 builds require clang libclc and python-ply, rely on system (host) intel_clc
ifeq ($(BR2_x86_64),y)
MESA3D_DEPENDENCIES += clang libclc host-python-ply
endif

# panvk needs libclc, llvm and spirv-llvm-translator
ifeq ($(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_PANFROST),y)
MESA3D_DEPENDENCIES += libclc spirv-llvm-translator spirv-tools
endif

# imagination needs libclc, llvm and spirv-llvm-translator
ifeq ($(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_IMAGINATION),y)
MESA3D_DEPENDENCIES += libclc spirv-llvm-translator spirv-tools
endif

# asahi needs libclc spirv-tools
# specify extra binaries to cross-compile asahi clc
ifeq ($(BR2_x86_64)$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_ASAHI),y)
MESA3D_DEPENDENCIES += libclc spirv-tools spirv-llvm-translator clang host-glslang
endif

# spirv-tools is a meson `feature`, so leaving it unset means auto: meson takes
# SPIRV-Tools if pkg-config finds it, whether or not buildroot asked for it, and
# libgallium then carries a NEEDED on libSPIRV-Tools.so. On a board that never
# enabled the target package nothing installs that library, so every GL client
# dies at load time and the device boots to a black screen - which is what a
# stray SPIRV-Tools.pc in the sysroot did to cha. Say what we mean, and depend
# on the package here rather than relying on the per-driver blocks above to
# have named it (BR2_PACKAGE_SPIRV_TOOLS is also selected for plain x86_64,
# where none of them fires).
ifeq ($(BR2_PACKAGE_SPIRV_TOOLS),y)
MESA3D_DEPENDENCIES += spirv-tools
MESA3D_CONF_OPTS += -Dspirv-tools=enabled
else
MESA3D_CONF_OPTS += -Dspirv-tools=disabled
endif

ifeq ($(BR2_PACKAGE_MESA3D_NEEDS_ELFUTILS),y)
MESA3D_DEPENDENCIES += elfutils
endif

ifeq ($(BR2_PACKAGE_MESA3D_OPENGL_GLX),y)
# Disable-mangling not yet supported by meson build system.
# glx:
#  dri          : dri based GLX requires at least one DRI driver
#  xlib         : xlib conflicts with any dri driver
# Always enable glx-direct; without it, many GLX applications don't work.
MESA3D_CONF_OPTS += \
	-Dglx=dri \
	-Dglx-direct=true
else
MESA3D_CONF_OPTS += \
	-Dglx=disabled
endif

# Drivers

#Gallium Drivers
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_CROCUS)   += crocus
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_ETNAVIV)  += etnaviv
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_FREEDRENO) += freedreno
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_I915)     += i915
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_IRIS)     += iris
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_LIMA)     += lima
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_NOUVEAU)  += nouveau
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_PANFROST) += panfrost
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_R300)     += r300
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_R600)     += r600
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_RADEONSI) += radeonsi
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_SVGA)     += svga
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_SWRAST)   += softpipe,llvmpipe
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_TEGRA)    += tegra
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_V3D)      += v3d
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_VC4)      += vc4
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_VIRGL)    += virgl
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_ZINK)     += zink
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_D3D12)    += d3d12
MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_ASAHI)    += asahi
MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_INTEL)     += intel
MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_SWRAST) += swrast
MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_VIRTIO)    += virtio
MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_HASWELL)   += intel_hasvk
MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_AMD)       += amd
MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_BROADCOM)  += broadcom
MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_PANFROST)  += panfrost
MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_FREEDRENO) += freedreno
MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_ASAHI)     += asahi
MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_LAVAPIPE)      += swrast
MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_IMAGINATION)  += imagination
MESA3D_VIDEO_CODECS-$(BR2_PACKAGE_MESA3D_VIDEO_CODEC_VC1DEC)        += vc1dec
MESA3D_VIDEO_CODECS-$(BR2_PACKAGE_MESA3D_VIDEO_CODEC_H264DEC)       += h264dec
MESA3D_VIDEO_CODECS-$(BR2_PACKAGE_MESA3D_VIDEO_CODEC_H264ENC)       += h264enc
MESA3D_VIDEO_CODECS-$(BR2_PACKAGE_MESA3D_VIDEO_CODEC_H265DEC)       += h265dec
MESA3D_VIDEO_CODECS-$(BR2_PACKAGE_MESA3D_VIDEO_CODEC_H265ENC)       += h265enc
MESA3D_VIDEO_CODECS-$(BR2_PACKAGE_MESA3D_VIDEO_CODEC_AV1DEC)        += av1dec
MESA3D_VIDEO_CODECS-$(BR2_PACKAGE_MESA3D_VIDEO_CODEC_AV1ENC)        += av1enc
MESA3D_VIDEO_CODECS-$(BR2_PACKAGE_MESA3D_VIDEO_CODEC_VP9DEC)        += vp9dec

# Vulkan Layers - helps with multi-GPU switching
ifeq ($(BR2_PACKAGE_WAYLAND)$(BR2_PACKAGE_MESA3D_NEEDS_X11),yy)
MESA3D_CONF_OPTS += -Dvulkan-layers=device-select,overlay
endif

ifeq ($(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER),)
MESA3D_CONF_OPTS += \
	-Dgallium-drivers= \
	-Dgallium-extra-hud=false
else
MESA3D_CONF_OPTS += \
	-Dgallium-drivers=$(subst $(space),$(comma),$(MESA3D_GALLIUM_DRIVERS-y)) \
	-Dgallium-extra-hud=true
endif

ifeq ($(BR2_PACKAGE_MESA3D_VULKAN_DRIVER),)
MESA3D_CONF_OPTS += \
	-Dvulkan-drivers=
else
MESA3D_DEPENDENCIES += host-glslang
MESA3D_CONF_OPTS += \
	-Dvulkan-drivers=$(subst $(space),$(comma),$(MESA3D_VULKAN_DRIVERS-y))
endif

# video codecs
ifeq ($(BR2_PACKAGE_MESA3D_VIDEO_CODEC),)
MESA3D_CONF_OPTS += \
	-Dvideo-codecs=
else
MESA3D_CONF_OPTS += \
	-Dvideo-codecs=$(subst $(space),$(comma),$(MESA3D_VIDEO_CODECS-y))
endif

# Always enable OpenGL:
#   - Building OpenGL ES without OpenGL is not supported, so always keep opengl enabled.
MESA3D_CONF_OPTS += -Dopengl=true

# libva and mesa3d have a circular dependency
# we do not need libva support in mesa3d, therefore disable this option
# enable vaapi acceleration
ifneq ($(BR2_PACKAGE_SYSTEM_TARGET_WSL),y)
ifeq ($(BR2_PACKAGE_LIBVA)$(BR2_x86_64),yy)
MESA3D_CONF_OPTS += -Dgallium-va=enabled
MESA3D_DEPENDENCIES += libva
# link vaapi acceleration drivers accordingly
define MESA3D_ADD_VA_LINKS
	(mkdir -p $(TARGET_DIR)/usr/lib/va && cd $(TARGET_DIR)/usr/lib/va \
	    && ln -sf /usr/lib/dri/radeonsi_drv_video.so radeonsi_drv_video.so \
		&& ln -sf /usr/lib/dri/r600_drv_video.so r600_drv_video.so \
		&& ln -sf /usr/lib/dri/nouveau_drv_video.so nouveau_drv_video.so)
endef

MESA3D_POST_INSTALL_TARGET_HOOKS += MESA3D_ADD_VA_LINKS
else
MESA3D_CONF_OPTS += -Dgallium-va=disabled
endif
else
MESA3D_CONF_OPTS += -Dgallium-va=disabled
endif

# libGL is only provided for a full xorg stack, without libglvnd
ifeq ($(BR2_PACKAGE_MESA3D_OPENGL_GLX),y)
MESA3D_PROVIDES += $(if $(BR2_PACKAGE_LIBGLVND),,libgl)
else
define MESA3D_REMOVE_OPENGL_HEADERS
	rm -rf $(STAGING_DIR)/usr/include/GL/
endef

MESA3D_POST_INSTALL_STAGING_HOOKS += MESA3D_REMOVE_OPENGL_HEADERS
endif

ifeq ($(BR2_PACKAGE_MESA3D_NEEDS_X11),y)
MESA3D_DEPENDENCIES += \
	xlib_libX11 \
	xlib_libXext \
	xlib_libXdamage \
	xlib_libXfixes \
	xlib_libXrandr \
	xlib_libXxf86vm \
	xorgproto \
	libxcb
MESA3D_PLATFORMS += x11
endif
ifeq ($(BR2_PACKAGE_WAYLAND),y)
MESA3D_DEPENDENCIES += wayland wayland-protocols
MESA3D_PLATFORMS += wayland
endif

MESA3D_CONF_OPTS += \
	-Dplatforms=$(subst $(space),$(comma),$(MESA3D_PLATFORMS))

ifeq ($(BR2_PACKAGE_MESA3D_GBM),y)
MESA3D_CONF_OPTS += \
	-Dgbm=enabled
else
MESA3D_CONF_OPTS += \
	-Dgbm=disabled
endif

ifeq ($(BR2_PACKAGE_MESA3D_OPENGL_EGL),y)
MESA3D_PROVIDES += $(if $(BR2_PACKAGE_LIBGLVND),,libegl)
MESA3D_CONF_OPTS += \
	-Degl=enabled
else
MESA3D_CONF_OPTS += \
	-Degl=disabled
endif

ifeq ($(BR2_PACKAGE_MESA3D_OPENGL_ES),y)
MESA3D_PROVIDES += $(if $(BR2_PACKAGE_LIBGLVND),,libgles)
MESA3D_CONF_OPTS += -Dgles1=enabled -Dgles2=enabled
else
MESA3D_CONF_OPTS += -Dgles1=disabled -Dgles2=disabled
endif

ifeq ($(BR2_PACKAGE_VALGRIND),y)
MESA3D_CONF_OPTS += -Dvalgrind=enabled
MESA3D_DEPENDENCIES += valgrind
else
MESA3D_CONF_OPTS += -Dvalgrind=disabled
endif

ifeq ($(BR2_PACKAGE_LIBUNWIND),y)
MESA3D_CONF_OPTS += -Dlibunwind=enabled
MESA3D_DEPENDENCIES += libunwind
else
MESA3D_CONF_OPTS += -Dlibunwind=disabled
endif

ifeq ($(BR2_PACKAGE_LM_SENSORS),y)
MESA3D_CONF_OPTS += -Dlmsensors=enabled
MESA3D_DEPENDENCIES += lm-sensors
else
MESA3D_CONF_OPTS += -Dlmsensors=disabled
endif

ifeq ($(BR2_PACKAGE_ZSTD),y)
MESA3D_CONF_OPTS += -Dzstd=enabled
MESA3D_DEPENDENCIES += zstd
else
MESA3D_CONF_OPTS += -Dzstd=disabled
endif

# icd.@0@.json vulkan files
define MESA3D_VULKANJSON_X86_64
        $(SED) s+"host_machine.cpu()"+"'x86_64'"+ $(@D)/src/intel/vulkan/meson.build \
		    $(@D)/src/intel/vulkan_hasvk/meson.build $(@D)/src/amd/vulkan/meson.build
endef

define MESA3D_VULKANJSON_X86
        $(SED) s+"host_machine.cpu()"+"'i686'"+ $(@D)/src/intel/vulkan/meson.build \
		    $(@D)/src/intel/vulkan_hasvk/meson.build $(@D)/src/amd/vulkan/meson.build
endef

ifeq ($(BR2_x86_64),y)
    MESA3D_PRE_CONFIGURE_HOOKS += MESA3D_VULKANJSON_X86_64
endif
ifeq ($(BR2_x86_i686),y)
    MESA3D_PRE_CONFIGURE_HOOKS += MESA3D_VULKANJSON_X86
endif

MESA3D_CFLAGS = $(TARGET_CFLAGS)

# m68k needs 32-bit offsets in switch tables to build
ifeq ($(BR2_m68k),y)
MESA3D_CFLAGS += -mlong-jump-table-offsets
endif

ifeq ($(BR2_PACKAGE_LIBGLVND),y)
ifneq ($(BR2_PACKAGE_MESA3D_OPENGL_GLX)$(BR2_PACKAGE_MESA3D_OPENGL_EGL),)
MESA3D_DEPENDENCIES += libglvnd
MESA3D_CONF_OPTS += -Dglvnd=enabled
else
MESA3D_CONF_OPTS += -Dglvnd=disabled
endif
else
MESA3D_CONF_OPTS += -Dglvnd=disabled
endif

$(eval $(meson-package))

# "just" need various clc compilers / host tools
HOST_MESA3D_DEPENDENCIES = host-glslang host-wayland-protocols host-libdrm host-bison host-flex host-python-mako host-expat host-zlib host-python-ply host-python3 host-python-pyyaml
HOST_MESA3D_CONF_OPTS = -Dplatforms= -Dgallium-drivers= -Dvulkan-drivers= -Dglx=disabled -Dgallium-rusticl=false -Dcpp_rtti=false

# mesa-clc compiles OpenCL C kernels, so it needs clang/LLVM: libclc and
# spirv-llvm-translator drag in the whole stack (spirv-llvm-translator -> clang
# -> llvm). These are make-level dependencies, which buildroot honours whatever
# the kconfig symbol says, so on an arch missing from
# BR2_PACKAGE_LLVM_ARCH_SUPPORTS (i386/x86_64/aarch64/arm/riscv - mipsel is not
# there) this built an LLVM that kconfig deliberately leaves unset. With
# BR2_PACKAGE_LLVM_BUILD_FROM_SOURCE off that means downloading a prebuilt that
# was never published for the CPU, and the build dies on a 404.
#
# Every driver that needs mesa-clc (asahi, panfrost, imagination) is on an arch
# that does support LLVM. etnaviv, the only mipsel user, never references it.
ifeq ($(BR2_PACKAGE_LLVM_ARCH_SUPPORTS),y)
HOST_MESA3D_DEPENDENCIES += host-libclc host-spirv-llvm-translator
HOST_MESA3D_CONF_OPTS += -Dmesa-clc=enabled -Dinstall-mesa-clc=true -Dinstall-precomp-compiler=true
endif
ifeq ($(BR2_x86_64),y)
# LLVM RTTI is enabled on x86_64 build
HOST_MESA3D_CONF_OPTS += -Dcpp_rtti=true
#HOST_MESA3D_CONF_OPTS += -Dgallium-drivers=crocus,i915,iris,nouveau,r300,r600,radeonsi -Dvulkan-drivers=intel,intel_hasvk,amd
endif
ifeq ($(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_PANFROST),y)
HOST_MESA3D_CONF_OPTS += -Dgallium-drivers=panfrost
endif
ifeq ($(BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_ASAHI),y)
HOST_MESA3D_CONF_OPTS += -Dtools=asahi
endif
ifeq ($(BR2_PACKAGE_MESA3D_VULKAN_DRIVER_IMAGINATION),y)
HOST_MESA3D_CONF_OPTS += -Dtools=imagination
endif

# reglinux hack to fix prebuilt llvm/clang
#HOST_MESA3D_CONF_OPTS += -DCMAKE_INSTALL_RPATH="$(HOST_DIR)/lib"
# -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=TRUE
HOST_MESA3D_DEPENDENCIES += host-patchelf
define HOST_MESA3D_FIX_RPATH
    $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $(HOST_DIR)/bin/obj2yaml || true;
    $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $(HOST_DIR)/bin/yaml2obj || true;
endef

HOST_MESA3D_POST_INSTALL_HOOKS += HOST_MESA3D_FIX_RPATH
$(eval $(host-meson-package))
