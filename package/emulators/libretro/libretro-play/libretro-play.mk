################################################################################
#
# libretro-play
#
################################################################################

LIBRETRO_PLAY_VERSION = 0.77
LIBRETRO_PLAY_SITE = https://github.com/jpd002/Play-.git
LIBRETRO_PLAY_SITE_METHOD = git
LIBRETRO_PLAY_GIT_SUBMODULES = YES
LIBRETRO_PLAY_LICENSE = BSD

LIBRETRO_PLAY_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_PLAY_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
LIBRETRO_PLAY_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
LIBRETRO_PLAY_CONF_OPTS += -DBUILD_TESTS=OFF
LIBRETRO_PLAY_CONF_OPTS += -DBUILD_LIBRETRO_CORE=ON
LIBRETRO_PLAY_CONF_OPTS += -DBUILD_PLAY=OFF
LIBRETRO_PLAY_CONF_OPTS += -DENABLE_AMAZON_S3=ON

# OpenGL backend — must match RetroArch's API selection.
# Key off HAS_DESKTOP_OPENGL rather than HAS_LIBGL (polluted by XWayland).
ifeq ($(BR2_PACKAGE_HAS_DESKTOP_OPENGL),y)
LIBRETRO_PLAY_DEPENDENCIES = libgl libglew libglu
# USE_GLES must be passed explicitly, not left to the CMake default.
# deps/Framework/build_cmake/FrameworkOpenGl/CMakeLists.txt turns it ON for
# TARGET_PLATFORM_UNIX_AARCH64 (set just below), which defines
# GLES_COMPATIBILITY, which makes main_libretro.cpp ask for
# RETRO_HW_CONTEXT_OPENGLES3. On a desktop-GL RetroArch that request is
# refused outright:
#   [HW] Requesting OpenGLES3 context, but RetroArch is compiled against
#        OpenGL. Cannot use HW context.
# The core then runs with no GL context and presents nothing -- a white
# screen with audio still playing. Seen on sm8250/RP5 (Adreno 650, glcore
# 4.6). Because the CMake default uses set(... CACHE ...), a -D on the
# command line takes precedence.
LIBRETRO_PLAY_CONF_OPTS += -DUSE_GLES=OFF
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
LIBRETRO_PLAY_DEPENDENCIES = libgles
LIBRETRO_PLAY_CONF_OPTS += -DUSE_GLEW=OFF
LIBRETRO_PLAY_CONF_OPTS += -DUSE_GLES=ON
endif

ifeq ($(BR2_aarch64),y)
LIBRETRO_PLAY_CONF_OPTS += -DTARGET_PLATFORM_UNIX_AARCH64=YES
else ifeq ($(BR2_arm),y)
LIBRETRO_PLAY_CONF_OPTS += -DTARGET_PLATFORM_UNIX_ARM=YES
endif

define LIBRETRO_PLAY_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Source/ui_libretro/play_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/play_libretro.so
endef

$(eval $(cmake-package))
