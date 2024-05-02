################################################################################
#
# Nuitka
#
################################################################################

NUITKA_VERSION = 6a1239c1f505e7d9e2c1873f3211f79f8e671d7c
NUITKA_TOKEN = $(shell cat /build/gh_token)
NUITKA_SITE = https://$(NUITKA_TOKEN)@github.com/REG-Linux/Nuitka.git
NUITKA_SITE_METHOD = git
NUITKA_GIT_SUBMODULES = YES
NUITKA_SETUP_TYPE = setuptools host-python3 python3
NUITKA_LICENSE_FILES = LICENSE
NUITKA_DEPENDENCIES += patchelf host-patchelf host-zstd host-python-pip python-pip
NUITKA_SETUP_TYPE = setuptools

define NUIKA_INSTALL_DEPS
	$(HOST_DIR)/usr/bin/pip install ordered-set
	$(HOST_DIR)/usr/bin/pip install zstandard
endef

NUITKA_PRE_CONFIGURE_HOOKS += NUIKA_INSTALL_DEPS

$(eval $(python-package))
$(eval $(host-python-package))
