################################################################################
#
# GemRB
#
################################################################################

GEMRB_VERSION = v0.9.4
GEMRB_SITE =  $(call github,gemrb,gemrb,$(GEMRB_VERSION))
GEMRB_LICENSE = GPL-2.0
GEMRB_LICENSE_FILE = LICENSE

GEMRB_DEPENDENCIES += sdl2 sdl2_mixer openal zlib icu
GEMRB_DEPENDENCIES += libpng freetype libogg libvorbis

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
GEMRB_DEPENDENCIES += libgl
GEMRB_CONF_OPTS += -DOPENGL_BACKEND="OpenGL"
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
GEMRB_DEPENDENCIES += libgles
GEMRB_CONF_OPTS += -DOPENGL_BACKEND="GLES"
endif

GEMRB_SUPPORTS_IN_SOURCE_BUILD = NO

GEMRB_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
GEMRB_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
GEMRB_CONF_OPTS += -DSTATIC_LINK=ON
GEMRB_CONF_OPTS += -DUSE_LIBVLC=OFF

define GEMRB_STRIP_BINARY
	$(TARGET_STRIP) $(TARGET_DIR)/usr/bin/gemrb
endef

define GEMRB_EVMAPY
#	mkdir -p $(TARGET_DIR)/usr/share/evmapy
#	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/reglinux/ports/gemrb/gemrbkeys \
#	    $(TARGET_DIR)/usr/share/evmapy
endef

GEMRB_POST_INSTALL_TARGET_HOOKS += GEMRB_STRIP_BINARY
GEMRB_POST_INSTALL_TARGET_HOOKS += GEMRB_EVMAPY

$(eval $(cmake-package))
