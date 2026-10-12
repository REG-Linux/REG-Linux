################################################################################
#
# asio
#
################################################################################

ASIO_VERSION = 1.38.2
ASIO_SITE = $(call github,chriskohlhoff,asio,asio-$(subst .,-,$(ASIO_VERSION)))
ASIO_LICENSE = BSL-1.0
ASIO_LICENSE_FILES = LICENSE_1_0.txt
ASIO_INSTALL_STAGING = YES

# Standalone asio is header-only, so nothing is compiled and nothing belongs on
# the target. Upstream's autotools build exists only to install the headers and
# fill in asio.pc, and its SUBDIRS reaches into src/, which builds the entire
# example and test suite. Do those two steps directly and skip autoreconf.
ASIO_INSTALL_TARGET = NO

# asio.pc is generated from upstream's own template so its field set stays in
# step with the release. Upstream installs it under $(datadir)/pkgconfig
# because the package is architecture-independent, and buildroot's pkg-config
# wrapper searches usr/share/pkgconfig alongside usr/lib/pkgconfig.
define ASIO_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/include
	cp -a $(@D)/include/asio.hpp $(@D)/include/asio $(STAGING_DIR)/usr/include/
	mkdir -p $(STAGING_DIR)/usr/share/pkgconfig
	sed -e 's|@prefix@|/usr|' \
	    -e 's|@exec_prefix@|$${prefix}|' \
	    -e 's|@includedir@|$${prefix}/include|' \
	    -e 's|@PACKAGE_NAME@|asio|' \
	    -e 's|@PACKAGE_VERSION@|$(ASIO_VERSION)|' \
	    $(@D)/asio.pc.in >$(STAGING_DIR)/usr/share/pkgconfig/asio.pc
endef

$(eval $(generic-package))
