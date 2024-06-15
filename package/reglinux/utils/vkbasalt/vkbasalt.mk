################################################################################
#
# GAMESCOPE
#
################################################################################

VKBASALT_VERSION = v0.3.2.10
VKBASALT_SOURCE = vkBasalt-$(VKBASALT_VERSION).tar.gz
VKBASALT_SITE = https://github.com/DadSchoorse/vkBasalt.git
VKBASALT_SITE_METHOD = git
VKBASALT_GIT_SUBMODULES = YES

VKBASALT_LICENSE = Zlib
VKBASALT_LICENSE_FILES = LICENSE

VKBASALT_DEPENDENCIES = gamescope
#VKBASALT_DEPENDENCIES = wayland wlroots stb sdl2 libdecor glslang spirv-tools xwayland glm

#VKBASALT_CONF_OPTS += -Denable_openvr_support=false -Denable_VKBASALT_wsi_layer=true -Denable_gamescope=true -Ddrm_backend=enabled -Dsdl2_backend=enabled

$(eval $(meson-package))
