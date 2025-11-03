################################################################################
#
# raze
#
################################################################################

RAZE_VERSION = 1.11.0
RAZE_SITE = $(call github,coelckers,Raze,$(RAZE_VERSION))
RAZE_LICENSE = GPLv2
RAZE_DEPENDENCIES = host-raze sdl2 bzip2 openal zmusic webp libvpx
RAZE_SUPPORTS_IN_SOURCE_BUILD = NO

# We need the tools from the host package to build the target package
HOST_RAZE_DEPENDENCIES = host-sdl2 zlib bzip2 host-webp
HOST_RAZE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HOST_RAZE_CONF_OPTS += -DSKIP_INSTALL_ALL=ON

# The TOOLS_ONLY=ON option is not implemented in Raze yet.
# This does in fact build the entire engine, not just the build tools.
# We disable Vulkan to avoid having to depend on `host-xlib_libX11`.
HOST_RAZE_CONF_OPTS += -DTOOLS_ONLY=ON
HOST_RAZE_CONF_OPTS += -DHAVE_VULKAN=OFF
HOST_RAZE_SUPPORTS_IN_SOURCE_BUILD = NO

define HOST_RAZE_INSTALL_CMDS
	# Skip install as we only need `ImportExecutables.cmake` from the build directory.
endef

RAZE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RAZE_CONF_OPTS += -DFORCE_CROSSCOMPILE=ON
RAZE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
RAZE_CONF_OPTS += -DIMPORT_EXECUTABLES="$(HOST_RAZE_BUILDDIR)/ImportExecutables.cmake"

# Musl quirks
ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
RAZE_DEPENDENCIES += libbacktrace musl-fts
RAZE_CONF_OPTS += -DCMAKE_THREAD_LIBS_INIT="-lpthread" -DCMAKE_HAVE_THREADS_LIBRARY=1 -DTHREADS_PREFER_PTHREAD_FLAG=ON
RAZE_CONF_OPTS += -DCMAKE_C_FLAGS="-DLZMA_NO_MT -DZ7_AFFINITY_DISABLE"
RAZE_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-L$(STAGING_DIR)/usr/lib -lfts"
endif

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    RAZE_CONF_OPTS += -DHAVE_VULKAN=ON
    RAZE_DEPENDENCIES += vulkan-headers vulkan-loader
    RAZE_DEPENDENCIES += wayland
    RAZE_CONF_OPTS += -DVULKAN_USE_XLIB=OFF -DVULKAN_USE_WAYLAND=ON
else
    RAZE_CONF_OPTS += -DHAVE_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_HAS_GLES2)$(BR2_PACKAGE_HAS_GLES3),y)
    RAZE_CONF_OPTS += -DHAVE_GLES2=ON
    RAZE_DEPENDENCIES += libgles
else
    RAZE_CONF_OPTS += -DHAVE_GLES2=OFF
    RAZE_DEPENDENCIES += libgl
endif

define RAZE_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/raze \
        $(TARGET_DIR)/usr/bin/raze
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/raze.pk3 \
        $(TARGET_DIR)/usr/share/raze/raze.pk3
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/soundfonts/raze.sf2 \
        $(TARGET_DIR)/usr/share/raze/soundfonts/raze.sf2
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/raze/raze.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
$(eval $(host-cmake-package))
