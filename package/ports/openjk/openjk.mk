################################################################################
#
# openjk — Jedi Academy + Jedi Outcast source port
#
################################################################################
# Version: Commits on Oct 10, 2025
OPENJK_VERSION = d1cb662f07dfa4c1999edfb5c1a86fd1c6285372
OPENJK_SITE = https://github.com/JACoders/OpenJK
OPENJK_SITE_METHOD = git
OPENJK_SUPPORTS_IN_SOURCE_BUILD = NO
OPENJK_LICENSE = GPL-2.0
OPENJK_LICENSE_FILES = LICENSE.txt

# host-openjk builds compact_glsl shader compiler needed during target build
OPENJK_DEPENDENCIES = host-openjk jpeg libpng sdl2 zlib

OPENJK_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DBUILD_SHARED_LIBS=OFF \
	-DBuildJK2SPEngine=ON \
	-DBuildJK2SPGame=ON \
	-DBuildJK2SPRdVanilla=ON

# Host build: compact_glsl only
# Depends on mesa3d (target) for GL headers in staging sysroot
# Same approach as Batocera
HOST_OPENJK_DEPENDENCIES = mesa3d
HOST_OPENJK_SUPPORTS_IN_SOURCE_BUILD = NO

HOST_OPENJK_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DBUILD_SHARED_LIBS=OFF \
	-DUseInternalSDL2=ON \
	-DUseInternalJPEG=ON \
	-DUseInternalPNG=ON

define HOST_OPENJK_BUILD_CMDS
	$(HOST_MAKE_ENV) $(MAKE) -C $(HOST_OPENJK_BUILDDIR) compact_glsl
endef

define HOST_OPENJK_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(HOST_OPENJK_BUILDDIR)/compact_glsl \
		$(HOST_DIR)/usr/bin/compact_glsl
endef

define OPENJK_INSTALL_TARGET_CMDS
	-find $(@D)/buildroot-build -maxdepth 1 -name "openjk*" -type f -executable \
		-exec $(INSTALL) -D -m 0755 {} $(TARGET_DIR)/usr/bin/ \;
	-find $(@D)/buildroot-build -maxdepth 1 -name "openjo*" -type f -executable \
		-exec $(INSTALL) -D -m 0755 {} $(TARGET_DIR)/usr/bin/ \;
	-cp -f $(@D)/buildroot-build/*.so $(TARGET_DIR)/usr/lib/ 2>/dev/null || true
endef

$(eval $(cmake-package))
$(eval $(host-cmake-package))
