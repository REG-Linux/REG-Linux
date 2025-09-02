################################################################################
#
# sdl2
#
################################################################################

# reglinux - bump
SDL2_VERSION = 2.32.10
SDL2_SOURCE = SDL2-$(SDL2_VERSION).tar.gz
SDL2_SITE = http://www.libsdl.org/release
SDL2_LICENSE = Zlib
SDL2_LICENSE_FILES = LICENSE.txt
SDL2_CPE_ID_VENDOR = libsdl
SDL2_CPE_ID_PRODUCT = simple_directmedia_layer
SDL2_INSTALL_STAGING = YES
SDL2_CONFIG_SCRIPTS = sdl2-config

# reglinux - remove --disable-video-wayland and --disable-video-vulkan
SDL2_CONF_OPTS += \
	--disable-rpath \
	--disable-arts \
	--disable-esd \
	--disable-dbus \
	--disable-pulseaudio \
	--disable-video-vivante \
	--disable-video-cocoa \
	--disable-video-metal \
	--disable-video-dummy \
	--disable-video-offscreen \
	--disable-ime \
	--disable-ibus \
	--disable-fcitx \
	--disable-joystick-mfi \
	--disable-directx \
	--disable-xinput \
	--disable-wasapi \
	--disable-joystick-virtual \
	--disable-render-d3d

HOST_SDL2_CONF_OPTS += \
	--disable-rpath \
	--disable-arts \
	--disable-esd \
	--disable-dbus \
	--disable-pulseaudio \
	--disable-video-vivante \
	--disable-video-cocoa \
	--disable-video-metal \
	--disable-video-dummy \
	--disable-video-offscreen \
	--disable-video-wayland \
	--disable-video-x11 \
	--disable-video-vulkan \
	--disable-ime \
	--disable-ibus \
	--disable-fcitx \
	--disable-joystick-mfi \
	--disable-directx \
	--disable-xinput \
	--disable-wasapi \
	--disable-hidapi-joystick \
	--disable-hidapi-libusb \
	--disable-joystick-virtual \
	--disable-render-d3d

# We are using autotools build system for sdl2, so the sdl2-config.cmake
# include path are not resolved like for sdl2-config script.
# Change the absolute /usr path to resolve relatively to the sdl2-config.cmake location.
# https://bugzilla.libsdl.org/show_bug.cgi?id=4597
define SDL2_FIX_SDL2_CONFIG_CMAKE
	$(SED) '2iget_filename_component(PACKAGE_PREFIX_DIR "$${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)\n' \
		$(STAGING_DIR)/usr/lib/cmake/SDL2/sdl2-config.cmake
	$(SED) 's%"/usr"%$${PACKAGE_PREFIX_DIR}%' \
		$(STAGING_DIR)/usr/lib/cmake/SDL2/sdl2-config.cmake
endef

# batocera
define SDL2_FIX_WAYLAND_SCANNER_PATH
	sed -i "s+/usr/bin/wayland-scanner+$(HOST_DIR)/usr/bin/wayland-scanner+g" $(@D)/Makefile
endef

define SDL2_FIX_CONFIGURE_PATHS
	sed -i "s+/host/bin/\.\.+/host+g" $(@D)/config.log
	sed -i "s+/host/bin/\.\.+/host+g" $(@D)/config.status
	sed -i "s+/host/bin/\.\.+/host+g" $(@D)/libtool
	sed -i "s+/host/bin/\.\.+/host+g" $(@D)/Makefile
	sed -i "s+/host/bin/\.\.+/host+g" $(@D)/sdl2-config
	sed -i "s+/host/bin/\.\.+/host+g" $(@D)/sdl2.pc
	sed -i "s+-I/.* ++g"              $(@D)/sdl2.pc
endef

SDL2_POST_CONFIGURE_HOOKS += SDL2_FIX_WAYLAND_SCANNER_PATH
SDL2_POST_CONFIGURE_HOOKS += SDL2_FIX_CONFIGURE_PATHS

SDL2_POST_INSTALL_STAGING_HOOKS += SDL2_FIX_SDL2_CONFIG_CMAKE

# We must enable static build to get compilation successful.
SDL2_CONF_OPTS += --enable-static

# batocera - Used in screen rotation (SDL and Retroarch)
ifeq ($(BR2_PACKAGE_ROCKCHIP_RGA),y)
SDL2_DEPENDENCIES += rockchip-rga
endif

# reglinux - RISC-V depend on custom mesa to enable wayland properly
ifeq ($(BR2_PACKAGE_IMG_GPU_POWERVR),y)
SDL2_DEPENDENCIES += img-gpu-powervr img-mesa3d
endif

# reglinux - depend on mesa3d for kmsdrm (gbm+egl) if enabled
ifeq ($(BR2_PACKAGE_MESA3D),y)
SDL2_DEPENDENCIES += mesa3d
endif

# batocera - use Pipewire audio
ifeq ($(BR2_PACKAGE_PIPEWIRE),y)
SDL2_CONF_OPTS += --enable-pipewire
endif

