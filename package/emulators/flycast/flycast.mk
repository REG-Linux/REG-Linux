################################################################################
#
# flycast
#
################################################################################
FLYCAST_VERSION = v2.3.2
FLYCAST_SITE = https://github.com/flyinghead/flycast.git
FLYCAST_SITE_METHOD=git
FLYCAST_GIT_SUBMODULES=YES
FLYCAST_LICENSE = GPLv2
FLYCAST_DEPENDENCIES = boost sdl2 libpng libzip libcurl libao libminiupnpc elfutils

FLYCAST_SUPPORTS_IN_SOURCE_BUILD = NO

FLYCAST_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
FLYCAST_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
FLYCAST_CONF_OPTS += -DLIBRETRO=OFF
FLYCAST_CONF_OPTS += -DUSE_HOST_SDL=ON

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    FLYCAST_CONF_OPTS += -DUSE_OPENGL=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
    FLYCAST_CONF_OPTS += -DUSE_GLES=ON -DUSE_GLES2=OFF -DUSE_OPENGL=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    FLYCAST_CONF_OPTS += -DUSE_GLES2=ON -DUSE_GLES=OFF -DUSE_OPENGL=ON
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    FLYCAST_CONF_OPTS += -DUSE_VULKAN=ON
    FLYCAST_DEPENDENCIES += glslang
    FLYCAST_CONF_OPTS += -DUSE_HOST_GLSLANG=ON
else
    FLYCAST_CONF_OPTS += -DUSE_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
    FLYCAST_DEPENDENCIES += libmali
    FLYCAST_CONF_OPTS += -DUSE_MALI=ON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
    FLYCAST_CONF_OPTS += -DRK3399=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3568),y)
    FLYCAST_CONF_OPTS += -DRK3568=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
    FLYCAST_CONF_OPTS += -DRPI4=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
    FLYCAST_CONF_OPTS += -DRPI5=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
    FLYCAST_CONF_OPTS += -DODROIDXU4=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
    FLYCAST_CONF_OPTS += -DS922X=ON
endif

define FLYCAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/flycast $(TARGET_DIR)/usr/bin/flycast
	# evmapy files
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/emulators/flycast/*.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
