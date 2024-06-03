################################################################################
#
# OpenLara
#
################################################################################

OPENLARA_VERSION = 28ee7ac92367e6c97aea2391c25e1c6fe29785aa
OPENLARA_SITE = https://github.com/XProger/OpenLara
OPENLARA_SITE_METHOD=git
OPENLARA_DEPENDENCIES = zlib openal sdl2

# SDL2 + GL build
ifeq ($(BR2_x86_64),y)
define OPENLARA_BUILD_CMDS
cd $(@D)/src/platform/sdl2 && \
$(TARGET_CXX) -std=c++11 `$(STAGING_DIR)/usr/bin/sdl2-config --cflags` -O3 -fno-exceptions -fno-rtti -ffunction-sections -fdata-sections -Wl,--gc-sections -DNDEBUG -D__SDL2__ -D_SDL2_OPENGL main.cpp ../../libs/stb_vorbis/stb_vorbis.c ../../libs/minimp3/minimp3.cpp ../../libs/tinf/tinflate.c -I../../ -o OpenLara `$(STAGING_DIR)/usr/bin/sdl2-config --libs` -lGL -lm -lrt -lpthread -lasound -ludev
endef

# SDL2 + GLES2 build
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_GLES3),y)
define OPENLARA_BUILD_CMDS
cd $(@D)/src/platform/sdl2 && \
$(TARGET_CXX) -DSDL2_GLES -std=c++11 `$(STAGING_DIR)/usr/bin/sdl2-config --cflags` -O3 -fno-exceptions -fno-rtti -ffunction-sections -fdata-sections -Wl,--gc-sections -DNDEBUG -D__SDL2__ main.cpp ../../libs/stb_vorbis/stb_vorbis.c ../../libs/minimp3/minimp3.cpp ../../libs/tinf/tinflate.c -I../../ -o OpenLara `$(STAGING_DIR)/usr/bin/sdl2-config --libs` -lGLESv2 -lEGL -lm -lrt -lpthread -lasound -ludev
endef

# SDL2 + GLES3 build
else
define OPENLARA_BUILD_CMDS
cd $(@D)/src/platform/sdl2 && \
$(TARGET_CXX) -DSDL2_GLES -D_GAPI_GLES2 -std=c++11 `$(STAGING_DIR)/usr/bin/sdl2-config --cflags` -O3 -fno-exceptions -fno-rtti -ffunction-sections -fdata-sections -Wl,--gc-sections -DNDEBUG -D__SDL2__ main.cpp ../../libs/stb_vorbis/stb_vorbis.c ../../libs/minimp3/minimp3.cpp ../../libs/tinf/tinflate.c -I../../ -o OpenLara `$(STAGING_DIR)/usr/bin/sdl2-config --libs` -lGLESv2 -lEGL -lm -lrt -lpthread -lasound -ludev
endef
endif

define OPENLARA_INSTALL_TARGET_CMDS
cd $(@D)/src/platform/sdl2 && $(INSTALL) -m 0755 -D ./OpenLara $(TARGET_DIR)/usr/bin/OpenLara
endef

$(eval $(generic-package))
