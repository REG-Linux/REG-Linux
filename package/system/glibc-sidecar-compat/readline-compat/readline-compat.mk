################################################################################
#
# readline-compat
#
# readline 7.0 for the glibc sidecar: libreadline.so.7 and libhistory.so.7,
# next to readline 8's .so.8. Libraries only.
#
################################################################################

READLINE_COMPAT_VERSION = 7.0
READLINE_COMPAT_SITE = $(BR2_GNU_MIRROR)/readline
READLINE_COMPAT_SOURCE = readline-$(READLINE_COMPAT_VERSION).tar.gz
READLINE_COMPAT_DL_SUBDIR = readline
READLINE_COMPAT_LICENSE = GPL-3.0+
READLINE_COMPAT_LICENSE_FILES = COPYING
READLINE_COMPAT_DEPENDENCIES = ncurses
READLINE_COMPAT_CONF_ENV = bash_cv_func_sigsetjmp=yes bash_cv_wcwidth_broken=no
READLINE_COMPAT_CONF_OPTS = --disable-static --enable-shared --with-curses
# Link libtinfo/ncurses like readline 8 does, for programs that don't
READLINE_COMPAT_MAKE_OPTS = SHLIB_LIBS=-lncurses

define READLINE_COMPAT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(READLINE_COMPAT_MAKE_OPTS) shared
endef

# The shlib build makes only the .so.7.0 files: the soname links are install's
define READLINE_COMPAT_INSTALL_TARGET_CMDS
	for l in readline history; do \
		$(INSTALL) -m 0755 $(@D)/shlib/lib$$l.so.7.0 $(TARGET_DIR)/usr/lib/ && \
		ln -sf lib$$l.so.7.0 $(TARGET_DIR)/usr/lib/lib$$l.so.7 || exit 1; \
	done
endef

$(eval $(autotools-package))
