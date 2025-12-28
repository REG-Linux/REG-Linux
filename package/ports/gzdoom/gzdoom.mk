################################################################################
#
# gzdoom
#
################################################################################
# Version: Release on May 3, 2025
GZDOOM_VERSION = g4.14.2
GZDOOM_SITE = https://github.com/ZDoom/gzdoom.git
GZDOOM_SITE_METHOD=git
GZDOOM_GIT_SUBMODULES=YES
GZDOOM_LICENSE = GPLv3
GZDOOM_DEPENDENCIES = host-gzdoom sdl2 bzip2 openal zmusic libvpx webp
GZDOOM_SUPPORTS_IN_SOURCE_BUILD = NO

# We need the tools from the host package to build the target package
HOST_GZDOOM_DEPENDENCIES = zlib bzip2 host-webp host-zmusic
HOST_GZDOOM_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HOST_GZDOOM_CONF_OPTS += -DSKIP_INSTALL_ALL=ON
HOST_GZDOOM_CONF_OPTS += -DTOOLS_ONLY=ON
HOST_GZDOOM_SUPPORTS_IN_SOURCE_BUILD = NO

define HOST_GZDOOM_INSTALL_CMDS
	# Skip install as we only need `ImportExecutables.cmake` from the build directory.
endef

GZDOOM_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
GZDOOM_CONF_OPTS += -DFORCE_CROSSCOMPILE=ON
GZDOOM_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
GZDOOM_CONF_OPTS += -DIMPORT_EXECUTABLES="$(HOST_GZDOOM_BUILDDIR)/ImportExecutables.cmake"

# Musl quirks
ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
GZDOOM_DEPENDENCIES += libbacktrace musl-fts
GZDOOM_CONF_OPTS += -DCMAKE_THREAD_LIBS_INIT="-lpthread" -DCMAKE_HAVE_THREADS_LIBRARY=1 -DTHREADS_PREFER_PTHREAD_FLAG=ON
GZDOOM_CONF_OPTS += -DCMAKE_C_FLAGS="-DLZMA_NO_MT -DZ7_AFFINITY_DISABLE"
GZDOOM_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-L$(STAGING_DIR)/usr/lib -lfts"
endif

# Enable vulkan only if we have it + Sway
ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER)$(BR2_PACKAGE_SWAY),yyy)
    GZDOOM_CONF_OPTS += -DHAVE_VULKAN=ON
    GZDOOM_DEPENDENCIES += vulkan-headers vulkan-loader
    ifeq ($(BR2_PACKAGE_REGLINUX_XWAYLAND),y)
        GZDOOM_CONF_OPTS += -DVULKAN_USE_XLIB=ON -DVULKAN_USE_WAYLAND=OFF
    else ifeq ($(BR2_PACKAGE_WAYLAND)$(BR2_PACKAGE_SWAY),yy)
        GZDOOM_CONF_OPTS += -DVULKAN_USE_XLIB=OFF -DVULKAN_USE_WAYLAND=ON
    endif
else
    GZDOOM_CONF_OPTS += -DHAVE_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    GZDOOM_CONF_OPTS += -DHAVE_GLES2=OFF
    GZDOOM_DEPENDENCIES += libgl
else
    GZDOOM_CONF_OPTS += -DHAVE_GLES2=ON
    GZDOOM_DEPENDENCIES += libgles
endif

define GZDOOM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/gzdoom
	$(INSTALL) -m 0755 $(@D)/buildroot-build/gzdoom	$(TARGET_DIR)/usr/bin
	$(INSTALL) -m 0755 $(@D)/buildroot-build/*.pk3 $(TARGET_DIR)/usr/share/gzdoom
	cp -pr $(@D)/buildroot-build/fm_banks $(TARGET_DIR)/usr/share/gzdoom
	cp -pr $(@D)/buildroot-build/soundfonts $(TARGET_DIR)/usr/share/gzdoom
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/gzdoom/gzdoom.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
$(eval $(host-cmake-package))
