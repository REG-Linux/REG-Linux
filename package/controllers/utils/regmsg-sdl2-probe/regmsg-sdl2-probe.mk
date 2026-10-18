################################################################################
#
# regmsg-sdl2-probe
#
################################################################################

REGMSG_SDL2_PROBE_VERSION = 1.0.0
REGMSG_SDL2_PROBE_LICENSE = MIT
REGMSG_SDL2_PROBE_LICENSE_FILES = LICENSE
REGMSG_SDL2_PROBE_SOURCE =
REGMSG_SDL2_PROBE_DEPENDENCIES = sdl2

REGMSG_SDL2_PROBE_PKGDIR = $(BR2_EXTERNAL_REGLINUX_PATH)/package/controllers/utils/regmsg-sdl2-probe

# No download — the single C source ships in-tree. Stage it (and the LICENSE,
# so legal-info can find it) into the build dir.
define REGMSG_SDL2_PROBE_EXTRACT_CMDS
	cp -avf $(REGMSG_SDL2_PROBE_PKGDIR)/src/* $(@D)
	cp -avf $(REGMSG_SDL2_PROBE_PKGDIR)/LICENSE $(@D)
endef

# Compile against the target SDL2 (flags via the staged sdl2-config).
define REGMSG_SDL2_PROBE_BUILD_CMDS
	$(TARGET_CC) $(TARGET_CFLAGS) \
		`$(STAGING_DIR)/usr/bin/sdl2-config --cflags` \
		-o $(@D)/regmsg-sdl2-probe $(@D)/regmsg-sdl2-probe.c \
		`$(STAGING_DIR)/usr/bin/sdl2-config --libs` \
		$(TARGET_LDFLAGS)
endef

define REGMSG_SDL2_PROBE_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/regmsg-sdl2-probe \
		$(TARGET_DIR)/usr/bin/regmsg-sdl2-probe
endef

$(eval $(generic-package))
