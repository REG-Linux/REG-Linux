################################################################################
#
# GAMESCOPE
#
################################################################################

GAMESCOPE_VERSION = 3.14.4
GAMESCOPE_SOURCE = gamescope-$(GAMESCOPE_VERSION).tar.gz
GAMESCOPE_SITE = https://github.com/ValveSoftware/gamescope.git
GAMESCOPE_SITE_METHOD = git
GAMESCOPE_GIT_SUBMODULES = YES

GAMESCOPE_LICENSE = MIT
GAMESCOPE_LICENSE_FILES = LICENSE

GAMESCOPE_DEPENDENCIES = wayland wlroots stb sdl2 libdecor glslang spirv-tools xwayland glm

GAMESCOPE_CONF_OPTS += -Denable_openvr_support=false -Denable_gamescope_wsi_layer=true -Denable_gamescope=true -Ddrm_backend=enabled -Dsdl2_backend=enabled

$(eval $(meson-package))
