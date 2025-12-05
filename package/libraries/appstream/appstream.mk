################################################################################
#
# appstream
#
################################################################################
APPSTREAM_VERSION = v1.0.4
APPSTREAM_SITE = $(call github,ximion,appstream,$(APPSTREAM_VERSION))
APPSTREAM_INSTALL_STAGING = YES

APPSTREAM_DEPENDENCIES = itstool libxmlb libcurl libidn2 host-appstream libyaml gperf brotli zstd
APPSTREAM_CONF_OPTS = -Dgir=false -Dstemming=false -Dsystemd=false -Dzstd-support=true -Ddocs=false -Dapidocs=false -Dinstall-docs=false
#stemmer=false -Dintrospection=false -Dbuilder=false -Dman=false -Dgtk-doc=false -Drpm=false

APPSTREAM_CONF_ENV = LD_LIBRARY_PATH=$(HOST_DIR)/usr/lib:$(LD_LIBRARY_PATH) PATH=$(HOST_DIR)/usr/bin:$(PATH)

$(eval $(meson-package))

HOST_APPSTREAM_DEPENDENCIES = host-libxmlb host-itstool host-libidn2 host-libyaml host-gperf host-brotli host-zstd
HOST_APPSTREAM_CONF_OPTS = -Dgir=false -Dstemming=false -Dsystemd=false -Dzstd-support=true -Ddocs=false -Dapidocs=false -Dinstall-docs=false
$(eval $(host-meson-package))
