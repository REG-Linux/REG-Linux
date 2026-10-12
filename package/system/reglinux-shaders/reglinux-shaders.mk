################################################################################
#
# reglinux-shaders
#
# Installs a curated, tier-aware shortlist of RetroArch shader presets into
# /usr/share/reglinux/shaders. The per-tier shortlist lives in
# shaders-per-tier.json; see CLAUDE.md for the design rationale.
#
# T0-T3 boards use the `gl` RetroArch backend and install `.glslp` presets.
# T4 boards (Vulkan / desktop GL3.1+) install BOTH `.slangp` (preferred,
# for glcore/vulkan backends) AND `.glslp` (so the same image still
# serves cores running on the gl backend).
#
################################################################################

# --- glsl-shaders (primary source, always downloaded) ---
REGLINUX_SHADERS_VERSION = ebe123c55fa8538ec6abfa3eaa22d87f91e36679
REGLINUX_SHADERS_SITE    = https://github.com/libretro/glsl-shaders/archive
REGLINUX_SHADERS_SOURCE  = $(REGLINUX_SHADERS_VERSION).tar.gz
REGLINUX_SHADERS_LICENSE = GPL-2.0+
REGLINUX_SHADERS_LICENSE_FILES = LICENSE

# --- slang-shaders (extra download, only materialised at T4) ---
REGLINUX_SHADERS_SLANG_VERSION = 11c7f492a07e4fd8940a7d6b367f85ef7effabea
REGLINUX_SHADERS_SLANG_TARBALL = slang-shaders-$(REGLINUX_SHADERS_SLANG_VERSION).tar.gz
REGLINUX_SHADERS_SLANG_URL     = https://github.com/libretro/slang-shaders/archive/$(REGLINUX_SHADERS_SLANG_VERSION)/$(REGLINUX_SHADERS_SLANG_TARBALL)

ifeq ($(BR2_PACKAGE_REGLINUX_SHADERS_GPU_TIER),"T4")
REGLINUX_SHADERS_EXTRA_DOWNLOADS = $(REGLINUX_SHADERS_SLANG_URL)
endif

REGLINUX_SHADERS_INSTALL_STAGING = NO
REGLINUX_SHADERS_INSTALL_TARGET  = YES

REGLINUX_SHADERS_DEPENDENCIES = host-python3

REGLINUX_SHADERS_GPU_TIER = $(call qstrip,$(BR2_PACKAGE_REGLINUX_SHADERS_GPU_TIER))
REGLINUX_SHADERS_DESTDIR  = $(TARGET_DIR)/usr/share/reglinux/shaders

# T4 needs the slang-shaders tarball extracted alongside the glsl-shaders tree.
define REGLINUX_SHADERS_EXTRACT_SLANG
	$(if $(filter T4,$(REGLINUX_SHADERS_GPU_TIER)),\
		mkdir -p $(@D)/slang-shaders && \
		$(TAR) -C $(@D)/slang-shaders --strip-components=1 \
			-xf $($(PKG)_DL_DIR)/$(REGLINUX_SHADERS_SLANG_TARBALL))
endef
REGLINUX_SHADERS_POST_EXTRACT_HOOKS += REGLINUX_SHADERS_EXTRACT_SLANG

define REGLINUX_SHADERS_INSTALL_TARGET_CMDS
	mkdir -p $(REGLINUX_SHADERS_DESTDIR)
	$(HOST_DIR)/bin/python3 $(REGLINUX_SHADERS_PKGDIR)/curate-install.py \
		--manifest   $(REGLINUX_SHADERS_PKGDIR)/shaders-per-tier.json \
		--tier       $(REGLINUX_SHADERS_GPU_TIER) \
		--glsl-root  $(@D) \
		--slang-root $(@D)/slang-shaders \
		--destdir    $(REGLINUX_SHADERS_DESTDIR)
endef

$(eval $(generic-package))
