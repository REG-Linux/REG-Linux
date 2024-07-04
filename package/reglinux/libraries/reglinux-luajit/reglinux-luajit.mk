################################################################################
#
# luajit
#
################################################################################

# REG-Linux: use specific fork for RISC-V 64
# REG-Linux: use OpenResty maintained LuaJIT2 fork for others
ifeq ($(BR2_RISCV_64),y)
REGLINUX_LUAJIT_VERSION = c0be24b5467e9c7ba3765423b680c368c76a4f07
REGLINUX_LUAJIT_SITE = $(call github,plctlab,LuaJIT,$(REGLINUX_LUAJIT_VERSION))
else
REGLINUX_LUAJIT_VERSION = dc397b66e6c8065185343cbe5dbeb4532f8e0b92
REGLINUX_LUAJIT_SITE = $(call github,openresty,luajit2,$(REGLINUX_LUAJIT_VERSION))
endif
REGLINUX_LUAJIT_LICENSE = MIT
REGLINUX_LUAJIT_LICENSE_FILES = COPYRIGHT
REGLINUX_LUAJIT_CPE_ID_VENDOR = luajit

REGLINUX_LUAJIT_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_REGLINUX_LUAJIT_COMPAT52),y)
REGLINUX_LUAJIT_XCFLAGS += -DLUAJIT_ENABLE_LUA52COMPAT
endif

# The luajit build procedure requires the host compiler to have the
# same bitness as the target compiler. Therefore, on a x86 build
# machine, we can't build luajit for x86_64, which is checked in
# Config.in. When the target is a 32 bits target, we pass -m32 to
# ensure that even on 64 bits build machines, a compiler of the same
# bitness is used. Of course, this assumes that the 32 bits multilib
# libraries are installed.
ifeq ($(BR2_ARCH_IS_64),y)
REGLINUX_LUAJIT_HOST_CC = $(HOSTCC)
# There is no LUAJIT_ENABLE_GC64 option.
else
REGLINUX_LUAJIT_HOST_CC = $(HOSTCC) -m32
REGLINUX_LUAJIT_XCFLAGS += -DLUAJIT_DISABLE_GC64
endif

# We unfortunately can't use TARGET_CONFIGURE_OPTS, because the luajit
# build system uses non conventional variable names.
define REGLINUX_LUAJIT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) PREFIX="/usr" \
		STATIC_CC="$(TARGET_CC)" \
		DYNAMIC_CC="$(TARGET_CC) -fPIC" \
		TARGET_LD="$(TARGET_CC)" \
		TARGET_AR="$(TARGET_AR) rcus" \
		TARGET_STRIP=true \
		TARGET_CFLAGS="$(TARGET_CFLAGS)" \
		TARGET_LDFLAGS="$(TARGET_LDFLAGS)" \
		HOST_CC="$(REGLINUX_LUAJIT_HOST_CC)" \
		HOST_CFLAGS="$(HOST_CFLAGS)" \
		HOST_LDFLAGS="$(HOST_LDFLAGS)" \
		BUILDMODE=dynamic \
		XCFLAGS="$(REGLINUX_LUAJIT_XCFLAGS)" \
		-C $(@D) amalg
endef

define REGLINUX_LUAJIT_INSTALL_STAGING_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) PREFIX="/usr" DESTDIR="$(STAGING_DIR)" LDCONFIG=true -C $(@D) install
endef

define REGLINUX_LUAJIT_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) PREFIX="/usr" DESTDIR="$(TARGET_DIR)" LDCONFIG=true -C $(@D) install
endef

# host-efl package needs host-luajit to be linked dynamically.
define HOST_REGLINUX_LUAJIT_BUILD_CMDS
	$(HOST_MAKE_ENV) $(MAKE) PREFIX="$(HOST_DIR)" BUILDMODE=dynamic \
		TARGET_LDFLAGS="$(HOST_LDFLAGS)" \
		XCFLAGS="$(REGLINUX_LUAJIT_XCFLAGS)" \
		-C $(@D) amalg
endef

define HOST_REGLINUX_LUAJIT_INSTALL_CMDS
	$(HOST_MAKE_ENV) $(MAKE) PREFIX="$(HOST_DIR)" LDCONFIG=true -C $(@D) install
endef

$(eval $(generic-package))
$(eval $(host-generic-package))
