################################################################################
#
# sdl12-compat
#
# SDL 1.2 for the glibc sidecar: libSDL-1.2.so.0 on top of the sidecar's SDL2,
# so SDL 1.2 ports get KMS/DRM, Wayland, the GPU renderer and pulse audio like
# the SDL2 ones (SDL 1.2.15 itself has none of these here). It loads
# libSDL2-2.0.so.0 at run time. Headers and sdl-config go to staging for the
# SDL 1.2 add-ons (sdl-*-compat).
#
################################################################################

SDL12_COMPAT_VERSION = 1.2.78
SDL12_COMPAT_SITE = $(call github,libsdl-org,sdl12-compat,release-$(SDL12_COMPAT_VERSION))
SDL12_COMPAT_LICENSE = Zlib
SDL12_COMPAT_LICENSE_FILES = LICENSE.txt
SDL12_COMPAT_INSTALL_STAGING = YES
SDL12_COMPAT_DEPENDENCIES = sdl2
SDL12_COMPAT_CONFIG_SCRIPTS = sdl-config

SDL12_COMPAT_CONF_OPTS = \
	-DSDL12TESTS=OFF \
	-DSDL12DEVEL=ON \
	-DSTATICDEVEL=OFF \
	-DSDL2_INCLUDE_DIR=$(STAGING_DIR)/usr/include/SDL2

# sdl-config's libdir and includedir are absolute: make them follow prefix,
# which buildroot points at staging
define SDL12_COMPAT_RELATIVE_SDL_CONFIG
	$(SED) 's|^libdir=.*|libdir=$${exec_prefix}/lib|; s|^includedir=.*|includedir=$${prefix}/include|' \
		$(@D)/sdl-config.in
endef
SDL12_COMPAT_PRE_CONFIGURE_HOOKS += SDL12_COMPAT_RELATIVE_SDL_CONFIG

$(eval $(cmake-package))
