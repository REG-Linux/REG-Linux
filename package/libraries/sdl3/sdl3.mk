################################################################################
#
# sdl3
#
################################################################################

SDL3_VERSION = 3.2.24
SDL3_SOURCE = SDL3-$(SDL3_VERSION).tar.gz
SDL3_SITE = http://www.libsdl.org/release
SDL3_LICENSE = Zlib
SDL3_LICENSE_FILES = LICENSE.txt
SDL3_CPE_ID_VENDOR = libsdl
SDL3_CPE_ID_PRODUCT = simple_directmedia_layer
SDL3_INSTALL_STAGING = YES

ifeq ($(BR2_ENABLE_DEBUG),y)
SDL3_CONF_OPTS = -DCMAKE_BUILD_TYPE=Debug
SDL3_CONF_OPTS += -DSDL_TESTS=ON
SDL3_CONF_OPTS += -DSDL_INSTALL_TESTS=ON
else
SDL3_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release
endif

# reglinux - RISC-V depend on custom mesa to enable wayland properly
ifeq ($(BR2_PACKAGE_IMG_GPU_POWERVR),y)
SDL3_DEPENDENCIES += img-gpu-powervr img-mesa3d
endif

# reglinux - depend on mesa3d for kmsdrm (gbm+egl) if enabled
ifeq ($(BR2_PACKAGE_MESA3D),y)
SDL3_DEPENDENCIES += mesa3d
endif

# reglinux - use Pipewire audio
ifeq ($(BR2_PACKAGE_PIPEWIRE),y)
SDL3_DEPENDENCIES += pipewire
endif

ifeq ($(BR2_PACKAGE_HAS_UDEV),y)
SDL3_DEPENDENCIES += udev
endif

ifeq ($(BR2_PACKAGE_SDL3_DIRECTFB),y)
SDL3_DEPENDENCIES += directfb
endif

# x-includes and x-libraries must be set for cross-compiling
# By default x_includes and x_libraries contains unsafe paths.
# (/usr/X11R6/include and /usr/X11R6/lib)
ifeq ($(BR2_PACKAGE_SDL3_X11),y)
SDL3_DEPENDENCIES += xlib_libX11 xlib_libXext
ifeq ($(BR2_PACKAGE_XLIB_LIBXCURSOR),y)
SDL3_DEPENDENCIES += xlib_libXcursor
endif
ifeq ($(BR2_PACKAGE_XLIB_LIBXI),y)
SDL3_DEPENDENCIES += xlib_libXi
endif
ifeq ($(BR2_PACKAGE_XLIB_LIBXRANDR),y)
SDL3_DEPENDENCIES += xlib_libXrandr
endif
ifeq ($(BR2_PACKAGE_XLIB_LIBXSCRNSAVER),y)
SDL3_DEPENDENCIES += xlib_libXScrnSaver
endif
endif

ifeq ($(BR2_PACKAGE_SDL3_OPENGL),y)
SDL3_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_SDL3_OPENGLES),y)
SDL3_DEPENDENCIES += libgles
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
SDL3_DEPENDENCIES += alsa-lib
endif

ifeq ($(BR2_PACKAGE_SDL3_KMSDRM),y)
SDL3_DEPENDENCIES += libdrm
endif

# reglinux - enable/disable Wayland video driver
ifeq ($(BR2_PACKAGE_SDL3_WAYLAND),y)
SDL3_DEPENDENCIES += wayland wayland-protocols libxkbcommon
else
SDL3_CONF_OPTS += -DSDL_UNIX_CONSOLE_BUILD=ON
endif

# reglinux - libdecor
ifeq ($(BR2_PACKAGE_LIBDECOR),y)
SDL3_DEPENDENCIES += libdecor
endif

# reglinux - enable/disable Vulkan support
ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
SDL3_DEPENDENCIES += vulkan-headers vulkan-loader
endif

$(eval $(cmake-package))

# Host build specific option
HOST_SDL3_CONF_OPTS += -DSDL_UNIX_CONSOLE_BUILD=ON
$(eval $(host-cmake-package))
