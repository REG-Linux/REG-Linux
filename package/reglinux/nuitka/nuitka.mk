################################################################################
#
# Nuitka
#
################################################################################

NUITKA_VERSION = 2.1.6
NUITKA_SOURCE = $(NUITKA_VERSION).tar.gz
NUITKA_SITE = https://github.com/Nuitka/Nuitka/archive/refs/tags
NUITKA_SETUP_TYPE = setuptools host-python3 python3
NUITKA_LICENSE_FILES = LICENSE
NUITKA_DEPENDENCIES += host-patchelf host-zstd host-python-pip
NUITKA_SETUP_TYPE = setuptools

define NUIKA_INSTALL_PIP_ZSTANDARD
	$(HOST_DIR)/usr/bin/pip install zstandard
	$(HOST_DIR)/usr/bin/pip install ordered-set
endef

NUITKA_PRE_CONFIGURE_HOOKS += NUIKA_INSTALL_PIP_ZSTANDARD

$(eval $(python-package))
$(eval $(host-python-package))
