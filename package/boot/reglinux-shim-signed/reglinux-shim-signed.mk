################################################################################
#
# reglinux-shim-signed
#
# Unified package for Microsoft-signed EFI shim binaries (x64 + ia32).
#
# Both arches come from the same Debian bookworm shim generation, so the two
# EFI legs of an image are never a version apart. x64 used to come from Ubuntu
# (1.58+15.8) while ia32 came from Debian; when Debian rotated 15.8 out of its
# pool and ia32 had to move to 16.1, that left the two legs on different shim
# generations - shim 16.x tightens SBAT revocation, so they are better matched.
#
# Debian splits the MOK manager and fallback binaries into a separate
# shim-helpers-<arch>-signed package, unlike Ubuntu which ships them in one, so
# there are four downloads. Both arches share the same two version strings.
#
################################################################################

REGLINUX_SHIM_SIGNED_VERSION = 1.51~1+deb12u1+16.1-2~deb12u1
REGLINUX_SHIM_SIGNED_HELPERS_VERSION = 1+16.1+2~deb12u1

REGLINUX_SHIM_SIGNED_DEBIAN_POOL = https://ftp.debian.org/debian/pool/main/s
REGLINUX_SHIM_SIGNED_SITE = $(REGLINUX_SHIM_SIGNED_DEBIAN_POOL)/shim-signed
REGLINUX_SHIM_SIGNED_SOURCE = shim-signed_$(REGLINUX_SHIM_SIGNED_VERSION)_amd64.deb

REGLINUX_SHIM_SIGNED_DEPENDENCIES = host-sbsigntools

REGLINUX_SHIM_SIGNED_EXTRA_DOWNLOADS = \
	$(REGLINUX_SHIM_SIGNED_DEBIAN_POOL)/shim-signed/shim-signed_$(REGLINUX_SHIM_SIGNED_VERSION)_i386.deb \
	$(REGLINUX_SHIM_SIGNED_DEBIAN_POOL)/shim-helpers-amd64-signed/shim-helpers-amd64-signed_$(REGLINUX_SHIM_SIGNED_HELPERS_VERSION)_amd64.deb \
	$(REGLINUX_SHIM_SIGNED_DEBIAN_POOL)/shim-helpers-i386-signed/shim-helpers-i386-signed_$(REGLINUX_SHIM_SIGNED_HELPERS_VERSION)_i386.deb

REGLINUX_SHIM_SIGNED_TOKEN = $(shell cat /build/gh_token)

define REGLINUX_SHIM_SIGNED_EXTRACT_CMDS
	mkdir -p $(@D)/x64 $(@D)/x64-helpers $(@D)/ia32 $(@D)/ia32-helpers
	dpkg-deb -R $(REGLINUX_SHIM_SIGNED_DL_DIR)/$(REGLINUX_SHIM_SIGNED_SOURCE) $(@D)/x64
	dpkg-deb -R $(REGLINUX_SHIM_SIGNED_DL_DIR)/shim-helpers-amd64-signed_$(REGLINUX_SHIM_SIGNED_HELPERS_VERSION)_amd64.deb $(@D)/x64-helpers
	dpkg-deb -R $(REGLINUX_SHIM_SIGNED_DL_DIR)/shim-signed_$(REGLINUX_SHIM_SIGNED_VERSION)_i386.deb $(@D)/ia32
	dpkg-deb -R $(REGLINUX_SHIM_SIGNED_DL_DIR)/shim-helpers-i386-signed_$(REGLINUX_SHIM_SIGNED_HELPERS_VERSION)_i386.deb $(@D)/ia32-helpers

	# Download reglinux-mok.key from REG-Linux keys repository (if available) to be able to verify signatures of the binaries
	@wget --header="Authorization: token $(REGLINUX_SHIM_SIGNED_TOKEN)" -O $(REGLINUX_SHIM_SIGNED_PKGDIR)/reglinux-mok.key "https://raw.githubusercontent.com/REG-Linux/keys/main/secure-boot/reglinux-mok.key" || true	
endef

define REGLINUX_SHIM_SIGNED_BUILD_CMDS
endef

define REGLINUX_SHIM_SIGNED_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/shim-signed

	# x64: shim, MOK manager, fallback
	cp $(@D)/x64/usr/lib/shim/shimx64.efi.signed        $(BINARIES_DIR)/shim-signed/shimx64.efi
	cp $(@D)/x64-helpers/usr/lib/shim/mmx64.efi.signed  $(BINARIES_DIR)/shim-signed/mmx64.efi
	cp $(@D)/x64-helpers/usr/lib/shim/fbx64.efi.signed  $(BINARIES_DIR)/shim-signed/fbx64.efi

	# ia32: shim, MOK manager, fallback
	cp $(@D)/ia32/usr/lib/shim/shimia32.efi.signed       $(BINARIES_DIR)/shim-signed/shimia32.efi
	cp $(@D)/ia32-helpers/usr/lib/shim/mmia32.efi.signed  $(BINARIES_DIR)/shim-signed/mmia32.efi
	cp $(@D)/ia32-helpers/usr/lib/shim/fbia32.efi.signed  $(BINARIES_DIR)/shim-signed/fbia32.efi
endef

$(eval $(generic-package))
