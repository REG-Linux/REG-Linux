################################################################################
#
# libxmlb
#
################################################################################
LIBXMLB_VERSION = 0.3.19
LIBXMLB_SITE = $(call github,ximion,appstream,$(LIBXMLB_VERSION))
LIBXMLB_INSTALL_STAGING = YES

#LIBXMLB_DEPENDENCIES = libgtk3 libyaml json-glib

LIBXMLB_CONF_OPTS = -Dgtkdoc=false -Dtests=false -Dstemmer=false -Dcli=false -Dlzma=enabled -Dzstd=enabled #-Dintrospection=false -Dbuilder=false -Dman=false -Dgtk-doc=false -Drpm=false
HOST_LIBXMLB_CONF_OPTS = -Dgtkdoc=false -Dtests=false -Dstemmer=false -Dcli=false -Dlzma=enabled -Dzstd=enabled #-Dintrospection=false -Dbuilder=false -Dman=false -Dgtk-doc=false -Drpm=false

#option('gtkdoc',type : 'boolean', value : true, description : 'enable developer documentation')
#option('introspection', type : 'boolean', value : true, description : 'generate GObject Introspection data')
#option('tests', type : 'boolean', value : true, description : 'enable tests')
#option('stemmer', type : 'boolean', value : false, description : 'enable stemmer support')
#option('cli', type : 'boolean', value : true, description : 'build and install the xb-tool CLI')
#option('lzma',
#  type: 'feature',
#  description : 'enable lzma (xz) support',
#)
#option('zstd',
#  type: 'feature',
#  description: 'enable zstd support',
#  deprecated: {
#    'true': 'enabled',
#    'false': 'disabled',
#  },

$(eval $(meson-package))
$(eval $(host-meson-package))
