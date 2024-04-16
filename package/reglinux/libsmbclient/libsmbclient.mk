################################################################################
#
# libsmbclient
#
################################################################################

LIBSMBCLIENT_VERSION = 4.19.6
LIBSMBCLIENT_SITE = https://download.samba.org/pub/samba/stable
LIBSMBCLIENT_SOURCE = samba-$(LIBSMBCLIENT_VERSION).tar.gz
LIBSMBCLIENT_INSTALL_STAGING = YES
LIBSMBCLIENT_LICENSE = GPL-3.0+
LIBSMBCLIENT_LICENSE_FILES = COPYING
LIBSMBCLIENT_CPE_ID_VENDOR = samba
LIBSMBCLIENT_CPE_ID_PRODUCT = samba
LIBSMBCLIENT_SELINUX_MODULES = samba
LIBSMBCLIENT_DEPENDENCIES = \
	host-e2fsprogs host-flex host-heimdal host-nfs-utils \
	host-perl host-perl-parse-yapp host-python3 \
	cmocka e2fsprogs gnutls popt zlib openldap \
	$(if $(BR2_PACKAGE_ICU),icu) \
	$(if $(BR2_PACKAGE_LIBAIO),libaio) \
	$(if $(BR2_PACKAGE_LIBCAP),libcap) \
	$(if $(BR2_PACKAGE_LIBGLIB2),libglib2) \
	$(if $(BR2_PACKAGE_READLINE),readline) \
	$(TARGET_NLS_DEPENDENCIES)
LIBSMBCLIENT_CFLAGS = $(TARGET_CFLAGS)
LIBSMBCLIENT_LDFLAGS = $(TARGET_LDFLAGS) $(TARGET_NLS_LIBS)
LIBSMBCLIENT_CONF_ENV = \
	CFLAGS="$(LIBSMBCLIENT_CFLAGS)" \
	LDFLAGS="$(LIBSMBCLIENT_LDFLAGS)" \
	XSLTPROC=false \
	WAF_NO_PREFORK=1

LIBSMBCLIENT_PYTHON = PYTHON="$(HOST_DIR)/bin/python3"
ifeq ($(BR2_PACKAGE_PYTHON3),y)
LIBSMBCLIENT_PYTHON += PYTHON_CONFIG="$(STAGING_DIR)/usr/bin/python3-config"
LIBSMBCLIENT_DEPENDENCIES += python3
else
LIBSMBCLIENT_CONF_OPTS += --disable-python
endif

ifeq ($(BR2_PACKAGE_LIBICONV),y)
LIBSMBCLIENT_DEPENDENCIES += libiconv
LIBSMBCLIENT_LDFLAGS += -liconv
endif

ifeq ($(BR2_PACKAGE_LIBTIRPC),y)
LIBSMBCLIENT_CFLAGS += `$(PKG_CONFIG_HOST_BINARY) --cflags libtirpc`
LIBSMBCLIENT_LDFLAGS += `$(PKG_CONFIG_HOST_BINARY) --libs libtirpc`
LIBSMBCLIENT_DEPENDENCIES += libtirpc host-pkgconf
endif

ifeq ($(BR2_PACKAGE_ACL),y)
LIBSMBCLIENT_CONF_OPTS += --with-acl-support
LIBSMBCLIENT_DEPENDENCIES += acl
else
LIBSMBCLIENT_CONF_OPTS += --without-acl-support
endif

ifeq ($(BR2_PACKAGE_CUPS),y)
LIBSMBCLIENT_CONF_ENV += CUPS_CONFIG="$(STAGING_DIR)/usr/bin/cups-config"
LIBSMBCLIENT_CONF_OPTS += --enable-cups
LIBSMBCLIENT_DEPENDENCIES += cups
else
LIBSMBCLIENT_CONF_OPTS += --disable-cups
endif

ifeq ($(BR2_PACKAGE_DBUS),y)
LIBSMBCLIENT_DEPENDENCIES += dbus
LIBSMBCLIENT_SHARED_MODULES += vfs_snapper
else
LIBSMBCLIENT_SHARED_MODULES += !vfs_snapper
endif

ifeq ($(BR2_PACKAGE_DBUS)$(BR2_PACKAGE_AVAHI_DAEMON),yy)
LIBSMBCLIENT_CONF_OPTS += --enable-avahi
LIBSMBCLIENT_DEPENDENCIES += avahi
else
LIBSMBCLIENT_CONF_OPTS += --disable-avahi
endif

