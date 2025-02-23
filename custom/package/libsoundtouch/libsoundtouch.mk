################################################################################
#
# libsoundtouch
#
################################################################################

LIBSOUNDTOUCH_VERSION = 2.3.3
LIBSOUNDTOUCH_SOURCE = soundtouch-$(LIBSOUNDTOUCH_VERSION).tar.gz
LIBSOUNDTOUCH_SITE = https://www.surina.net/soundtouch
LIBSOUNDTOUCH_LICENSE = LGPL-2.1+
LIBSOUNDTOUCH_LICENSE_FILES = COPYING.TXT
LIBSOUNDTOUCH_INSTALL_STAGING = YES

# REG
LIBSOUNDTOUCH_SUPPORTS_IN_SOURCE_BUILD = NO
LIBSOUNDTOUCH_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
LIBSOUNDTOUCH_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
LIBSOUNDTOUCH_CONF_OPTS += -DSOUNDTOUCH_DLL=ON
LIBSOUNDTOUCH_CONF_OPTS += -DOPENMP=ON

$(eval $(cmake-package))
