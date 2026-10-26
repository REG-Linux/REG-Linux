################################################################################
#
# libopenssl-compat
#
# OpenSSL 1.1.1 for the glibc sidecar: libssl.so.1.1 and libcrypto.so.1.1,
# which ports built on Ubuntu 20.04 link. Libraries only. Certificates and
# openssl.cnf come from the board's /etc/ssl like OpenSSL 3's (data, not
# code); engines would load from the prefix, none are shipped.
#
################################################################################

LIBOPENSSL_COMPAT_VERSION = 1.1.1w
LIBOPENSSL_COMPAT_SITE = https://github.com/openssl/openssl/releases/download/OpenSSL_1_1_1w
LIBOPENSSL_COMPAT_SOURCE = openssl-$(LIBOPENSSL_COMPAT_VERSION).tar.gz
LIBOPENSSL_COMPAT_DL_SUBDIR = libopenssl
LIBOPENSSL_COMPAT_LICENSE = OpenSSL or SSLeay
LIBOPENSSL_COMPAT_LICENSE_FILES = LICENSE

define LIBOPENSSL_COMPAT_CONFIGURE_CMDS
	cd $(@D); \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_OPTS) \
		./Configure \
			$(LIBOPENSSL_TARGET_ARCH) \
			--prefix=$(GLIBC_SIDECAR_PREFIX) \
			--libdir=lib \
			--openssldir=/etc/ssl \
			threads \
			shared \
			no-tests \
			no-fuzz-libfuzzer \
			no-fuzz-afl \
			no-afalgeng \
			no-unit-test \
			no-crypto-mdebug
endef

define LIBOPENSSL_COMPAT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) build_libs
endef

define LIBOPENSSL_COMPAT_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 $(@D)/libcrypto.so.1.1 $(@D)/libssl.so.1.1 $(TARGET_DIR)/usr/lib/
endef

$(eval $(generic-package))
