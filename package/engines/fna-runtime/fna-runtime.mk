################################################################################
#
# fna-runtime — FNA game runtime (MonoKickstart + FNA3D + FAudio + Theorafile)
#
################################################################################

# FNA3D — 3D graphics library for FNA (SDL3 backend)
FNA_RUNTIME_FNA3D_VERSION = 26.07
FNA_RUNTIME_FNA3D_SITE = $(call github,FNA-XNA,FNA3D,$(FNA_RUNTIME_FNA3D_VERSION))
FNA_RUNTIME_FNA3D_SOURCE = FNA3D-$(FNA_RUNTIME_FNA3D_VERSION).tar.gz

# Theorafile — Theora video library (no SDL dependency)
FNA_RUNTIME_THEORAFILE_VERSION = 77e486c9348f3f899c3e0d565022f828daff37a1
FNA_RUNTIME_THEORAFILE_SITE = $(call github,FNA-XNA,Theorafile,$(FNA_RUNTIME_THEORAFILE_VERSION))
FNA_RUNTIME_THEORAFILE_SOURCE = Theorafile-$(FNA_RUNTIME_THEORAFILE_VERSION).tar.gz

# MojoShader — shader transpiler (FNA3D git submodule, not included in tarball)
FNA_RUNTIME_MOJOSHADER_VERSION = abdc80360c1d4560ab8f356035dcd53ae6e9b87f
FNA_RUNTIME_MOJOSHADER_SITE = $(call github,icculus,mojoshader,$(FNA_RUNTIME_MOJOSHADER_VERSION))
FNA_RUNTIME_MOJOSHADER_SOURCE = mojoshader-$(FNA_RUNTIME_MOJOSHADER_VERSION).tar.gz

FNA_RUNTIME_EXTRA_DOWNLOADS = \
	$(FNA_RUNTIME_THEORAFILE_SITE)/$(FNA_RUNTIME_THEORAFILE_SOURCE) \
	$(FNA_RUNTIME_MOJOSHADER_SITE)/$(FNA_RUNTIME_MOJOSHADER_SOURCE)

# Main source is FNA3D (for cmake-package), others are EXTRA_DOWNLOADS
FNA_RUNTIME_VERSION = $(FNA_RUNTIME_FNA3D_VERSION)
FNA_RUNTIME_SITE = $(FNA_RUNTIME_FNA3D_SITE)
FNA_RUNTIME_SOURCE = $(FNA_RUNTIME_FNA3D_SOURCE)

FNA_RUNTIME_LICENSE = zlib (FNA3D, FAudio, Theorafile), MIT (MonoKickstart/Mono BCL)
FNA_RUNTIME_DEPENDENCIES = sdl3 faudio

# FNA3D CMake options — build for SDL3, no tracing
FNA_RUNTIME_CONF_OPTS = \
	-DBUILD_SDL3=ON \
	-DBUILD_SHARED_LIBS=ON \
	-DTRACING_SUPPORT=OFF

FNA_RUNTIME_INSTALL_STAGING = NO

# MonoKickstart install dir
FNA_RUNTIME_MONODIR = $(TARGET_DIR)/usr/share/fna-runtime

# After extracting FNA3D source, also extract Theorafile and MojoShader
define FNA_RUNTIME_EXTRACT_EXTRA
	mkdir -p $(@D)/theorafile
	$(call suitable-extractor,$(FNA_RUNTIME_THEORAFILE_SOURCE)) \
		$(FNA_RUNTIME_DL_DIR)/$(FNA_RUNTIME_THEORAFILE_SOURCE) | \
		$(TAR) --strip-components=1 -C $(@D)/theorafile $(TAR_OPTIONS) -
	$(call suitable-extractor,$(FNA_RUNTIME_MOJOSHADER_SOURCE)) \
		$(FNA_RUNTIME_DL_DIR)/$(FNA_RUNTIME_MOJOSHADER_SOURCE) | \
		$(TAR) --strip-components=1 -C $(@D)/MojoShader $(TAR_OPTIONS) -
endef
FNA_RUNTIME_POST_EXTRACT_HOOKS += FNA_RUNTIME_EXTRACT_EXTRA

# After FNA3D builds via cmake-package, build Theorafile
define FNA_RUNTIME_BUILD_EXTRA
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/theorafile \
		CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS) -fPIC" \
		LDFLAGS="$(TARGET_LDFLAGS)" \
		lib
endef
FNA_RUNTIME_POST_BUILD_HOOKS += FNA_RUNTIME_BUILD_EXTRA

# Install everything
define FNA_RUNTIME_INSTALL_TARGET_CMDS
	# Install FNA3D native lib (built by cmake-package)
	cp -avf $(@D)/libFNA3D.so* $(TARGET_DIR)/usr/lib/

	# Install Theorafile native lib
	$(INSTALL) -D -m 0755 $(@D)/theorafile/libtheorafile.so \
		$(TARGET_DIR)/usr/lib/libtheorafile.so

	# Install MonoKickstart runtime
	mkdir -p $(FNA_RUNTIME_MONODIR)
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/fna-runtime/monokickstart/*.dll \
		$(FNA_RUNTIME_MONODIR)/
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/fna-runtime/monokickstart/monoconfig \
		$(FNA_RUNTIME_MONODIR)/
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/fna-runtime/monokickstart/monomachineconfig \
		$(FNA_RUNTIME_MONODIR)/

	# Install arch-specific MonoKickstart binary
	if [ "$(BR2_x86_64)" = "y" ]; then \
		$(INSTALL) -D -m 0755 \
			$(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/fna-runtime/monokickstart/kick.bin.x86_64 \
			$(FNA_RUNTIME_MONODIR)/kick.bin ; \
		$(INSTALL) -D -m 0755 \
			$(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/fna-runtime/monokickstart/libMonoPosixHelper.x86_64.so \
			$(FNA_RUNTIME_MONODIR)/libMonoPosixHelper.so ; \
	elif [ "$(BR2_aarch64)" = "y" ]; then \
		$(INSTALL) -D -m 0755 \
			$(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/fna-runtime/monokickstart/kick.bin.aarch64 \
			$(FNA_RUNTIME_MONODIR)/kick.bin ; \
		$(INSTALL) -D -m 0755 \
			$(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/fna-runtime/monokickstart/libMonoPosixHelper.aarch64.so \
			$(FNA_RUNTIME_MONODIR)/libMonoPosixHelper.so ; \
	elif [ "$(BR2_RISCV_64)" = "y" ]; then \
		$(INSTALL) -D -m 0755 \
			$(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/fna-runtime/monokickstart/kick.bin.x86_64 \
			$(FNA_RUNTIME_MONODIR)/kick.bin ; \
		$(INSTALL) -D -m 0755 \
			$(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/fna-runtime/monokickstart/libMonoPosixHelper.x86_64.so \
			$(FNA_RUNTIME_MONODIR)/libMonoPosixHelper.so ; \
	fi

	# Create launcher symlink
	ln -sf /usr/share/fna-runtime/kick.bin $(TARGET_DIR)/usr/bin/fna-kick
endef

$(eval $(cmake-package))