ifeq ($(BR2_PACKAGE_GAMIN),y)
LIBSMBCLIENT_CONF_OPTS += --with-fam
LIBSMBCLIENT_DEPENDENCIES += gamin
else
LIBSMBCLIENT_CONF_OPTS += --without-fam
endif

ifeq ($(BR2_PACKAGE_LIBARCHIVE),y)
LIBSMBCLIENT_CONF_OPTS += --with-libarchive
LIBSMBCLIENT_DEPENDENCIES += libarchive
else
LIBSMBCLIENT_CONF_OPTS += --without-libarchive
endif

ifeq ($(BR2_PACKAGE_NCURSES),y)
LIBSMBCLIENT_CONF_ENV += NCURSES_CONFIG="$(STAGING_DIR)/usr/bin/$(NCURSES_CONFIG_SCRIPTS)"
LIBSMBCLIENT_DEPENDENCIES += ncurses
else
LIBSMBCLIENT_CONF_OPTS += --without-regedit
endif

LIBSMBCLIENT_WAF_BUILD_TARGET = smbclient
LIBSMBCLIENT_WAF_INSTALL_TARGET = install_smbclient
LIBSMBCLIENT_CONF_OPTS += --disable-rpath-private-install

# The ctdb tests (cluster) need bash and take up some space
# They're normally intended for debugging so remove them
define LIBSMBCLIENT_REMOVE_CTDB_TESTS
	rm -rf $(TARGET_DIR)/usr/lib/ctdb-tests
	rm -rf $(TARGET_DIR)/usr/share/ctdb-tests
	rm -f $(TARGET_DIR)/usr/bin/ctdb_run_*tests
endef
LIBSMBCLIENT_POST_INSTALL_TARGET_HOOKS += LIBSMBCLIENT_REMOVE_CTDB_TESTS

define LIBSMBCLIENT_CONFIGURE_CMDS
	$(INSTALL) -m 0644 package/samba4/samba4-cache.txt $(@D)/cache.txt;
	echo 'Checking whether fcntl supports setting/geting hints: $(if $(BR2_TOOLCHAIN_HEADERS_AT_LEAST_4_13),OK,NO)' >>$(@D)/cache.txt;
	echo 'Checking uname machine type: $(BR2_ARCH)' >>$(@D)/cache.txt;
	(cd $(@D); \
		$(LIBSMBCLIENT_PYTHON) \
		python_LDFLAGS="" \
		python_LIBDIR="" \
		PERL="$(HOST_DIR)/bin/perl" \
		$(TARGET_CONFIGURE_OPTS) \
		$(LIBSMBCLIENT_CONF_ENV) \
		./buildtools/bin/waf configure \
			--prefix=/usr \
			--sysconfdir=/etc \
			--localstatedir=/var \
			--with-libiconv=$(STAGING_DIR)/usr \
			--enable-fhs \
			--cross-compile \
			--cross-answers=$(@D)/cache.txt \
			--hostcc=gcc \
			--disable-rpath \
			--disable-rpath-install \
			--disable-iprint \
			--without-pam \
			--without-dmapi \
			--without-gpgme \
			--without-ldb-lmdb \
			--disable-glusterfs \
			--with-cluster-support \
			--bundled-libraries='!asn1_compile,!compile_et' \
			--with-shared-modules=$(subst $(space),$(comma),$(strip $(LIBSMBCLIENT_SHARED_MODULES))) \
			$(LIBSMBCLIENT_CONF_OPTS) \
	)
endef

define LIBSMBCLIENT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(LIBSMBCLIENT_PYTHON) $(MAKE) -C $(@D) $(LIBSMBCLIENT_WAF_BUILD_TARGET)
endef

define LIBSMBCLIENT_INSTALL_STAGING_CMDS
	$(TARGET_MAKE_ENV) $(LIBSMBCLIENT_PYTHON) $(MAKE) -C $(@D) DESTDIR=$(STAGING_DIR) $(LIBSMBCLIENT_WAF_INSTALL_TARGET)
endef

define LIBSMBCLIENT_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(LIBSMBCLIENT_PYTHON) $(MAKE) -C $(@D) DESTDIR=$(TARGET_DIR) $(LIBSMBCLIENT_WAF_INSTALL_TARGET)
endef

LIBSMBCLIENT_CONF_OPTS += --without-ad-dc --without-json

define LIBSMBCLIENT_REMOVE_SMBTORTURE
	rm -f $(TARGET_DIR)/usr/bin/smbtorture
endef

LIBSMBCLIENT_POST_INSTALL_TARGET_HOOKS += LIBSMBCLIENT_REMOVE_SMBTORTURE

$(eval $(generic-package))
