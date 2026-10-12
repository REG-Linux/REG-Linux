################################################################################
#
# reglinux-test
#
################################################################################
REGLINUX_TEST_VERSION = 0.2
REGLINUX_TEST_LICENSE = GPL-3.0
REGLINUX_TEST_SOURCE =
REGLINUX_TEST_DEPENDENCIES = python3 python-pyyaml python-pillow

REGLINUX_TEST_SRC_DIR = $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-test/src
REGLINUX_TEST_TARGET_LIB = $(TARGET_DIR)/usr/lib/reglinux-test
REGLINUX_TEST_TARGET_SHARE = $(TARGET_DIR)/usr/share/reglinux-test
REGLINUX_TEST_WL_PROBE_SRC = $(REGLINUX_TEST_SRC_DIR)/wl-probe

# wl-probe is optional — only built/installed when the target has Wayland.
# Bare-KMS boards (a133, cha, de10nano, jz4770, mini) skip it cleanly.
ifeq ($(BR2_PACKAGE_REGLINUX_TEST_WL_PROBE),y)
REGLINUX_TEST_DEPENDENCIES += wayland wayland-protocols host-wayland

# Build wl-probe out-of-tree in $(@D)/wl-probe so the source tree under
# $(BR2_EXTERNAL_REGLINUX_PATH) stays clean (no generated/, no binary).
define REGLINUX_TEST_BUILD_CMDS
	mkdir -p $(@D)/wl-probe
	cp -a $(REGLINUX_TEST_WL_PROBE_SRC)/Makefile \
		$(REGLINUX_TEST_WL_PROBE_SRC)/main.c \
		$(REGLINUX_TEST_WL_PROBE_SRC)/protocols \
		$(@D)/wl-probe/
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/wl-probe \
		CC="$(TARGET_CC)" \
		PKG_CONFIG="$(HOST_DIR)/bin/pkg-config" \
		WAYLAND_SCANNER="$(HOST_DIR)/bin/wayland-scanner" \
		CFLAGS="$(TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)"
endef

define REGLINUX_TEST_INSTALL_WL_PROBE_CMDS
	$(INSTALL) -m 0755 -D $(@D)/wl-probe/reglinux-test-wl-probe \
		$(TARGET_DIR)/usr/bin/reglinux-test-wl-probe
endef
else
define REGLINUX_TEST_INSTALL_WL_PROBE_CMDS
	@echo "reglinux-test: wl-probe disabled (no Wayland on this target)"
endef
endif

define REGLINUX_TEST_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(REGLINUX_TEST_SRC_DIR)/reglinux-test \
		$(TARGET_DIR)/usr/bin/reglinux-test
	$(REGLINUX_TEST_INSTALL_WL_PROBE_CMDS)
	mkdir -p $(REGLINUX_TEST_TARGET_LIB)/lib/display
	cp -a $(REGLINUX_TEST_SRC_DIR)/lib/. $(REGLINUX_TEST_TARGET_LIB)/lib/
	find $(REGLINUX_TEST_TARGET_LIB) -name __pycache__ -prune -exec rm -rf {} +
	mkdir -p $(REGLINUX_TEST_TARGET_SHARE)/scenarios
	cp -a $(REGLINUX_TEST_SRC_DIR)/scenarios/. \
		$(REGLINUX_TEST_TARGET_SHARE)/scenarios/
endef

$(eval $(generic-package))
