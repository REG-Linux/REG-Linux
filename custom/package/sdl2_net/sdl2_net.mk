################################################################################
#
# sdl2_net
#
################################################################################

SDL2_NET_VERSION = 2.2.0
SDL2_NET_SOURCE = SDL2_net-$(SDL2_NET_VERSION).tar.gz
SDL2_NET_SITE = http://www.libsdl.org/projects/SDL_net/release
SDL2_NET_LICENSE = Zlib
SDL2_NET_LICENSE_FILES = LICENSE.txt
SDL2_NET_INSTALL_STAGING = YES
SDL2_NET_DEPENDENCIES = sdl2 host-pkgconf

# Same fix as sdl2_image: the autotools install bakes the target's exec-prefix
# into the installed CMake config, which ends up with
#     set(exec_prefix "/usr")
#     set(libdir "${exec_prefix}/lib")
# so find_package(SDL2_net CONFIG) hands every consumer an IMPORTED_LOCATION of
# /usr/lib/libSDL2_net.so -- a path that only exists on the target. Under the
# Makefile generator that becomes a file dependency nothing can build.
# 'prefix', set immediately above it, is already derived from the config file's
# own location; upstream SDL2 fixed this by spelling it
# set(exec_prefix ${PACKAGE_PREFIX_DIR}), but the satellite libraries never
# followed. Point exec_prefix at the relocatable prefix so libdir lands inside
# the sysroot.
define SDL2_NET_FIXUP_CMAKE_EXEC_PREFIX
	$(SED) 's|^set(exec_prefix "/usr")|set(exec_prefix "$${prefix}")|' \
		$(STAGING_DIR)/usr/lib/cmake/SDL2_net/sdl2_net-config.cmake
endef
SDL2_NET_POST_INSTALL_STAGING_HOOKS += SDL2_NET_FIXUP_CMAKE_EXEC_PREFIX

$(eval $(autotools-package))