ifeq ($(BR2_ARM_INSTRUCTIONS_THUMB),y)
SDL2_CONF_ENV += CFLAGS="$(TARGET_CFLAGS) -marm"
endif

ifeq ($(BR2_PACKAGE_HAS_UDEV),y)
SDL2_DEPENDENCIES += udev
SDL2_CONF_OPTS += --enable-libudev
else
SDL2_CONF_OPTS += --disable-libudev
endif

ifeq ($(BR2_X86_CPU_HAS_SSE),y)
SDL2_CONF_OPTS += --enable-sse
else
SDL2_CONF_OPTS += --disable-sse
endif

# batocera / with patch sdl2_add_video_mali_gles2.patch / mrfixit
ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
SDL2_CONF_OPTS += --enable-video-mali
endif

ifeq ($(BR2_X86_CPU_HAS_3DNOW),y)
SDL2_CONF_OPTS += --enable-3dnow
else
SDL2_CONF_OPTS += --disable-3dnow
endif

ifeq ($(BR2_PACKAGE_SDL2_DIRECTFB),y)
SDL2_DEPENDENCIES += directfb
SDL2_CONF_OPTS += --enable-video-directfb
SDL2_CONF_ENV += ac_cv_path_DIRECTFBCONFIG=$(STAGING_DIR)/usr/bin/directfb-config
else
SDL2_CONF_OPTS += --disable-video-directfb
endif

SDL2_CONF_OPTS += --disable-video-rpi

# x-includes and x-libraries must be set for cross-compiling
# By default x_includes and x_libraries contains unsafe paths.
# (/usr/X11R6/include and /usr/X11R6/lib)
ifeq ($(BR2_PACKAGE_SDL2_X11),y)
SDL2_DEPENDENCIES += xlib_libX11 xlib_libXext

# X11/extensions/shape.h is provided by libXext.
SDL2_CONF_OPTS += --enable-video-x11 \
	--with-x=$(STAGING_DIR) \
	--x-includes=$(STAGING_DIR)/usr/include \
	--x-libraries=$(STAGING_DIR)/usr/lib \
	--enable-video-x11-xshape

ifeq ($(BR2_PACKAGE_XLIB_LIBXCURSOR),y)
SDL2_DEPENDENCIES += xlib_libXcursor
SDL2_CONF_OPTS += --enable-video-x11-xcursor
else
SDL2_CONF_OPTS += --disable-video-x11-xcursor
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXI),y)
SDL2_DEPENDENCIES += xlib_libXi
SDL2_CONF_OPTS += --enable-video-x11-xinput
else
SDL2_CONF_OPTS += --disable-video-x11-xinput
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXRANDR),y)
SDL2_DEPENDENCIES += xlib_libXrandr
SDL2_CONF_OPTS += --enable-video-x11-xrandr
else
SDL2_CONF_OPTS += --disable-video-x11-xrandr
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXSCRNSAVER),y)
SDL2_DEPENDENCIES += xlib_libXScrnSaver
SDL2_CONF_OPTS += --enable-video-x11-scrnsaver
else
SDL2_CONF_OPTS += --disable-video-x11-scrnsaver
endif

else
SDL2_CONF_OPTS += --disable-video-x11 --without-x
endif

ifeq ($(BR2_PACKAGE_SDL2_OPENGL),y)
SDL2_CONF_OPTS += --enable-video-opengl
SDL2_DEPENDENCIES += libgl
else
SDL2_CONF_OPTS += --disable-video-opengl
endif

ifeq ($(BR2_PACKAGE_SDL2_OPENGLES),y)
SDL2_CONF_OPTS += \
	--enable-video-opengles \
	--enable-video-opengles1 \
	--enable-video-opengles2
SDL2_DEPENDENCIES += libgles
else
SDL2_CONF_OPTS += \
	--disable-video-opengles \
	--disable-video-opengles1 \
	--disable-video-opengles2
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
SDL2_DEPENDENCIES += alsa-lib
SDL2_CONF_OPTS += --enable-alsa
else
SDL2_CONF_OPTS += --disable-alsa
endif

ifeq ($(BR2_PACKAGE_SDL2_KMSDRM),y)
SDL2_DEPENDENCIES += libdrm
SDL2_CONF_OPTS += --enable-video-kmsdrm
else
SDL2_CONF_OPTS += --disable-video-kmsdrm
endif

# batocera - enable/disable Wayland video driver
ifeq ($(BR2_PACKAGE_SDL2_WAYLAND),y)
SDL2_DEPENDENCIES += wayland wayland-protocols libxkbcommon
SDL2_CONF_OPTS += --enable-video-wayland
else
SDL2_CONF_OPTS += --disable-video-wayland
endif

# batocera - libdecor
ifeq ($(BR2_PACKAGE_LIBDECOR),y)
SDL2_DEPENDENCIES += libdecor
endif

# batocera - enable/disable Vulkan support
ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
SDL2_DEPENDENCIES += vulkan-headers vulkan-loader
SDL2_CONF_OPTS += --enable-video-vulkan
else
SDL2_CONF_OPTS += --disable-video-vulkan
endif

$(eval $(autotools-package))
$(eval $(host-autotools-package))
