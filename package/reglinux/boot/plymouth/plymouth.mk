#############################################################
#
# Plymouth
#
#############################################################

PLYMOUTH_VERSION = 24.004.60
PLYMOUTH_SITE = https://gitlab.freedesktop.org/plymouth/plymouth.git
PLYMOUTH_SITE_METHOD = git
PLYMOUTH_DEPENDENCIES += pango cairo libdrm libpng libevdev freetype libxkbcommon xkeyboard-config
PLYMOUTH_PATH = $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/boot/plymouth

PLYMOUTH_CONF_OPTS  = -Dgtk=disabled -Dsystemd-integration=false -Ddocs=false
PLYMOUTH_CONF_OPTS += -Dlogo=/usr/share/pixmaps/reglinux_logo.png

define PLYMOUTH_LOGO
	mkdir -p /usr/share/pixmaps
	cp $(PLYMOUTH_PATH)/images/reglinux_logo.png			$(TARGET_DIR)/usr/share/pixmaps/
endef

define PLYMOUTH_INITD
	install -m 0755 $(PLYMOUTH_PATH)/config/S02plymouth		$(TARGET_DIR)/etc/init.d/
	install -m 0755 $(PLYMOUTH_PATH)/config/plymouthd.defaults	$(TARGET_DIR)/usr/share/plymouth/

	# Themes
	cp -r $(PLYMOUTH_PATH)/themes/*					$(TARGET_DIR)/usr/share/plymouth/themes/
endef

PLYMOUTH_PRE_CONFIGURE_HOOKS += PLYMOUTH_LOGO
PLYMOUTH_POST_INSTALL_TARGET_HOOKS += PLYMOUTH_INITD

$(eval $(meson-package))
