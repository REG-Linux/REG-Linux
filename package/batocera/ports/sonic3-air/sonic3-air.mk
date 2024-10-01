################################################################################
#
# sonic3-air
#
################################################################################

SONIC3_AIR_VERSION = v24.02.02.0-stable
SONIC3_AIR_SITE = https://github.com/Eukaryot/sonic3air.git
SONIC3_AIR_SITE_METHOD = git
SONIC3_AIR_GIT_SUBMODULES = YES
SONIC3_AIR_LICENSE = GPL-3.0
SONIC3_AIR_LICENSE_FILE = COPYING.txt

# Custom GLES 2.0 cmake
define SONIC3_AIR_ADD_GLES2_CMAKE
	mkdir -p $(@D)/Oxygen/sonic3air/build/_gles2/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/sonic3-air/CMakeLists.txt.gles2 $(@D)/Oxygen/sonic3air/build/_gles2/CMakeLists.txt
endef
SONIC3_AIR_PRE_CONFIGURE_HOOKS += SONIC3_AIR_ADD_GLES2_CMAKE

# CMakeLists.txt in subfolder
ifeq ($(BR2_PACKAGE_XORG7),y)
SONIC3_AIR_SUBDIR = Oxygen/sonic3air/build/_cmake
else
SONIC3_AIR_SUBDIR = Oxygen/sonic3air/build/_gles2
endif

SONIC3_AIR_DEPENDENCIES += alsa-lib libcurl zlib

# Dynamic dependencies
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
SONIC3_AIR_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
SONIC3_AIR_DEPENDENCIES += libgles
endif

# Do not enforce pulseaudio
ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
SONIC3_AIR_DEPENDENCIES += pulseaudio
endif

# Do not enforce X
ifeq ($(BR2_PACKAGE_XORG7),y)
SONIC3_AIR_DEPENDENCIES += xlib_libXxf86vm xlib_libXcomposite libglu
endif

SONIC3_AIR_SUPPORTS_IN_SOURCE_BUILD = NO

SONIC3_AIR_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SONIC3_AIR_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

define SONIC3_AIR_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/sonic3-air
	# copy binary
	cp $(@D)/Oxygen/sonic3air/sonic3air_linux $(TARGET_DIR)/usr/bin/sonic3-air
	# copy config files
	cp $(@D)/Oxygen/sonic3air/config.json $(TARGET_DIR)/usr/bin/sonic3-air
	cp $(@D)/Oxygen/sonic3air/oxygenproject.json $(TARGET_DIR)/usr/bin/sonic3-air
	# copy game resource files
	cp -r $(@D)/Oxygen/sonic3air/data $(TARGET_DIR)/usr/bin/sonic3-air
	cp -r $(@D)/Oxygen/sonic3air/scripts $(TARGET_DIR)/usr/bin/sonic3-air
	cp -r $(@D)/Oxygen/sonic3air/saves $(TARGET_DIR)/usr/bin/sonic3-air
endef

# Remove remastered music on size-constrained platforms (should live in content downloader)
define SONIC3_AIR_REMOVE_REMASTERED_MUSIC
	rm -Rf $(TARGET_DIR)/usr/bin/sonic3-air/data/audio/remastered/
endef

define SONIC3_AIR_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/sonic3-air/sonic3-air.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

SONIC3_AIR_POST_INSTALL_TARGET_HOOKS += SONIC3_AIR_EVMAPY

ifeq ($(BR2_x86_64)$(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
SONIC3_AIR_POST_INSTALL_TARGET_HOOKS += SONIC3_AIR_REMOVE_REMASTERED_MUSIC
endif

$(eval $(cmake-package))
