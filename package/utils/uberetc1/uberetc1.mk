################################################################################
#
# host-uberetc1 -- High-quality ETC1 texture compressor for theme assets
#
# Replaces host-etctool (etc2comp). Always runs at maximum quality. Emits
# both .pkm (PKM 1.0) and .pkz (zstd-compressed PKM envelope) sidecars.
#
# Used at build time by package/themes/theme-etc1.inc to pre-compress
# opaque theme textures for GLES2 targets.
#
################################################################################

UBERETC1_VERSION = 5c71f2d34b2329e2c5b9ab523236ce73476fdf83
UBERETC1_SITE = https://github.com/REG-Linux/uberetc1.git
UBERETC1_SITE_METHOD = git
UBERETC1_GIT_SUBMODULES = NO
UBERETC1_LICENSE = Apache-2.0
UBERETC1_LICENSE_FILES = LICENSE

HOST_UBERETC1_DEPENDENCIES = host-zstd

HOST_UBERETC1_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release

define HOST_UBERETC1_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(@D)/uberetc1 $(HOST_DIR)/bin/uberetc1
endef

$(eval $(host-cmake-package))
