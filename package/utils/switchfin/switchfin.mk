################################################################################
#
# switchfin
#
################################################################################
SWITCHFIN_VERSION = 0.8.2
SWITCHFIN_SITE = https://github.com/dragonflylee/switchfin
SWITCHFIN_SITE_METHOD = git
SWITCHFIN_LICENSE = Apache-2.0
SWITCHFIN_DEPENDENCIES = mpv libcurl
SWITCHFIN_GIT_SUBMODULES = YES

SWITCHFIN_SUPPORTS_IN_SOURCE_BUILD = NO

SWITCHFIN_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
SWITCHFIN_CONF_OPTS += -DPLATFORM_DESKTOP=ON
SWITCHFIN_CONF_OPTS += -DUSE_SYSTEM_CURL=ON
SWITCHFIN_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
SWITCHFIN_CONF_OPTS += -DGLFW_BUILD_X11=FALSE

SWITCHFIN_CONF_ENV += LDFLAGS=-lpthread

# TODO enhance by tweaking these
SWITCHFIN_CONF_OPTS += -DUSE_SDL2=ON
SWITCHFIN_CONF_OPTS += -DUSE_GLES2=ON
SWITCHFIN_CONF_OPTS += -DUSE_GLES3=OFF
SWITCHFIN_CONF_OPTS += -DUSE_GL2=OFF
SWITCHFIN_CONF_OPTS += -DUSE_GL3=OFF
SWITCHFIN_CONF_OPTS += -DUSE_GLFW=OFF

define SWITCHFIN_INSTALL_BINARY_RESOURCES
	mkdir -p $(TARGET_DIR)/usr/switchfin
	cp $(@D)/buildroot-build/Switchfin $(TARGET_DIR)/usr/switchfin/switchfin
	cp -r $(@D)/buildroot-build/resources $(TARGET_DIR)/usr/switchfin/

endef

SWITCHFIN_POST_INSTALL_TARGET_HOOKS += SWITCHFIN_INSTALL_BINARY_RESOURCES

$(eval $(cmake-package))
