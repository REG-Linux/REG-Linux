################################################################################
#
# semver
#
################################################################################
# Pinned to the tag Ymir builds against (vcpkg/ports/neargye-semver).
# Ymir is the only consumer, and it calls semver::detail::compare_parsed()
# with a version_compare_option that v1.0.0 dropped, so a newer semver
# breaks apps/ymir-sdl3/src/app/services/update_checker_service.cpp.
SEMVER_VERSION = v1.0.0-rc
SEMVER_SITE = $(call github,Neargye,semver,$(SEMVER_VERSION))
SEMVER_LICENSE = MIT

SEMVER_SUPPORTS_IN_SOURCE_BUILD = NO
SEMVER_INSTALL_STAGING = YES

SEMVER_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
# Header-only. This tag turns examples and tests on whenever it is the
# top-level project, which it always is here, and 'perform tests' means
# running target binaries on the build host.
SEMVER_CONF_OPTS += -DSEMVER_OPT_INSTALL=ON
SEMVER_CONF_OPTS += -DSEMVER_OPT_BUILD_EXAMPLES=OFF
SEMVER_CONF_OPTS += -DSEMVER_OPT_BUILD_TESTS=OFF

$(eval $(cmake-package))
