################################################################################
#
# vdpauinfo
#
################################################################################

VDPAUINFO_VERSION = 1.5
VDPAUINFO_SOURCE = vdpauinfo-$(VDPAUINFO_VERSION).tar.gz
VDPAUINFO_SITE = https://gitlab.freedesktop.org/vdpau/vdpauinfo/-/archive/$(VDPAUINFO_VERSION)
VDPAUINFO_LICENSE = MIT
VDPAUINFO_LICENSE_FILES = COPYING

VDPAUINFO_DEPENDENCIES = libvdpau xlib_libX11

# Force autoreconf because the repository does not ship a pre-generated configure script
VDPAUINFO_AUTORECONF = YES

$(eval $(autotools-package))
