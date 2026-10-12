################################################################################
#
# ioquake3
#
################################################################################
# Version: Commit on Jul 9, 2026
IOQUAKE3_VERSION = 67e4fa978530ae0a3f62fedb0a26ac4797443429
IOQUAKE3_SITE = $(call github,ioquake,ioq3,$(IOQUAKE3_VERSION))
IOQUAKE3_LICENSE = GPL-2.0
IOQUAKE3_LICENSE_FILE = COPYING.txt

IOQUAKE3_DEPENDENCIES = sdl2 libogg libvorbis opus opusfile jpeg libcurl

IOQUAKE3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
IOQUAKE3_CONF_OPTS += -DBUILD_SERVER=OFF
IOQUAKE3_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
IOQUAKE3_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
IOQUAKE3_CONF_OPTS += -DUSE_INTERNAL_LIBS=OFF
IOQUAKE3_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/share/reglinux/datainit/roms/quake3/"

# GCC 15 LTO workaround on rv64gc
ifeq ($(BR2_riscv),y)
IOQUAKE3_CONF_OPTS += -DCMAKE_C_FLAGS="-mno-relax"
IOQUAKE3_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-mno-relax"
endif

# Installed under datainit so first-boot populate lands the binary and its
# renderer/mod modules straight in /userdata/roms/quake3 (see
# board/fsoverlay/etc/init.d/S12populateshare) instead of the launcher
# mirroring them there on every run. The bin symlink points into that
# /userdata location so regmsgd's /usr/bin capability scan can see it.
define IOQUAKE3_INSTALL_BIN_SYMLINK
	ln -sf /userdata/roms/quake3/ioquake3 $(TARGET_DIR)/usr/bin/ioquake3
endef
IOQUAKE3_POST_INSTALL_TARGET_HOOKS += IOQUAKE3_INSTALL_BIN_SYMLINK

$(eval $(cmake-package))
