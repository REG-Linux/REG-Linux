################################################################################
#
# quakespasm
#
################################################################################

QUAKESPASM_VERSION = 0.96.3
QUAKESPASM_SITE = https://downloads.sourceforge.net/project/quakespasm/Source
QUAKESPASM_SOURCE = quakespasm-$(QUAKESPASM_VERSION).tar.gz
QUAKESPASM_LICENSE = GPL-2.0
QUAKESPASM_LICENSE_FILES = COPYING

QUAKESPASM_DEPENDENCIES = sdl2 sdl2_mixer

# GL vs GLES
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
QUAKESPASM_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
QUAKESPASM_DEPENDENCIES += libgles gl4es
endif

define QUAKESPASM_CONFIGURE_CMDS
endef

define QUAKESPASM_BUILD_CMDS
	cd $(@D) && \
	SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl2-config $(MAKE) -C Quake \
	USE_SDL2=1 \
	DO_USERDIRS=1 \
	CC="$(TARGET_CC)" \
	CPPFLAGS="$(TARGET_CFLAGS)" \
	LDFLAGS="$(TARGET_LDFLAGS)" \
	STRIP="$(TARGET_STRIP)" \
	$(JOBS)
endef


define QUAKESPASM_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m0755 $(@D)/Quake/quakespasm $(TARGET_DIR)/usr/bin/quakespasm
endef

$(eval $(generic-package))
