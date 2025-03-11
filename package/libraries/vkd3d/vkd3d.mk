################################################################################
#
# vkd3d
#
################################################################################

# Release 1.15
VKD3D_VERSION = 1.15
VKD3D_SOURCE = vkd3d-$(VKD3D_VERSION).tar.xz
VKD3D_SITE = https://dl.winehq.org/vkd3d/source
VKD3D_LICENSE = LGPL-2.1+
VKD3D_LICENSE_FILES = COPYING.LIB LICENSE
VKD3D_DEPENDENCIES = host-bison host-flex spirv-headers host-libtool vulkan-headers vulkan-loader host-wine
VKD3D_CONF_ENV += WIDL="$(BUILD_DIR)/host-wine-$(WINE_VERSION)/tools/widl/widl"
VKD3D_CONF_OPTS = --disable-tests --with-sysroot=$(STAGING_DIR)
VKD3D_AUTORECONF = YES
VKD3D_INSTALL_STAGING = YES

$(eval $(autotools-package))
