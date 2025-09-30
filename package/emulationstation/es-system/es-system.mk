################################################################################
#
# ES-SYSTEM
#
################################################################################

ES_SYSTEM_DEPENDENCIES = host-python3 host-python-pyyaml reglinux-configgen host-gettext
ES_SYSTEM_SOURCE=
ES_SYSTEM_VERSION=1.03

ES_SYSTEM_PATH = $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulationstation/es-system

define ES_SYSTEM_BUILD_CMDS
	$(HOST_DIR)/bin/python \
		$(ES_SYSTEM_PATH)/es-system.py \
		$(ES_SYSTEM_PATH)/es_systems.yml        \
		$(ES_SYSTEM_PATH)/es_features.yml       \
		$(@D)/es_external_translations.h \
		$(@D)/es_keys_translations.h \
                $(BR2_EXTERNAL_REGLINUX_PATH)/package \
		$(ES_SYSTEM_PATH)/locales/blacklisted-words.txt \
		$(CONFIG_DIR)/.config \
		$(@D)/es_systems.cfg \
		$(@D)/es_features.cfg \
		$(STAGING_DIR)/usr/share/reglinux/configgen/configgen-defaults.yml \
		$(STAGING_DIR)/usr/share/reglinux/configgen/configgen-defaults-arch.yml \
		$(ES_SYSTEM_PATH)/roms \
		$(@D)/roms $(REGLINUX_SYSTEM_ARCH)
		# translations
		mkdir -p $(ES_SYSTEM_PATH)/locales
		(echo "$(@D)/es_external_translations.h"; echo "$(@D)/es_keys_translations.h") | $(HOST_DIR)/bin/xgettext --language=C --add-comments=TRANSLATION -f - -o $(ES_SYSTEM_PATH)/locales/es-system.pot --no-location --keyword=_
		# remove the pot creation date always changing
		sed -i '/^"POT-Creation-Date: /d' $(ES_SYSTEM_PATH)/locales/es-system.pot

		for PO in $(ES_SYSTEM_PATH)/locales/*/es-system.po; do ($(HOST_DIR)/bin/msgmerge -U --no-fuzzy-matching $${PO} $(ES_SYSTEM_PATH)/locales/es-system.pot && printf "%s " $$(basename $$(dirname $${PO})) && LANG=C $(HOST_DIR)/bin/msgfmt -o /dev/null $${PO} --statistics) || exit 1; done

		# install staging
		mkdir -p $(STAGING_DIR)/usr/share/es-system/locales
		cp $(@D)/es_external_translations.h	$(STAGING_DIR)/usr/share/es-system/
		cp $(@D)/es_keys_translations.h		$(STAGING_DIR)/usr/share/es-system/
		cp -pr $(ES_SYSTEM_PATH)/locales	$(STAGING_DIR)/usr/share/es-system
endef

define ES_SYSTEM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit
	$(INSTALL) -m 0644 -D $(@D)/es_systems.cfg	$(TARGET_DIR)/usr/share/emulationstation/es_systems.cfg
	$(INSTALL) -m 0644 -D $(@D)/es_features.cfg	$(TARGET_DIR)/usr/share/emulationstation/es_features.cfg
	mkdir -p $(@D)/roms # in case there is no rom
	cp -pr $(@D)/roms $(TARGET_DIR)/usr/share/reglinux/datainit/
endef

define ES_SYSTEM_PRUNE_VIDEOS
	find $(TARGET_DIR)/usr/share/reglinux/datainit/roms -type f -name '*.mp4' -delete
endef

# Do NOT bundle if we don't build ffmpeg
ifneq ($(BR2_PACKAGE_FFMPEG),y)
ES_SYSTEM_POST_INSTALL_TARGET_HOOKS += ES_SYSTEM_PRUNE_VIDEOS
endif


$(eval $(generic-package))
