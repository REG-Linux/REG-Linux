################################################################################
# gcompat – glibc compatibility layer for musl
################################################################################

# Upstream Adélie Linux repo
GCOMPAT_VERSION = 1.1.0
GCOMPAT_SITE = https://git.adelielinux.org/adelie/gcompat/-/archive/$(GCOMPAT_VERSION)
GCOMPAT_SOURCE = gcompat-$(GCOMPAT_VERSION).tar.gz
GCOMPAT_LICENSE = NCSA
GCOMPAT_LICENSE_FILES = LICENSE

GCOMPAT_DEPENDENCIES =

# Makefile based build
define GCOMPAT_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
        CC="$(TARGET_CC)" \
        AR="$(TARGET_AR)" \
        RANLIB="$(TARGET_RANLIB)" \
        STRIP="$(TARGET_STRIP)" \
        CFLAGS="$(TARGET_CFLAGS) -D_GNU_SOURCE" \
        LDFLAGS="$(TARGET_LDFLAGS)" \
        prefix=/usr libdir=/lib
endef

define GCOMPAT_INSTALL_TARGET_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
        DESTDIR="$(TARGET_DIR)" \
        prefix=/usr libdir=/lib \
        install
endef

$(eval $(generic-package))

# Symlinks to provide glibc compatibility layer without gcompat loader
# Only for aarch64 and arm variants so far (no musl on x86_64 or RISC-V so far)
define GCOMPAT_POST_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/lib

    # AArch64
    if [ "$(BR2_aarch64)" = "y" ]; then \
        ln -sf /lib/ld-musl-aarch64.so.1 $(TARGET_DIR)/lib/ld-linux-aarch64.so.1 ; \
    fi

    # ARM 32-bit variants
    if [ "$(BR2_arm)" = "y" ]; then \
        if [ -e "$(TARGET_DIR)/lib/ld-musl-armhf.so.1" ]; then \
            ln -sf /lib/ld-musl-armhf.so.1 $(TARGET_DIR)/lib/ld-linux-armhf.so.3 || true ; \
            ln -sf /lib/ld-musl-armhf.so.1 $(TARGET_DIR)/lib/ld-linux.so.3 || true ; \
        elif [ -e "$(TARGET_DIR)/lib/ld-musl-arm.so.1" ]; then \
            ln -sf /lib/ld-musl-arm.so.1 $(TARGET_DIR)/lib/ld-linux.so.3 || true ; \
        fi ; \
    fi
endef

GCOMPAT_POST_INSTALL_TARGET_HOOKS += GCOMPAT_POST_INSTALL_TARGET_CMDS
