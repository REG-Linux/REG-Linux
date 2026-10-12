################################################################################
#
# apotris — Feature-rich Tetris clone
#
################################################################################

APOTRIS_VERSION = v4.1.0
APOTRIS_SITE = https://gitea.com/akouzoukos/apotris
APOTRIS_SITE_METHOD = git
APOTRIS_GIT_SUBMODULES = YES
APOTRIS_LICENSE = GPL-3.0

APOTRIS_DEPENDENCIES = sdl2 sdl2_mixer host-vim opus

define APOTRIS_FIX_PKGCONFIG
	cd $(STAGING_DIR)/usr/lib/pkgconfig && \
		for f in SDL2_mixer.pc SDL2_image.pc SDL2_ttf.pc SDL2_net.pc; do \
			[ -f "$$f" ] && ln -sf "$$f" "$$(echo $$f | tr 'A-Z' 'a-z')" 2>/dev/null || true; \
		done
endef
APOTRIS_PRE_CONFIGURE_HOOKS += APOTRIS_FIX_PKGCONFIG

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
APOTRIS_DEPENDENCIES += libgl
APOTRIS_CONF_OPTS = -Dportmaster=false --wrap-mode=nodownload
else
APOTRIS_CONF_OPTS = -Dportmaster=true --wrap-mode=nodownload
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
APOTRIS_DEPENDENCIES += libgles
else
APOTRIS_DEPENDENCIES += libgl
endif

define APOTRIS_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/Apotris $(TARGET_DIR)/usr/bin/apotris
endef

$(eval $(meson-package))
