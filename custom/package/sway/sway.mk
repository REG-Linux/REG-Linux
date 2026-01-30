################################################################################
#
# sway
#
################################################################################

SWAY_VERSION = 1.11
SWAY_SITE = https://github.com/swaywm/sway/releases/download/$(SWAY_VERSION)
SWAY_LICENSE = MIT
SWAY_LICENSE_FILES = LICENSE
SWAY_DEPENDENCIES = host-pkgconf wlroots json-c pcre cairo pango basu
SWAY_CONF_OPTS = \
	--buildtype=release \
	-Dtray=disabled \
	-Dwerror=false \
	-Dbash-completions=false \
	-Dzsh-completions=false \
	-Dfish-completions=false \
	-Dman-pages=disabled \
	-Dsd-bus-provider=basu

ifeq ($(BR2_PACKAGE_GDK_PIXBUF),y)
SWAY_CONF_OPTS += -Dgdk-pixbuf=enabled
SWAY_DEPENDENCIES += gdk-pixbuf
else
SWAY_CONF_OPTS += -Dgdk-pixbuf=disabled
endif

ifeq ($(BR2_PACKAGE_BASH_COMPLETION),y)
SWAY_CONF_OPTS += -Dbash-completions=true
else
SWAY_CONF_OPTS += -Dbash-completions=false
endif

ifeq ($(BR2_PACKAGE_SWAYBG),y)
SWAY_CONF_OPTS += -Ddefault-wallpaper=true
else
SWAY_CONF_OPTS += -Ddefault-wallpaper=false
endif

ifeq ($(BR2_PACKAGE_SWAY_SWAYBAR),y)
SWAY_CONF_OPTS += -Dswaybar=true
else
SWAY_CONF_OPTS += -Dswaybar=false
endif

ifeq ($(BR2_PACKAGE_SWAY_SWAYNAG),y)
SWAY_CONF_OPTS += -Dswaynag=true
else
SWAY_CONF_OPTS += -Dswaynag=false
endif

ifeq ($(BR2_PACKAGE_SWAY_SWAYBAR_TRAY),y)
SWAY_CONF_OPTS += -Dtray=enabled
else
SWAY_CONF_OPTS += -Dtray=disabled
endif

# Install only what is needed avoiding systemd files
define SWAY_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D $(@D)/buildroot-build/sway/sway         $(TARGET_DIR)/usr/bin
	$(INSTALL) -D $(@D)/buildroot-build/swaymsg/swaymsg   $(TARGET_DIR)/usr/bin
endef

$(eval $(meson-package))
