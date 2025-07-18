################################################################################
#
# libretro-clownmdemu
#
################################################################################

LIBRETRO_CLOWNMDEMU_VERSION = v1.4
LIBRETRO_CLOWNMDEMU_SITE = https://github.com/Clownacy/clownmdemu-libretro
LIBRETRO_CLOWNMDEMU_SITE_METHOD=git
LIBRETRO_CLOWNMDEMU_GIT_SUBMODULES=YES
LIBRETRO_CLOWNMDEMU_LICENSE = GPLv2

LIBRETRO_CLOWNMDEMU_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_CLOWNMDEMU_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
LIBRETRO_CLOWNMDEMU_CONF_OPTS += -DCMAKE_SYSTEM_NAME=Linux
LIBRETRO_CLOWNMDEMU_CONF_OPTS += -DCMAKE_C_FLAGS="$(LIBRETRO_CLOWNMDEMU_TARGET_CFLAGS)"
LIBRETRO_CLOWNMDEMU_CONF_OPTS +=  -DCMAKE_CXX_FLAGS="$(LIBRETRO_CLOWNMDEMU_TARGET_CFLAGS)"

LIBRETRO_CLOWNMDEMU_TARGET_CFLAGS = $(TARGET_CFLAGS)

define LIBRETRO_CLOWNMDEMU_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/clownmdemu_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/clownmdemu_libretro.so
endef

$(eval $(cmake-package))
