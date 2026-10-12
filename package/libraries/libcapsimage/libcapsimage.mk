################################################################################
#
# LIBCAPSIMAGE
#
################################################################################

LIBCAPSIMAGE_SOURCE = spsdeclib_$(LIBCAPSIMAGE_VERSION)_source.zip
LIBCAPSIMAGE_VERSION = 5.21
LIBCAPSIMAGE_SITE = http://www.kryoflux.com/download
LIBCAPSIMAGE_SITE_METHOD = wget
LIBCAPSIMAGE_SUBDIR = SPStudio_Dev

# Real lib is libCAPSImage.so.<major>.<minor>.0 (CMakeLists.txt always uses
# patch level 0), SONAME is libCAPSImage.so.<major>
LIBCAPSIMAGE_SOMAJOR = $(firstword $(subst ., ,$(LIBCAPSIMAGE_VERSION)))
LIBCAPSIMAGE_SOFULL = $(LIBCAPSIMAGE_VERSION).0

LIBCAPSIMAGE_INSTALL_STAGING = YES

define LIBCAPSIMAGE_EXTRACT_CMDS
	$(UNZIP) $(DL_DIR)/$(LIBCAPSIMAGE_DL_SUBDIR)/$(LIBCAPSIMAGE_SOURCE) -d $(@D)
endef

# ComLib.h unconditionally defines ExtSub/ExtVar as "extern \"C\" ...", which
# is invalid outside of C++. Consumers using the public headers from plain C
# (hatari, libretro-hatari...) fail to parse CapsLib.h as a result: guard it
# the standard way so C callers still get correct (non name-mangled) linkage.
define LIBCAPSIMAGE_FIX_C_LINKAGE
	$(SED) 's/#define ExtSub extern "C" DllSub/#ifdef __cplusplus\n#define ExtSub extern "C" DllSub\n#else\n#define ExtSub DllSub\n#endif/' \
		$(@D)/SPStudio_Dev/LibIPF/ComLib.h
	$(SED) 's/#define ExtVar extern "C" DllVar/#ifdef __cplusplus\n#define ExtVar extern "C" DllVar\n#else\n#define ExtVar DllVar\n#endif/' \
		$(@D)/SPStudio_Dev/LibIPF/ComLib.h
endef

LIBCAPSIMAGE_POST_EXTRACT_HOOKS += LIBCAPSIMAGE_FIX_C_LINKAGE

# The upstream CMakeLists.txt installs headers flatly under
# include/CAPSImage and tries to create an extra lowercase "libcapsimage.so"
# symlink outside of DESTDIR (broken with staging/target installs), so we
# bypass "cmake --install" entirely and install by hand, keeping the
# usr/include/caps + libcapsimage.so layout that hatari/amiberry expect.
define LIBCAPSIMAGE_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/include/caps
	cp -r $(@D)/SPStudio_Dev/LibIPF/*.h \
		$(STAGING_DIR)/usr/include/caps
	cp $(@D)/SPStudio_Dev/Core/CommonTypes.h \
		$(STAGING_DIR)/usr/include/caps
	mkdir -p $(STAGING_DIR)/usr/lib
	cp $(@D)/SPStudio_Dev/libCAPSImage.so.$(LIBCAPSIMAGE_SOFULL) \
		$(STAGING_DIR)/usr/lib
	ln -sf libCAPSImage.so.$(LIBCAPSIMAGE_SOFULL) $(STAGING_DIR)/usr/lib/libCAPSImage.so.$(LIBCAPSIMAGE_SOMAJOR)
	ln -sf libCAPSImage.so.$(LIBCAPSIMAGE_SOFULL) $(STAGING_DIR)/usr/lib/libcapsimage.so
endef

define LIBCAPSIMAGE_INSTALL_TARGET_CMDS
	# Target generic install
	mkdir -p $(TARGET_DIR)/usr/lib
	cp $(@D)/SPStudio_Dev/libCAPSImage.so.$(LIBCAPSIMAGE_SOFULL) \
		$(TARGET_DIR)/usr/lib
	ln -sf libCAPSImage.so.$(LIBCAPSIMAGE_SOFULL) $(TARGET_DIR)/usr/lib/libCAPSImage.so.$(LIBCAPSIMAGE_SOMAJOR)

	# FS-UAE specific install
	mkdir -p $(TARGET_DIR)/usr/share/fs-uae/Plugins
	ln -sf /usr/lib/libCAPSImage.so.$(LIBCAPSIMAGE_SOFULL) \
		$(TARGET_DIR)/usr/share/fs-uae/Plugins/capsimg.so
	echo "$(LIBCAPSIMAGE_VERSION)" > $(TARGET_DIR)/usr/share/fs-uae/Plugins/Version.txt

	# Amiberry specific install
	mkdir -p $(TARGET_DIR)/usr/share/amiberry/plugins
	ln -sf /usr/lib/libCAPSImage.so.$(LIBCAPSIMAGE_SOFULL) \
		$(TARGET_DIR)/usr/share/amiberry/plugins/capsimg.so
endef

$(eval $(cmake-package))
