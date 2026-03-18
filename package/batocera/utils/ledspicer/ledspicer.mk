################################################################################
#
# ledspicer
#
################################################################################

LEDSPICER_VERSION = 0.7.3
LEDSPICER_SITE = $(call github,meduzapat,LEDSpicer,$(LEDSPICER_VERSION))
LEDSPICER_LICENSE = GPLv3
LEDSPICER_DEPENDENCIES = tinyxml2 libusb udev

# Override data/config directories to use userdata
LEDSPICER_CONF_OPTS = -DPROJECT_DATA_DIR=/userdata/system/configs/ledspicer/
LEDSPICER_CONF_OPTS += -DPROJECT_CONF_DIR=/userdata/system/configs/ledspicer
LEDSPICER_CONF_OPTS += -DCMAKE_CXX_FLAGS='-g0 -O3'

# Device plugins
LEDSPICER_CONF_OPTS += -DENABLE_NANOLED=ON -DENABLE_PACDRIVE=ON -DENABLE_PACLED64=ON
LEDSPICER_CONF_OPTS += -DENABLE_ULTIMATEIO=ON -DENABLE_LEDWIZ32=ON -DENABLE_HOWLER=ON
LEDSPICER_CONF_OPTS += -DENABLE_ADALIGHT=ON

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
LEDSPICER_CONF_OPTS += -DENABLE_PULSEAUDIO=ON
LEDSPICER_DEPENDENCIES += pulseaudio
else
LEDSPICER_CONF_OPTS += -DENABLE_PULSEAUDIO=OFF
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
LEDSPICER_CONF_OPTS += -DENABLE_ALSAAUDIO=ON
LEDSPICER_DEPENDENCIES += alsa-lib
else
LEDSPICER_CONF_OPTS += -DENABLE_ALSAAUDIO=OFF
endif

define LEDSPICER_UDEV_RULE
	mkdir -p $(TARGET_DIR)/etc/udev/rules.d
	cp $(@D)/data/21-ledspicer.rules $(TARGET_DIR)/etc/udev/rules.d/99-ledspicer.rules
endef

define LEDSPICER_SERVICE_INSTALL
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/services
	install -m 0755 $(BR2_EXTERNAL_REGLINUX_PATH)/package/batocera/utils/ledspicer/ledspicer \
		$(TARGET_DIR)/usr/share/reglinux/services/
endef

LEDSPICER_POST_INSTALL_TARGET_HOOKS += LEDSPICER_UDEV_RULE
LEDSPICER_POST_INSTALL_TARGET_HOOKS += LEDSPICER_SERVICE_INSTALL

$(eval $(cmake-package))
