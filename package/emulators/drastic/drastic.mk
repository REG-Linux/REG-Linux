################################################################################
#
# drastic
#
################################################################################

DRASTIC_VERSION = 1.1
DRASTIC_SOURCE = drastic.tar.gz
DRASTIC_SITE = https://github.com/liberodark/drastic/releases/download/$(DRASTIC_VERSION)
DRASTIC_DEPENDENCIES = sdl2

define DRASTIC_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(DRASTIC_DL_SUBDIR)/$(DRASTIC_SOURCE)
endef

ifeq ($(BR2_arm),y)
    DRASTIC_BINARYFILE=drastic_xu4
else ifeq ($(BR2_aarch64),y)
    ifeq ($(BR2_PACKAGE_MESA3D),y)
        DRASTIC_BINARYFILE=drastic_n2
    else
        DRASTIC_BINARYFILE=drastic_oga
    endif
endif

# SDL hook (from Batocera): spans stacked dual screens, maps touch, shaders
define DRASTIC_BUILD_CMDS
	$(TARGET_CC) $(TARGET_CFLAGS) $(TARGET_LDFLAGS) -shared -fPIC \
		-o $(@D)/libdrastouch.so $(DRASTIC_PKGDIR)/libdrastouch.c -ldl
endef

define DRASTIC_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/
	mkdir -p $(TARGET_DIR)/usr/share/

	install -m 0755 $(@D)/target/$(DRASTIC_BINARYFILE) $(TARGET_DIR)/usr/bin/drastic
	cp -pr $(@D)/target/drastic $(TARGET_DIR)/usr/share/drastic
	install -D -m 0755 $(@D)/libdrastouch.so $(TARGET_DIR)/usr/lib/libdrastouch.so
endef

$(eval $(generic-package))
