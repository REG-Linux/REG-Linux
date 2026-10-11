################################################################################
#
# nfsiise — Need for Speed II SE reimplementation
#
################################################################################

NFSIISE_VERSION = v1.4.0
NFSIISE_SITE = https://github.com/zaps166/NFSIISE
NFSIISE_SITE_METHOD = git
NFSIISE_GIT_SUBMODULES = YES
NFSIISE_LICENSE = MIT

NFSIISE_DEPENDENCIES = sdl2

# NFS II SE uses a custom compile script, not CMake.
# On non-x86, it uses the C++ translation (compile_nfs cpp).
# Supports: gl2 (default), gl1, gles2.
ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
NFSIISE_GL_MODE = gles2
NFSIISE_DEPENDENCIES += libgles
else
NFSIISE_GL_MODE = gl1
NFSIISE_DEPENDENCIES += libgl
endif

# Always use C++ translation — avoids yasm host dependency
NFSIISE_BUILD_MODE = cpp

define NFSIISE_BUILD_CMDS
	cd $(@D) && \
		CC="$(TARGET_CC)" \
		CXX="$(TARGET_CXX)" \
		CFLAGS="$(TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)" \
		SDL2_CONFIG="$(PKG_CONFIG_HOST_BINARY) sdl2" \
		./compile_nfs $(NFSIISE_BUILD_MODE) $(NFSIISE_GL_MODE)
endef

define NFSIISE_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/build/nfs2se $(TARGET_DIR)/usr/bin/nfs2se
endef

$(eval $(generic-package))
