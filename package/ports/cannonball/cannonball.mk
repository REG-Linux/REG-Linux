################################################################################
#
# cannonball
#
################################################################################
# Version.: Commits on Feb 1, 2026
CANNONBALL_VERSION = v1.4
CANNONBALL_SITE = $(call github,J1mbo,cannonball-se,$(CANNONBALL_VERSION))
CANNONBALL_LICENSE = GPLv2
CANNONBALL_DEPENDENCIES = sdl2 boost tinyxml2

CANNONBALL_TARGET = sdl2gles

ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
CANNONBALL_DEPENDENCIES += libexecinfo
CANNONBALL_DEPENDENCIES += libbacktrace
endif

ifeq ($(BR2_PACKAGE_MPG123),y)
CANNONBALL_DEPENDENCIES += mpg123
else
CANNONBALL_CONF_OPTS += -DWITH_MP3=OFF
endif

ifeq ($(BR2_x86_64),y)
CANNONBALL_TARGET = sdl2gl
endif

# Build as release with proper target and paths
CANNONBALL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DTARGET=$(CANNONBALL_TARGET)
CANNONBALL_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
CANNONBALL_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
CANNONBALL_CONF_OPTS += -DWITH_MARCH_NATIVE=OFF
CANNONBALL_CONF_OPTS += -Droms_directory=/userdata/roms/cannonball/
CANNONBALL_CONF_OPTS += -Dxml_directory=/userdata/system/configs/cannonball/
CANNONBALL_CONF_OPTS += -Dres_directory=/userdata/system/configs/cannonball/


# Enabling LTO as hires mode tends to be slow, it does help video rendering loops
CANNONBALL_EXE_LINKER_FLAGS += -flto=auto
CANNONBALL_SHARED_LINKER_FLAGS += -flto=auto
CANNONBALL_CONF_OPTS += -DCMAKE_CXX_FLAGS=-flto=auto
CANNONBALL_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="$(CANNONBALL_EXE_LINKER_FLAGS)"
CANNONBALL_CONF_OPTS += -DCMAKE_SHARED_LINKER_FLAGS="$(CANNONBALL_SHARED_LINKER_FLAGS)"

# We need to build out-of-tree
CANNONBALL_SUPPORTS_IN_SOURCE_BUILD = NO

define CANNONBALL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(CANNONBALL_SUBDIR)/buildroot-build/cannonball-se $(TARGET_DIR)/usr/bin/cannonball
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/cannonball/res/
	$(INSTALL) -D $(@D)/$(CANNONBALL_SUBDIR)/buildroot-build/tilemap.bin \
	    $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/cannonball/
	$(INSTALL) -D $(@D)/$(CANNONBALL_SUBDIR)/buildroot-build/tilepatch.bin \
	    $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/cannonball/
	$(INSTALL) -D $(@D)/res/config.xml \
	    $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/cannonball/config_help.txt

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/cannonball/cannonball.cannonball.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
