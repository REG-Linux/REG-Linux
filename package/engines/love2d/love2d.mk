################################################################################
#
# love2d
#
################################################################################
# Version: Release on Dec 3, 2023
LOVE2D_VERSION = 11.5
LOVE2D_SITE = https://github.com/love2d/love
LOVE2D_SITE_METHOD = git

LOVE2D_LICENSE = zlib
LOVE2D_LICENSE_FILES = license.txt
LOVE2D_SUPPORTS_IN_SOURCE_BUILD = NO

LOVE2D_DEPENDENCIES = freetype libmodplug libogg libtheora \
	libvorbis mpg123 openal reglinux-luajit sdl2 zlib

# Use bundled FindLuaJIT.cmake and other find modules
LOVE2D_CONF_OPTS = \
	-DLOVE_JIT=ON \
	-DLOVE_MPG123=ON \
	-DBUILD_SHARED_LIBS=OFF \
	-DCMAKE_MODULE_PATH=$(@D)/extra/cmake

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
LOVE2D_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
# Love2d uses GLAD to load GL/GLES at runtime.
# CMake needs a libGL to link against — use gl4es on GLES platforms.
LOVE2D_DEPENDENCIES += gl4es libgles
LOVE2D_CONF_OPTS += \
	-DOPENGL_opengl_LIBRARY=$(STAGING_DIR)/usr/lib/gl4es/libGL.so.1 \
	-DOPENGL_gl_LIBRARY=$(STAGING_DIR)/usr/lib/gl4es/libGL.so.1 \
	-DOPENGL_INCLUDE_DIR=$(STAGING_DIR)/usr/include \
	-DOPENGL_glx_LIBRARY=$(STAGING_DIR)/usr/lib/gl4es/libGL.so.1
endif

define LOVE2D_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/love $(TARGET_DIR)/usr/bin/love
	-cp -avf $(@D)/buildroot-build/liblove*.so* $(TARGET_DIR)/usr/lib/ 2>/dev/null || true
endef

$(eval $(cmake-package))
