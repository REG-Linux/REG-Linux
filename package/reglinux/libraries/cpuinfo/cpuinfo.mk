################################################################################
#
# cpuinfo
#
################################################################################
CPUINFO_VERSION = 05332fd802d9109a2a151ec32154b107c1e5caf9
CPUINFO_SITE = https://github.com/pytorch/cpuinfo.git
CPUINFO_SITE_METHOD = git
CPUINFO_LICENSE = BSD

CPUINFO_SUPPORTS_IN_SOURCE_BUILD = NO
CPUINFO_INSTALL_STAGING = YES

CPUINFO_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
CPUINFO_CONF_OPTS += -DBUILD_SHARED_LIBS=TRUE

CPUINFO_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
