#############################################################
#
# Plymouth
#
#############################################################

PLYMOUTH_VERSION = 24.004.60
PLYMOUTH_SITE = https://gitlab.freedesktop.org/plymouth/plymouth.git
PLYMOUTH_SITE_METHOD = git

PLYMOUTH_CONF_OPTS = -Dgtk=disabled -Dsystemd-integration=false -Ddocs=false
PLYMOUTH_DEPENDENCIES += pango libevdev libxkbcommon xkeyboard-config

$(eval $(meson-package))
