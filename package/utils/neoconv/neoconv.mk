################################################################################
#
# neoconv
#
################################################################################

NEOCONV_VERSION = aa7b6e6d66e0a29386acaa8d12e91e60205106b8
NEOCONV_SITE = $(call github,carmiker,neoconv,$(NEOCONV_VERSION))
NEOCONV_LICENSE = BSD-3-Clause (neoconv), MIT (bundled miniz)
NEOCONV_LICENSE_FILES = LICENSE miniz/LICENSE

NEOCONV_AUTORECONF = YES
# PKG_PROG_PKG_CONFIG probes for an external miniz at configure time; falls
# back to the bundled miniz/ sources when it isn't found (never the case here).
NEOCONV_DEPENDENCIES = host-pkgconf
HOST_NEOCONV_DEPENDENCIES = host-pkgconf

# No libneoconv shared library please, single executable
NEOCONV_CONF_OPTS = --disable-shared --enable-static

$(eval $(autotools-package))
$(eval $(host-autotools-package))
