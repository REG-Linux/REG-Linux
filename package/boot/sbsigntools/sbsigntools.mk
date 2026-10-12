################################################################################
#
# sbsigntools
#
# Based on buildroot patchwork submission by Thomas Devoogdt
# https://patchwork.ozlabs.org/patch/2177123/
#
################################################################################

SBSIGNTOOLS_VERSION = v0.9.5
SBSIGNTOOLS_SITE = git://git.kernel.org/pub/scm/linux/kernel/git/jejb/sbsigntools.git
SBSIGNTOOLS_LICENSE = GPL-3.0+
SBSIGNTOOLS_LICENSE_FILES = COPYING
SBSIGNTOOLS_AUTORECONF = YES
SBSIGNTOOLS_GIT_SUBMODULES = YES

HOST_SBSIGNTOOLS_DEPENDENCIES = host-pkgconf host-binutils host-gnu-efi host-openssl host-util-linux host-automake host-autoconf

HOST_SBSIGNTOOLS_CONF_ENV = \
	CRTPATH="$(HOST_DIR)/lib/crt0-efi-$(shell uname -m).o" \
	CFLAGS="$(HOST_CFLAGS) \
		-I$(HOST_BINUTILS_DIR)/include \
		-I$(HOST_BINUTILS_DIR)/bfd" \
	ac_cv_header_bfd_h=yes

# Run ccan tree setup and create missing files BEFORE autoreconf
# (POST_PATCH runs after extract+patch, before autoreconf)
define HOST_SBSIGNTOOLS_SETUP_CCAN
	touch $(@D)/AUTHORS $(@D)/ChangeLog
	cd $(@D) && \
		lib/ccan.git/tools/create-ccan-tree \
			--build-type=automake lib/ccan \
			talloc read_write_all build_assert array_size endian
	$(SED) 's|/usr/include/efi|$(HOST_DIR)/include/efi|g' $(@D)/configure.ac
	$(SED) 's|SUBDIRS = lib/ccan src docs tests|SUBDIRS = lib/ccan src|' $(@D)/Makefile.am
	$(SED) 's|AC_CONFIG_FILES(\[Makefile src/Makefile lib/ccan/Makefile\]|AC_CONFIG_FILES([Makefile src/Makefile lib/ccan/Makefile])|;/docs\/Makefile/d' $(@D)/configure.ac
endef
HOST_SBSIGNTOOLS_POST_PATCH_HOOKS += HOST_SBSIGNTOOLS_SETUP_CCAN

$(eval $(host-autotools-package))
