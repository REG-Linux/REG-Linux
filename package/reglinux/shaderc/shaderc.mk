################################################################################
#
# Google ShaderC
#
################################################################################
SHADERC_VERSION = v2024.0
SHADERC_SITE = https://github.com/google/shaderc.git
SHADERC_SITE_METHOD=git
SHADERC_GIT_SUBMODULES = YES
SHADERC_LICENSE = Apache License 2.0
SHADERC_DEPENDENCIES =

SHADERC_SUPPORTS_IN_SOURCE_BUILD = NO

SHADERC_INSTALL_STAGING = YES

SHADERC_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
SHADERC_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
SHADERC_CONF_OPTS += -DSHADERC_SKIP_TESTS=TRUE
SHADERC_CONF_OPTS += -DSHADERC_SKIP_EXAMPLES=TRUE

SHADERC_CONF_ENV += LDFLAGS=-lpthread

define SHADERC_GIT_SYNC_DEPS
	cd $(@D) && ./utils/git-sync-deps
endef

SHADERC_PRE_CONFIGURE_HOOKS += SHADERC_GIT_SYNC_DEPS

$(eval $(cmake-package))
