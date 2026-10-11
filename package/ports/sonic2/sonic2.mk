################################################################################
#
# sonic2 — Sonic the Hedgehog 2 (RSDKv4 Decompilation)
#
################################################################################
# Same engine as sonic2013 (Sonic 1), different output name
SONIC2_VERSION = 1.3.3
SONIC2_SITE = https://github.com/RSDKModding/RSDKv4-Decompilation.git
SONIC2_SITE_METHOD = git
SONIC2_GIT_SUBMODULES = YES
SONIC2_LICENSE = Custom
SONIC2_SUPPORTS_IN_SOURCE_BUILD = NO

SONIC2_DEPENDENCIES = sdl2 libogg libvorbis

SONIC2_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DGAME_INCLUDE_EDITOR=OFF \
	-DRETRO_OUTPUT_NAME=sonic2 \
	-DRETRO_SUBSYSTEM=SDL2

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
SONIC2_DEPENDENCIES += libglew libglu libgl
else
# No desktop GL — disable HW render, use software renderer
SONIC2_CONF_OPTS += -DRETRO_USE_HW_RENDER=OFF
endif

define SONIC2_INSTALL_TARGET_CMDS
	find $(@D)/buildroot-build -name "sonic2" -type f -executable | head -1 | \
		xargs -I{} $(INSTALL) -D -m 0755 {} $(TARGET_DIR)/usr/bin/sonic2
endef

$(eval $(cmake-package))
