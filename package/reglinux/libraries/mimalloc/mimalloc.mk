################################################################################
#
# mimalloc
#
################################################################################
MIMALLOC_VERSION = v2.1.9
MIMALLOC_SITE = $(call github,microsoft,mimalloc,$(MIMALLOC_VERSION))
MIMALLOC_LICENSE = MIT

MIMALLOC_SUPPORTS_IN_SOURCE_BUILD = NO
MIMALLOC_INSTALL_STAGING = YES

MIMALLOC_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release

# Specify if we build for musl libc or not
ifeq ($(BR2_PACKAGE_MUSL),y)
MIMALLOC_CONF_OPTS += -DMI_LIBC_MUSL=ON
else
MIMALLOC_CONF_OPTS += -DMI_LIBC_MUSL=OFF
endif

$(eval $(cmake-package))
