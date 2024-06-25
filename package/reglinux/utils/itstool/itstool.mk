################################################################################
#
# itstool
#
################################################################################
ITSTOOL_VERSION = 2.0.7
ITSTOOL_SITE = $(call github,itstool,itstool,$(ITSTOOL_VERSION))
ITSTOOL_INSTALL_STAGING = YES
ITSTOOL_AUTORECONF = YES

#ITSTOOL_DEPENDENCIES = libgtk3 libyaml json-glib

ITSTOOL_CONF_OPTS =
#-Dgtkdoc=false -Dtests=false -Dstemmer=false -Dcli=false -Dlzma=enabled -Dzstd=enabled #-Dintrospection=false -Dbuilder=false -Dman=false -Dgtk-doc=false -Drpm=false
HOST_ITSTOOL_CONF_OPTS =
#-Dgtkdoc=false -Dtests=false -Dstemmer=false -Dcli=false -Dlzma=enabled -Dzstd=enabled #-Dintrospection=false -Dbuilder=false -Dman=false -Dgtk-doc=false -Drpm=false

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

$(eval $(autotools-package))
$(eval $(host-autotools-package))
