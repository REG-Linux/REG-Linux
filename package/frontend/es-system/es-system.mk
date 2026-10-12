################################################################################
#
# ES-SYSTEM
#
################################################################################

# branch: main
ES_SYSTEM_VERSION = f7704599c9efbc28c7212328bff12721f682629a
ES_SYSTEM_SITE = $(call github,REG-Linux,es-system,$(ES_SYSTEM_VERSION))
ES_SYSTEM_LICENSE = GPL-3.0-or-later
ES_SYSTEM_LICENSE_FILES = LICENSE
ES_SYSTEM_DEPENDENCIES = reglinux-launcher-defaults
ES_SYSTEM_INSTALL_STAGING = YES

RUSTC_TARGET_PROFILE = $(if $(BR2_ENABLE_DEBUG),debug,release)
ES_SYSTEM_LOCATION = target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)

define ES_SYSTEM_BUILD_CMDS
	# Build host binary (native) for build-time config generation
	cd $(@D) && \
	$(HOST_MAKE_ENV) \
		$(PKG_COMMON_CARGO_ENV) \
		cargo build --offline --release --locked

	# Run host binary to generate configs (replaces python es-system.py)
	# Systems stay XML (rs_systems.cfg); features emit JSON (rs_features.json) directly,
	# replacing the legacy regstation-side convert_features_xml_to_json.py step.
	$(@D)/target/release/es-system --format json \
		$(ES_SYSTEM_PKGDIR)/es_systems.yml \
		$(ES_SYSTEM_PKGDIR)/es_features.yml \
		$(@D)/rs_external_translations.h \
		$(@D)/rs_keys_translations.h \
		$(BR2_EXTERNAL_REGLINUX_PATH)/package \
		$(ES_SYSTEM_PKGDIR)/locales/blacklisted-words.txt \
		$(CONFIG_DIR)/.config \
		$(@D)/rs_systems.cfg \
		$(@D)/rs_features.json \
		$(STAGING_DIR)/usr/share/regmsg/launcher/launcher-defaults.yml \
		$(STAGING_DIR)/usr/share/regmsg/launcher/launcher-defaults-arch.yml \
		$(ES_SYSTEM_PKGDIR)/roms \
		$(@D)/roms $(REGLINUX_SYSTEM_ARCH)

	# Build target binary (cross-compiled) for on-device `es-system regenerate`
	cd $(@D) && \
	$(TARGET_MAKE_ENV) $(TARGET_CONFIGURE_OPTS) \
		$(PKG_CARGO_ENV) \
		$(ES_SYSTEM_CARGO_ENV) \
		cargo build --offline $(if $(BR2_ENABLE_DEBUG),,--release) \
		--manifest-path $(@D)/Cargo.toml --locked
endef

define ES_SYSTEM_INSTALL_STAGING_CMDS
	# Translation headers consumed by regstation xgettext at build time
	mkdir -p $(STAGING_DIR)/usr/share/es-system
	$(INSTALL) -m 0644 $(@D)/rs_external_translations.h $(STAGING_DIR)/usr/share/es-system/
	$(INSTALL) -m 0644 $(@D)/rs_keys_translations.h     $(STAGING_DIR)/usr/share/es-system/
endef

define ES_SYSTEM_INSTALL_TARGET_CMDS
	# Manual on-device regeneration: `es-system regenerate`. Nothing invokes it
	# at boot or otherwise -- the compile-time rs_systems.cfg / rs_features.json
	# below are what a stock image uses.
	$(INSTALL) -D $(@D)/$(ES_SYSTEM_LOCATION)/es-system \
		$(TARGET_DIR)/usr/bin/es-system

	# The same inputs this package just generated from, so a device regenerates
	# byte-identically out of the box. Each is individually overridable by
	# dropping a copy in /userdata/system/configs/es-system/.
	mkdir -p $(TARGET_DIR)/usr/share/es-system
	$(INSTALL) -m 0644 $(ES_SYSTEM_PKGDIR)/es_systems.yml  $(TARGET_DIR)/usr/share/es-system/
	$(INSTALL) -m 0644 $(ES_SYSTEM_PKGDIR)/es_features.yml $(TARGET_DIR)/usr/share/es-system/
	$(INSTALL) -m 0644 $(ES_SYSTEM_PKGDIR)/locales/blacklisted-words.txt $(TARGET_DIR)/usr/share/es-system/

	# BIOS manifest: what each system requires under /userdata/bios. It lives
	# here because it is keyed by es_systems.yml's system names -- a key that
	# does not match one is silently never checked. regmsgd's `bios.check`
	# validates against it; the build host renders the datainit readme from the
	# same file (post-build-script.sh).
	$(INSTALL) -m 0644 -D $(ES_SYSTEM_PKGDIR)/bios-manifest.json \
		$(TARGET_DIR)/usr/share/reglinux/bios-manifest.json
	# Build facts a device cannot reconstruct: which BR2_PACKAGE_* symbols this
	# image was built with (the requireAnyOf gating) and the arch tag.
	grep '^BR2_PACKAGE_.*=y$$' $(CONFIG_DIR)/.config > $(TARGET_DIR)/usr/share/es-system/installed-packages.conf || true
	echo "$(REGLINUX_SYSTEM_ARCH)" > $(TARGET_DIR)/usr/share/es-system/arch.conf

	# Install generated configs
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit
	$(INSTALL) -m 0644 -D $(@D)/rs_systems.cfg	$(TARGET_DIR)/usr/share/regstation/rs_systems.cfg
	$(INSTALL) -m 0644 -D $(@D)/rs_features.json	$(TARGET_DIR)/usr/share/regstation/rs_features.json
	mkdir -p $(@D)/roms # in case there is no rom
	cp -pr $(@D)/roms $(TARGET_DIR)/usr/share/reglinux/datainit/
endef

define ES_SYSTEM_PRUNE_VIDEOS
	find $(TARGET_DIR)/usr/share/reglinux/datainit/roms -type f -name '*.mp4' -delete
endef

# Do NOT bundle if neither ffmpeg variant is built
ifeq ($(BR2_PACKAGE_FFMPEG)$(BR2_PACKAGE_RS_FFMPEG),)
	ES_SYSTEM_POST_INSTALL_TARGET_HOOKS += ES_SYSTEM_PRUNE_VIDEOS
endif

$(eval $(cargo-package))
