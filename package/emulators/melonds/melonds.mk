################################################################################
#
# melonds
#
################################################################################
# Version: 1.1 on Nov 18, 2025
MELONDS_VERSION = 1.1
MELONDS_SITE = https://github.com/melonDS-emu/melonDS.git
MELONDS_SITE_METHOD=git
MELONDS_GIT_SUBMODULES=YES
MELONDS_LICENSE = GPLv2
MELONDS_DEPENDENCIES = sdl2 reglinux-qt6 slirp libepoxy libarchive libenet ecm
MELONDS_DEPENDENCIES += faad2

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
MELONDS_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
MELONDS_DEPENDENCIES += libgles
endif

MELONDS_SUPPORTS_IN_SOURCE_BUILD = NO

MELONDS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
MELONDS_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr"
MELONDS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
MELONDS_CONF_OPTS += -DENABLE_LTO=ON
MELONDS_CONF_OPTS += -DENABLE_LTO_RELEASE=ON

define MELONDS_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/melonDS \
		$(TARGET_DIR)/usr/bin/
endef

define MELONDS_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/melonds/nds.melonds.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

MELONDS_POST_INSTALL_TARGET_HOOKS += MELONDS_POST_PROCESS

$(eval $(cmake-package))
