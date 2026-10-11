################################################################################
#
# play!
#
################################################################################
PLAY_VERSION = 0.77
PLAY_SITE = https://github.com/jpd002/Play-.git
PLAY_SITE_METHOD = git
PLAY_GIT_SUBMODULES = YES
PLAY_LICENSE = BSD

PLAY_DEPENDENCIES = openal reglinux-qt6 sqlite ecm

PLAY_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
PLAY_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
PLAY_CONF_OPTS += -DINSTALL_STATIC_LIBS=ON
PLAY_CONF_OPTS += -DBUILD_TESTS=OFF
PLAY_CONF_OPTS += -DENABLE_AMAZON_S3=OFF

# OpenGL backend. Key off HAS_DESKTOP_OPENGL rather than HAS_LIBGL/XWayland:
# enabling XWayland selects XORG7, which pulls in MESA3D_OPENGL_GLX and
# therefore HAS_LIBGL, so libGL.so exists even on boards with no usable desktop
# GL. What actually decides this is Source/ui_qt/openglwindow.cpp, which asks
# Qt for a *desktop GL 3.2 core* context unless GLES_COMPATIBILITY is defined
# (in which case it asks for GLES 3.0). Framework_OpenGl defines that PUBLIC
# when USE_GLES is on, so it reaches ui_qt.
#
# The ODROID-C5's panfrost reports GL 3.1 core -- one minor version short --
# so the desktop-GL build dies at startup with "QEGLPlatformContext: Failed to
# create context: 3009" before anything renders. Selecting the Vulkan GS
# handler does not help: it is Qt's own window context that fails, not the GS.
# GLES 3.1 is available there, so the GLES build gets its 3.0 context.
# Mirrors libretro-play.mk.
ifeq ($(BR2_PACKAGE_HAS_DESKTOP_OPENGL),y)
    PLAY_DEPENDENCIES += libgl libglew libglu
ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86_64_ANY),y)
    PLAY_CONF_OPTS += -DOpenGL_GL_PREFERENCE=GLVND
endif
else
    # GLES everywhere else, including panfrost/panthor boards that have
    # XWayland but no usable desktop GL.
    PLAY_CONF_OPTS += -DUSE_GLEW=OFF
    PLAY_CONF_OPTS += -DUSE_GLES=ON
    PLAY_DEPENDENCIES += libgles
endif

# XWayland stays a build-order dependency wherever it is enabled; it is
# unrelated to which GL flavour Play! links against.
ifeq ($(BR2_PACKAGE_REGLINUX_XWAYLAND),y)
    PLAY_DEPENDENCIES += xwayland
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    PLAY_DEPENDENCIES += vulkan-headers vulkan-loader
endif

$(eval $(cmake-package))
