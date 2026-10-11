################################################################################
#
# touchHLE
#
################################################################################

TOUCHHLE_VERSION = v0.3.0
TOUCHHLE_SITE = https://github.com/touchHLE/touchHLE.git
TOUCHHLE_SITE_METHOD = git
TOUCHHLE_GIT_SUBMODULES = YES
TOUCHHLE_LICENSE = GPLv2
TOUCHHLE_DEPENDENCIES = boost openal sdl2

TOUCHHLE_CARGO_ENV += CMAKE_ARGS="-DALSOFT_BACKEND_SNDIO=OFF -DSDL_SNDIO=OFF"
# The vendored openal-soft uses uint8_t without <cstdint> (GCC 15+)
TOUCHHLE_CARGO_ENV += TARGET_CXXFLAGS="$(TARGET_CXXFLAGS) -include cstdint"

# Patches 002 and 003 edit the vendored sdl2-sys crate; refresh those files'
# checksums or cargo refuses to build it.
TOUCHHLE_SDL2_SYS_PATCHED = \
	SDL/src/audio/pipewire/SDL_pipewire.c \
	SDL/src/joystick/hidapi/SDL_hidapi_steam.c
define TOUCHHLE_REFRESH_SDL2_SYS_CHECKSUM
	$(foreach f,$(TOUCHHLE_SDL2_SYS_PATCHED),
		$(SED) "s|\"$(f)\":\"[0-9a-f]*\"|\"$(f)\":\"$$(sha256sum $(@D)/VENDOR/sdl2-sys/$(f) | cut -d' ' -f1)\"|" \
			$(@D)/VENDOR/sdl2-sys/.cargo-checksum.json$(sep))
endef
TOUCHHLE_POST_PATCH_HOOKS += TOUCHHLE_REFRESH_SDL2_SYS_CHECKSUM

define TOUCHHLE_INSTALL_TARGET_CMDS
        $(INSTALL) -D -m 0755 $(@D)/target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)/touchHLE \
                $(TARGET_DIR)/usr/bin/touchHLE
	# TODO add touchHLE_apps / touchHLE_dylibs / touchHLE_fonts
endef

$(eval $(rust-package))
