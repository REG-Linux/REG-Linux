################################################################################
#
# glibc-sidecar
#
# The toolchain glibc, rebuilt from the same patched source tree with
# --prefix=/usr/glibc (armhf: /usr/glibc32, so an aarch64 board can mount both
# sidecars, the 32-bit one for 32-bit ports). Everything in the sidecar is linked against the
# toolchain glibc in $(STAGING_DIR); this build is ABI-identical (same version,
# patches and options), only its compiled-in paths differ:
#   slibdir = libdir = rtlddir = <prefix>/lib   (the loader's only search dir)
#   sysconfdir = <prefix>/etc                     (ld.so.cache, ld.so.conf)
# reglinux-glibc-sidecar's pack step puts these files in place of the
# toolchain's copies.
#
# sidecar-patches/ only apply here, never to the toolchain glibc: the build
# runs from a copy of its source tree. (Not *.patch in this directory, which
# buildroot would apply to this package's empty source dir.)
#
################################################################################

GLIBC_SIDECAR_VERSION = $(GLIBC_VERSION)
GLIBC_SIDECAR_SOURCE =
GLIBC_SIDECAR_LICENSE = $(GLIBC_LICENSE)
# Builds out of the toolchain glibc's extracted and patched source tree
GLIBC_SIDECAR_DEPENDENCIES = glibc

GLIBC_SIDECAR_PREFIX = $(if $(BR2_arm),/usr/glibc32,/usr/glibc)

# Runtime only: the loader, libc and its split-out libraries, the NSS modules
# getaddrinfo() & co need. Not every arch has all of them (libmvec: aarch64
# and x86 only); the loader must be there.
GLIBC_SIDECAR_LIBS = \
	ld-linux*.so.* libc.so.* libm.so.* libmvec.so.* libpthread.so.* \
	libdl.so.* librt.so.* libresolv.so.* libutil.so.* libanl.so.* \
	libnss_files.so.* libnss_dns.so.*

# iconv: UTF-8, ASCII, UCS-2/4 and ISO-8859-1 are built into libc. Add the
# Unicode encodings and the Western, Japanese, Chinese and Korean charsets
# games commonly use.
GLIBC_SIDECAR_GCONV = \
	UTF-16.so UTF-32.so UTF-7.so UNICODE.so \
	ISO8859-*.so CP1250.so CP1251.so CP1252.so IBM437.so IBM850.so \
	SJIS.so CP932.so EUC-JP.so EUC-JP-MS.so libJIS.so \
	GBK.so GB18030.so EUC-CN.so BIG5.so BIG5HKSCS.so libGB.so libCNS.so \
	EUC-KR.so UHC.so JOHAB.so libKSC.so

define GLIBC_SIDECAR_CONFIGURE_CMDS
	rm -rf $(@D)/src $(@D)/build
	rsync -a --exclude=/build $(GLIBC_DIR)/ $(@D)/src/
	$(APPLY_PATCHES) $(@D)/src $(GLIBC_SIDECAR_PKGDIR)/sidecar-patches \*.patch
	mkdir -p $(@D)/build
	(cd $(@D)/build; \
		$(TARGET_CONFIGURE_OPTS) \
		CFLAGS="$(GLIBC_CFLAGS) $(GLIBC_EXTRA_CFLAGS)" CPPFLAGS="" \
		CXXFLAGS="$(GLIBC_CFLAGS) $(GLIBC_EXTRA_CFLAGS)" \
		$(GLIBC_CONF_ENV) \
		$(SHELL) $(@D)/src/configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=$(GLIBC_SIDECAR_PREFIX) \
		--enable-shared \
		--with-pkgversion="REG-Linux glibc sidecar" \
		--disable-profile \
		--disable-werror \
		--without-gd \
		--with-headers=$(STAGING_DIR)/usr/include \
		$(if $(BR2_aarch64)$(BR2_aarch64_be),--enable-mathvec) \
		$(GLIBC_CONF_OPTS))
endef

define GLIBC_SIDECAR_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(GLIBC_MAKE) -C $(@D)/build
endef

define GLIBC_SIDECAR_INSTALL_TARGET_CMDS
	rm -rf $(@D)/install
	$(TARGET_MAKE_ENV) $(GLIBC_MAKE) -C $(@D)/build install_root=$(@D)/install install
	mkdir -p $(TARGET_DIR)$(GLIBC_SIDECAR_PREFIX)/lib/gconv $(TARGET_DIR)$(GLIBC_SIDECAR_PREFIX)/etc
	cd $(@D)/install$(GLIBC_SIDECAR_PREFIX)/lib && \
		ls ld-linux*.so.* >/dev/null && \
		for f in $(GLIBC_SIDECAR_LIBS); do \
			if [ -e "$$f" ]; then cp -a $$f $(TARGET_DIR)$(GLIBC_SIDECAR_PREFIX)/lib/; fi; \
		done
	# gconv-modules lists every charset; a missing module only fails when it is asked for
	cd $(@D)/install$(GLIBC_SIDECAR_PREFIX)/lib/gconv && \
		for f in gconv-modules gconv-modules.d $(GLIBC_SIDECAR_GCONV); do \
			if [ -e "$$f" ]; then cp -a $$f $(TARGET_DIR)$(GLIBC_SIDECAR_PREFIX)/lib/gconv/; fi; \
		done
	touch $(TARGET_DIR)$(GLIBC_SIDECAR_PREFIX)/etc/ld.so.conf
endef

$(eval $(generic-package))
