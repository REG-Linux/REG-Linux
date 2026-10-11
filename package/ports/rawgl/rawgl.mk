################################################################################
#
# rawgl — Another World / Out of This World engine reimplementation
#
################################################################################

RAWGL_VERSION = rawgl-0.2.1
RAWGL_SITE = https://github.com/cyxx/rawgl
RAWGL_SITE_METHOD = git
RAWGL_LICENSE = Custom (Gregory Montoir)

RAWGL_DEPENDENCIES = sdl2 sdl2_mixer zlib

# Build with software renderer only (GLES-compatible, no desktop GL needed)
# Add USE_GL=1 and libgl dep to enable OpenGL renderer on desktop GL platforms
RAWGL_CFLAGS = $(TARGET_CFLAGS) -DBYPASS_PROTECTION -DMIX_INIT_FLUIDSYNTH=MIX_INIT_MID \
	$$($(PKG_CONFIG_HOST_BINARY) sdl2 --cflags) \
	-Wall -O2 -MMD
RAWGL_LDFLAGS = $(TARGET_LDFLAGS) \
	$$($(PKG_CONFIG_HOST_BINARY) sdl2 --libs) \
	-lSDL2_mixer -lz -lm

# Enable GL renderer on platforms that have desktop GL
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
RAWGL_DEPENDENCIES += libgl
RAWGL_CFLAGS += -DUSE_GL
RAWGL_LDFLAGS += -lGL
endif

RAWGL_SRCS = aifcplayer.cpp bitmap.cpp engine.cpp file.cpp \
	graphics_soft.cpp main.cpp mixer.cpp pak.cpp resource.cpp \
	resource_3do.cpp resource_nth.cpp resource_win31.cpp \
	script.cpp sfxplayer.cpp staticres.cpp \
	systemstub_sdl.cpp unpack.cpp util.cpp video.cpp

define RAWGL_BUILD_CMDS
	$(if $(BR2_PACKAGE_HAS_LIBGL),,echo '#include "graphics.h"' > $(@D)/graphics_gl_stub.cpp && echo 'Graphics *GraphicsGL_create() { return 0; }' >> $(@D)/graphics_gl_stub.cpp)
	$(TARGET_CXX) $(RAWGL_CFLAGS) -I$(@D) \
		$(addprefix $(@D)/,$(RAWGL_SRCS)) \
		$(if $(BR2_PACKAGE_HAS_LIBGL),$(@D)/graphics_gl.cpp,$(@D)/graphics_gl_stub.cpp) \
		-o $(@D)/rawgl $(RAWGL_LDFLAGS)
endef

define RAWGL_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/rawgl $(TARGET_DIR)/usr/bin/rawgl
endef

$(eval $(generic-package))
