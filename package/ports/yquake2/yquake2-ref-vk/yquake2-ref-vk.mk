################################################################################
#
# Yamagi Quake 2 (Vulkan renderer)
#
################################################################################

YQUAKE2_REF_VK_VERSION = v1.0.12
YQUAKE2_REF_VK_SITE = $(call github,yquake2,ref_vk,$(YQUAKE2_REF_VK_VERSION))

# Plain GNU Makefile, not CMake. Shaders are pre-compiled to SPIR-V and
# checked in as C arrays under src/vk/spirv/ (see shaders/shaders.bat), so
# no glslangValidator/glslc build dependency is needed -- just
# vulkan-headers for the <vulkan/vulkan.h> compile-time types. The actual
# Vulkan loader (libvulkan.so.1) is dlopen()'d at runtime by the vendored
# volk loader (src/vk/volk/), already installed on target by
# BR2_PACKAGE_REGLINUX_VULKAN's own BR2_PACKAGE_VULKAN_LOADER select --
# under BR2_PER_PACKAGE_DIRECTORIES this package's own build only sees
# headers from packages it explicitly depends on, so vulkan-headers has
# to be listed here too even though it's already selected globally.
YQUAKE2_REF_VK_DEPENDENCIES = vulkan-headers

# Same SDL major-version choice as yquake2-client: this renderer lib is
# dlopen()'d into the same process as the main quake2 binary, so it must
# agree with whichever SDL ABI that binary was built against.
ifeq ($(BR2_PACKAGE_SDL3),y)
YQUAKE2_REF_VK_DEPENDENCIES += sdl3
YQUAKE2_REF_VK_WITH_SDL3 = yes
else
YQUAKE2_REF_VK_DEPENDENCIES += sdl2
YQUAKE2_REF_VK_WITH_SDL3 = no
endif

# The Makefile derives YQ2_ARCH from `uname -m` by default, which reports
# the BUILD host's architecture, not the target's -- harmless on most of
# our targets (the value only gates i386/x86_64 -mfpmath=sse and arm
# -march=armv6k flags), but wrong when cross-compiling for aarch64 (e.g.
# odroidc5) from an x86_64 host: it would wrongly add the x86-only
# -mfpmath=sse flag to an aarch64 build and fail immediately. Force it
# from Buildroot's own normalized $(BR2_ARCH), through the same sed
# transform the Makefile itself uses, so it always matches the real
# target regardless of build host.
YQUAKE2_REF_VK_ARCH = $(shell echo $(BR2_ARCH) | sed -e 's/i.86/i386/' -e 's/amd64/x86_64/' -e 's/arm64/aarch64/' -e 's/^arm.*/arm/')

# The Makefile's own "Base include path" block (YQ2_OSTYPE=Linux ->
# INCLUDE ?= -I/usr/include) assumes a native desktop build where
# vulkan-headers live under the system prefix; it's the only place
# <vulkan/vulkan.h> gets found (there's no separate pkg-config/cmake
# vulkan detection in this Makefile at all). Cross-compiling, that
# resolves to the build HOST's /usr/include, which GCC's cross-compile
# safety check then rejects outright -- override it to this package's
# own sysroot instead, same as switchres/scummvm/love2d do.
define YQUAKE2_REF_VK_BUILD_CMDS
	$(MAKE) -C $(@D) \
		CC="$(TARGET_CC)" \
		PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
		CFLAGS="$(TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)" \
		INCLUDE="-I$(STAGING_DIR)/usr/include" \
		YQ2_OSTYPE=Linux \
		YQ2_ARCH="$(YQUAKE2_REF_VK_ARCH)" \
		WITH_SDL3=$(YQUAKE2_REF_VK_WITH_SDL3)
endef

# Installed under datainit alongside yquake2-client's other renderers so
# first-boot populate lands it in /userdata/roms/quake2 next to
# ref_gl1.so/ref_gl3.so/ref_gles3.so (see
# package/ports/yquake2/yquake2-client/yquake2-client.mk). Select "Vulkan"
# from the in-game video menu, or `vid_renderer vk` + `vid_restart`.
define YQUAKE2_REF_VK_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/release/ref_vk.so $(TARGET_DIR)/usr/share/reglinux/datainit/roms/quake2/ref_vk.so
endef

$(eval $(generic-package))
