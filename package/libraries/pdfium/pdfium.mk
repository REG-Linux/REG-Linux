################################################################################
# PDFium prebuilt binary distribution (bblanchon/pdfium-binaries)
################################################################################

PDFIUM_VERSION = 7569
PDFIUM_SITE = https://github.com/rtissera/pdfium-binaries/releases/download/chromium%2F$(PDFIUM_VERSION)
PDFIUM_LICENSE = MIT
PDFIUM_LICENSE_FILES = LICENSE

PDFIUM_LIBC_SUFFIX =
PDFIUM_ARCH =

ifeq ($(BR2_arm),y)
PDFIUM_ARCH = arm
else ifeq ($(BR2_aarch64),y)
PDFIUM_ARCH = arm64
else ifeq ($(BR2_x86_64),y)
PDFIUM_ARCH = x64
else ifeq ($(BR2_riscv)$(BR2_ARCH_IS_64),yy)
PDFIUM_ARCH = riscv64
else
$(error BR2_PACKAGE_PDFIUM only supports arm, aarch64, riscv64 or x86_64 targets)
endif

ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
PDFIUM_LIBC_SUFFIX = -musl
else ifeq ($(BR2_TOOLCHAIN_USES_GLIBC),y)
PDFIUM_LIBC_SUFFIX =
else
$(error BR2_PACKAGE_PDFIUM requires a glibc or musl toolchain)
endif

PDFIUM_SOURCE = pdfium-linux$(PDFIUM_LIBC_SUFFIX)-$(PDFIUM_ARCH).tgz
PDFIUM_SITE_METHOD = https

define PDFIUM_INSTALL_TO_ROOT
	$(INSTALL) -d $(1)/usr/lib
	cp $(PDFIUM_DIR)/libpdfium.so $(1)/usr/lib/
	chmod a+x $(1)/usr/lib/libpdfium.so
endef

PDFIUM_INSTALL_STAGING_CMDS = $(call PDFIUM_INSTALL_TO_ROOT,$(STAGING_DIR))
PDFIUM_INSTALL_TARGET_CMDS = $(call PDFIUM_INSTALL_TO_ROOT,$(TARGET_DIR))

$(eval $(generic-package))
