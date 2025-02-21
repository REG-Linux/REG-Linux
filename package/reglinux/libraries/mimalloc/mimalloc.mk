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
MIMALLOC_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
MIMALLOC_CONF_OPTS += -DBUILD_STATIC_LIBS=TRUE
MIMALLOC_CONF_OPTS += -DMI_BUILD_SHARED=OFF
MIMALLOC_CONF_OPTS += -DMI_LIBC_MUSL=ON
MIMALLOC_CONF_OPTS += -DMI_EXTRA_CPPDEFS="-DMI_MUSL_BUILTIN"

$(eval $(cmake-package))
