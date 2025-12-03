################################################################################
#
# regmsg
#
################################################################################

# branch iwd
REGLINUX_MSG_VERSION = 6dffa8004b2c4353baa6d41ab42d30a22242d8bf
REGLINUX_MSG_TOKEN = $(shell cat /build/gh_token)
REGLINUX_MSG_SITE = https://$(REGLINUX_MSG_TOKEN)@github.com/REG-Linux/regmsg
REGLINUX_MSG_SITE_METHOD = git
REGLINUX_MSG_LICENSE = MIT
REGLINUX_MSG_LICENSE_FILES = LICENSE
REGLINUX_MSG_DEPENDENCIES += libdrm

RUSTC_TARGET_PROFILE = $(if $(BR2_ENABLE_DEBUG),,release)
REGLINUX_MSG_LOCATION = target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)
REGLINUX_MSG_CARGO_BUILD_OPTS += --features integrity

define HASH_INTEGRITY_CHECK
	@echo "Creating integrity hash list for reglinux-msg..."

	CURRENTHASH=`b3sum --no-names $(@D)/init/S06regmsgd 2>/dev/null`; \
	if [ -z "$$CURRENTHASH" ]; then echo "Could not get HASH for integrity check!" >&2; exit 1; fi; \
	sed -i "s|___SCRIPT_HASH___|$$CURRENTHASH|" $(@D)/strings.txt
	
	CURRENTHASH=`b3sum --no-names $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/plymouth/config/S002plymouth 2>/dev/null`; \
	if [ -z "$$CURRENTHASH" ]; then echo "Could not get HASH for integrity check!" >&2; exit 1; fi; \
	sed -i "s|___PLYMOUTH_HASH___|$$CURRENTHASH|" $(@D)/strings.txt

	CURRENTHASH=`b3sum --no-names $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/plymouth/config/plymouthd.defaults 2>/dev/null`; \
	if [ -z "$$CURRENTHASH" ]; then echo "Could not get HASH for integrity check!" >&2; exit 1; fi; \
	sed -i "s|___DEFAULTS_HASH___|$$CURRENTHASH|" $(@D)/strings.txt

	CURRENTHASH=`b3sum --no-names $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/plymouth/themes/reglinux/reglinux.plymouth 2>/dev/null`; \
	if [ -z "$$CURRENTHASH" ]; then echo "Could not get HASH for integrity check!" >&2; exit 1; fi; \
	sed -i "s|___THEME_HASH___|$$CURRENTHASH|" $(@D)/strings.txt

	CURRENTHASH=`b3sum --no-names $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/plymouth/themes/reglinux/images/header-image.png 2>/dev/null`; \
	if [ -z "$$CURRENTHASH" ]; then echo "Could not get HASH for integrity check!" >&2; exit 1; fi; \
	sed -i "s|___HEADER_HASH___|$$CURRENTHASH|" $(@D)/strings.txt
endef

REGLINUX_MSG_POST_EXTRACT_HOOKS += HASH_INTEGRITY_CHECK

define REGLINUX_MSG_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsg			$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsgd			$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsg_shell		$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/target/$(RUSTC_TARGET_PROFILE)/libdrmhook.so	$(TARGET_DIR)/usr/lib/
	$(INSTALL) -D $(@D)/target/$(RUSTC_TARGET_PROFILE)/S06regmsgd		$(TARGET_DIR)/etc/init.d/
endef

$(eval $(cargo-package))
