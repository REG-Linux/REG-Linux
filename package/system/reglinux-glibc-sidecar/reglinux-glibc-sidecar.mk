################################################################################
#
# reglinux-glibc-sidecar
#
# glibc userland for the musl boards, mounted read-only on /usr/glibc. glibc
# itself comes relocated from glibc-sidecar; everything else is a normal
# buildroot package. The packages below that load plugins or config by
# absolute path get those paths moved under /usr/glibc here, so they never
# see the musl system's /usr/lib/<plugins> or /etc/<config>. pack.sh (the
# config's post-image script) lays out and checks the squashfs.
#
# Audio: no PipeWire libraries in the sidecar. ALSA's default device is the
# pulse plugin, and programs linking libpulse use it directly; both reach REG's
# pipewire-pulse socket.
#
################################################################################

REGLINUX_GLIBC_SIDECAR_VERSION = 1.0
REGLINUX_GLIBC_SIDECAR_SOURCE =
REGLINUX_GLIBC_SIDECAR_LICENSE = GPL
REGLINUX_GLIBC_SIDECAR_DEPENDENCIES = glibc-sidecar
ifeq ($(BR2_PACKAGE_WAYLAND),y)
REGLINUX_GLIBC_SIDECAR_DEPENDENCIES += wayland
endif

ifeq ($(BR2_PACKAGE_REGLINUX_GLIBC_SIDECAR),y)

REGLINUX_GLIBC_SIDECAR_PREFIX = $(GLIBC_SIDECAR_PREFIX)
SIDECAR_P = $(REGLINUX_GLIBC_SIDECAR_PREFIX)

# Mesa without runtime LLVM. REG's Mesa turns it on for Imagination, but with
# -Dmesa-clc=system (REG's setting) Panfrost's and Imagination's OpenCL-C
# kernels come precompiled from the host mesa_clc and Mesa itself only wants
# LLVM for llvmpipe. The prebuilt LLVM REG downloads per CPU is musl-linked,
# so it can't be linked into a glibc userland anyway. Meson keeps the last -D.
MESA3D_CONF_OPTS += -Dllvm=disabled

# Mesa: DRI drivers are installed and searched in the same dir; GBM backends
# are installed in $(libdir)/gbm (pack.sh moves it under the prefix)
MESA3D_CONF_OPTS += \
	-Ddri-drivers-path=$(SIDECAR_P)/lib/dri \
	-Dgbm-backends-path=$(SIDECAR_P)/lib/gbm

# ALSA: plugins and configuration under the prefix
ALSA_LIB_CONF_OPTS += \
	--with-plugindir=$(SIDECAR_P)/lib/alsa-lib \
	--with-configdir=$(SIDECAR_P)/share/alsa
ALSA_PLUGINS_CONF_OPTS += \
	--with-plugindir=$(SIDECAR_P)/lib/alsa-lib \
	--with-alsadatadir=$(SIDECAR_P)/share/alsa \
	--with-alsagconfdir=$(SIDECAR_P)/share/alsa/alsa.conf.d \
	--with-alsalconfdir=$(SIDECAR_P)/etc/alsa/conf.d

# Vulkan ICDs/layers: only the sidecar's JSON files (pack.sh copies Mesa's)
VULKAN_LOADER_CONF_OPTS += \
	-DSYSCONFDIR=$(SIDECAR_P)/etc \
	-DFALLBACK_CONFIG_DIRS=$(SIDECAR_P)/etc/xdg \
	-DFALLBACK_DATA_DIRS=$(SIDECAR_P)/share

LIBGLIB2_CONF_OPTS += -Dgio_module_dir=$(SIDECAR_P)/lib/gio/modules

# OpenSSL: providers and engines are compiled in as $(libdir)/ossl-modules and
# $(libdir)/engines-3 (also where they install). Its configure line can't be
# appended to, so rewrite them in the generated Makefile
define REGLINUX_GLIBC_SIDECAR_OPENSSL_DIRS
	$(SED) 's|^ENGINESDIR=.*|ENGINESDIR=$(SIDECAR_P)/lib/engines-3|; s|^MODULESDIR=.*|MODULESDIR=$(SIDECAR_P)/lib/ossl-modules|' \
		$(LIBOPENSSL_DIR)/Makefile
endef
LIBOPENSSL_POST_CONFIGURE_HOOKS += REGLINUX_GLIBC_SIDECAR_OPENSSL_DIRS

# SDL2: REG drops the dummy video driver; ports and tools run headless with it
# (SDL_VIDEODRIVER=dummy), and some crash when SDL can't init any video
SDL2_CONF_OPTS += --enable-video-dummy

# libcurl: Ubuntu's exports versioned symbols (CURL_OPENSSL_4); without them
# every port linking it prints "no version information available"
LIBCURL_CONF_OPTS += --enable-versioned-symbols

# Only options and hooks can be appended from here: a package's dependencies are fixed
# when its own .mk is evaluated, which happens before this external tree. So
# SDL2 keeps REG's audio setup (PipeWire off when PipeWire isn't selected) and
# plays through ALSA, whose default device here is the pulse plugin.

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
REGLINUX_GLIBC_SIDECAR_DEPENDENCIES += alsa-lib
endif
ifeq ($(BR2_PACKAGE_ALSA_PLUGINS),y)
REGLINUX_GLIBC_SIDECAR_DEPENDENCIES += alsa-plugins
endif

# Default ALSA device of the sidecar (pack.sh makes alsa.conf read it: that
# edit has to happen on the final tree, where every package that depends on
# alsa-lib brings back alsa-lib's own alsa.conf)
define REGLINUX_GLIBC_SIDECAR_ALSA_CONF
	$(INSTALL) -D -m 0644 $(REGLINUX_GLIBC_SIDECAR_PKGDIR)/asound.conf \
		$(TARGET_DIR)$(SIDECAR_P)/etc/asound.conf
endef

ifeq ($(BR2_PACKAGE_WAYLAND),y)
define REGLINUX_GLIBC_SIDECAR_BUILD_CMDS
	$(TARGET_CC) $(TARGET_CFLAGS) -shared -fPIC -nostdlib \
		-Wl,-soname,libwayland-fixes-compat.so \
		-o $(@D)/libwayland-fixes-compat.so \
		$(REGLINUX_GLIBC_SIDECAR_PKGDIR)/wl_fixes_compat.c \
		-L$(STAGING_DIR)/usr/lib -lwayland-client
endef
define REGLINUX_GLIBC_SIDECAR_INSTALL_WL_FIXES
	$(INSTALL) -D -m 0755 $(@D)/libwayland-fixes-compat.so \
		$(TARGET_DIR)$(SIDECAR_P)/lib/libwayland-fixes-compat.so
endef
endif

# The image compares this with its own version to offer a sidecar refresh
define REGLINUX_GLIBC_SIDECAR_INSTALL_TARGET_CMDS
	$(REGLINUX_GLIBC_SIDECAR_INSTALL_WL_FIXES)
	mkdir -p $(TARGET_DIR)$(SIDECAR_P)
	echo "$(REGLINUX_SYSTEM_VERSION) glibc-$(GLIBC_VERSION)" > $(TARGET_DIR)$(SIDECAR_P)/VERSION
	$(if $(BR2_PACKAGE_ALSA_LIB),$(REGLINUX_GLIBC_SIDECAR_ALSA_CONF))
endef

endif

$(eval $(generic-package))
