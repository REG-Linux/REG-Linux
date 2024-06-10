#############################################################
#
# Plymouth
#
#############################################################

PLYMOUTH_VERSION = 24.004.60
PLYMOUTH_SITE = https://gitlab.freedesktop.org/plymouth/plymouth.git
PLYMOUTH_SITE_METHOD = git
PLYMOUTH_DEPENDENCIES += pango libpng libevdev freetype libxkbcommon xkeyboard-config
PLYMOUTH_PATH = $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/boot/plymouth

PLYMOUTH_CONF_OPTS  = -Dgtk=disabled -Dsystemd-integration=false -Ddocs=false

define PLYMOUTH_INITD
	install -m 0755 $(PLYMOUTH_PATH)/config/S02plymouth		$(TARGET_DIR)/etc/init.d/
	install -m 0755 $(PLYMOUTH_PATH)/config/plymouthd.defaults	$(TARGET_DIR)/usr/share/plymouth/
	cp -r $(PLYMOUTH_PATH)/themes/*					$(TARGET_DIR)/usr/share/plymouth/themes/
endef

PLYMOUTH_POST_INSTALL_TARGET_HOOKS += PLYMOUTH_INITD

$(eval $(meson-package))
