################################################################################
#
# appstream
#
################################################################################
APPSTREAM_VERSION = v1.0.3
APPSTREAM_SITE = $(call github,ximion,appstream,$(APPSTREAM_VERSION))
APPSTREAM_INSTALL_STAGING = YES

APPSTREAM_DEPENDENCIES = itstool libxmlb host-appstream
HOST_APPSTREAM_DEPENDENCIES = host-libxmlb host-itstool

APPSTREAM_CONF_OPTS = -Dgir=false -Dstemming=false -Dsystemd=false -Dzstd-support=true -Ddocs=false -Dapidocs=false -Dinstall-docs=false #stemmer=false -Dintrospection=false -Dbuilder=false -Dman=false -Dgtk-doc=false -Drpm=false
HOST_APPSTREAM_CONF_OPTS = -Dgir=false -Dstemming=false -Dsystemd=false -Dzstd-support=true -Ddocs=false -Dapidocs=false -Dinstall-docs=false

APPSTREAM_CONF_ENV = LD_LIBRARY_PATH=$(HOST_DIR)/usr/lib:$(LD_LIBRARY_PATH) PATH=$(HOST_DIR)/usr/bin:$(PATH)

$(eval $(meson-package))
$(eval $(host-meson-package))
