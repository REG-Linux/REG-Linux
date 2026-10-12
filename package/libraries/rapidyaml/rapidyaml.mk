################################################################################
#
# rapidyaml
#
################################################################################

RAPIDYAML_VERSION = v0.9.0
RAPIDYAML_SITE = https://github.com/biojppm/rapidyaml.git
RAPIDYAML_SITE_METHOD = git
RAPIDYAML_GIT_SUBMODULES = YES
RAPIDYAML_LICENSE = MIT
RAPIDYAML_LICENSE_FILES = LICENSE.txt

RAPIDYAML_INSTALL_STAGING = YES
RAPIDYAML_SUPPORTS_IN_SOURCE_BUILD = NO

RAPIDYAML_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
RAPIDYAML_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
RAPIDYAML_CONF_OPTS += -DRYML_BUILD_TOOLS=OFF
RAPIDYAML_CONF_OPTS += -DRYML_BUILD_API=OFF

$(eval $(cmake-package))
