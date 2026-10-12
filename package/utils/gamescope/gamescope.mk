################################################################################
#
# GAMESCOPE
#
################################################################################

GAMESCOPE_VERSION = 3.16.29
GAMESCOPE_SOURCE = gamescope-$(GAMESCOPE_VERSION).tar.gz
GAMESCOPE_SITE = https://github.com/ValveSoftware/gamescope.git
GAMESCOPE_SITE_METHOD = git
GAMESCOPE_GIT_SUBMODULES = YES

GAMESCOPE_LICENSE = MIT
GAMESCOPE_LICENSE_FILES = LICENSE

GAMESCOPE_DEPENDENCIES = wayland wlroots stb sdl2 libdecor glslang spirv-tools xwayland glm xlib_libXres xlib_libXmu xlib_libXcomposite xlib_libXtst 
GAMESCOPE_DEPENDENCIES += reglinux-luajit libcap pipewire libliftoff

GAMESCOPE_CONF_OPTS += -Denable_openvr_support=false
GAMESCOPE_CONF_OPTS += -Denable_gamescope_wsi_layer=true
GAMESCOPE_CONF_OPTS += -Denable_gamescope=true
GAMESCOPE_CONF_OPTS += -Ddrm_backend=enabled
GAMESCOPE_CONF_OPTS += -Dsdl2_backend=enabled
GAMESCOPE_CONF_OPTS += -Denable_tests=false
$(eval $(meson-package))
