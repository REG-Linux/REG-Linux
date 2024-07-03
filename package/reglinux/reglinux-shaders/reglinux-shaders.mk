################################################################################
#
# REG-Linux shaders
#
################################################################################

REGLINUX_SHADERS_VERSION = 1.1
REGLINUX_SHADERS_SOURCE =
REGLINUX_SHADERS_DEPENDENCIES = glsl-shaders

REGLINUX_GPU_SYSTEM = none

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86)$(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
	REGLINUX_GPU_SYSTEM = x86
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_JH7110)$(BR2_PACKAGE_BATOCERA_TARGET_K1),y)
	REGLINUX_GPU_SYSTEM = riscv
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2836)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
	REGLINUX_GPU_SYSTEM = vc4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
	REGLINUX_GPU_SYSTEM = vc5
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H3)$(BR2_PACKAGE_BATOCERA_TARGET_RK3128)$(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
	REGLINUX_GPU_SYSTEM = mali-400
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812)$(BR2_PACKAGE_BATOCERA_TARGET_S905)$(BR2_PACKAGE_BATOCERA_TARGET_H5)$(BR2_PACKAGE_BATOCERA_TARGET_RK3328),y)
	REGLINUX_GPU_SYSTEM = mali-450
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
	REGLINUX_GPU_SYSTEM = mali-t628
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H6),y)
	REGLINUX_GPU_SYSTEM = mali-t720
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y)
	REGLINUX_GPU_SYSTEM = mali-t760
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
	REGLINUX_GPU_SYSTEM = mali-t860
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326)$(BR2_PACKAGE_BATOCERA_TARGET_S905GEN2)$(BR2_PACKAGE_BATOCERA_TARGET_S905GEN3)$(BR2_PACKAGE_BATOCERA_TARGET_H616)$(BR2_PACKAGE_BATOCERA_TARGET_S9GEN4),y)
	REGLINUX_GPU_SYSTEM = mali-g31
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X)$(BR2_PACKAGE_BATOCERA_TARGET_RK3568)$(BR2_PACKAGE_BATOCERA_TARGET_A3GEN2),y)
	REGLINUX_GPU_SYSTEM = mali-g52
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
	REGLINUX_GPU_SYSTEM = mali-g610
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODIN),y)
	REGLINUX_GPU_SYSTEM = adreno-630
# We would need a separate s912 target to take advantage of the more powerful T820 GPU instead of G31
#else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
#	REGLINUX_GPU_SYSTEM = mali-t820
endif

REGLINUX_SHADERS_DIRIN=$(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-shaders/configs

ifeq ($(REGLINUX_GPU_SYSTEM),x86)
	REGLINUX_SHADERS_SETS=sharp-bilinear-simple retro scanlines enhanced curvature zfast flatten-glow mega-bezel mega-bezel-lite mega-bezel-ultralite
else
	REGLINUX_SHADERS_SETS=sharp-bilinear-simple retro scanlines enhanced curvature zfast flatten-glow
endif

define REGLINUX_SHADERS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders/bezel/Mega_Bezel/Presets
	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-shaders/presets-batocera/* $(TARGET_DIR)/usr/share/batocera/shaders/bezel/Mega_Bezel/Presets

	# general
	mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders/configs; \
	if test -e $(REGLINUX_SHADERS_DIRIN)/rendering-defaults-$(REGLINUX_GPU_SYSTEM).yml; then \
		cp $(REGLINUX_SHADERS_DIRIN)/rendering-defaults-$(REGLINUX_GPU_SYSTEM).yml $(TARGET_DIR)/usr/share/batocera/shaders/configs/rendering-defaults.yml; \
	else \
		cp $(REGLINUX_SHADERS_DIRIN)/rendering-defaults.yml $(TARGET_DIR)/usr/share/batocera/shaders/configs/; \
	fi

	# sets
	for set in $(REGLINUX_SHADERS_SETS); do \
		mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders/configs/$$set; \
		if test -e $(REGLINUX_SHADERS_DIRIN)/$$set/rendering-defaults-$(REGLINUX_GPU_SYSTEM).yml; then \
			cp $(REGLINUX_SHADERS_DIRIN)/$$set/rendering-defaults-$(REGLINUX_GPU_SYSTEM).yml $(TARGET_DIR)/usr/share/batocera/shaders/configs/$$set/rendering-defaults.yml; \
		else \
			cp $(REGLINUX_SHADERS_DIRIN)/$$set/rendering-defaults.yml $(TARGET_DIR)/usr/share/batocera/shaders/configs/$$set/; \
		fi \
	done
endef

define REGLINUX_SHADERS_SLANG
    # Some shaders got the .slan(g) variants moved
    cd $(TARGET_DIR)/usr/share/batocera/shaders/ && cp -f pixel-art-scaling/sharp-bilinear-simple.slangp ./interpolation/ && \
		cp -f pixel-art-scaling/shaders/sharp-bilinear-simple.slang ./interpolation/shaders/
    cd $(TARGET_DIR)/usr/share/batocera/shaders/ && cp -f edge-smoothing/scalehq/2xScaleHQ.slangp ./scalehq/ && \
		cp -f ./edge-smoothing/scalehq/shaders/2xScaleHQ.slang ./scalehq/shaders/
endef

ifeq ($(BR2_PACKAGE_SLANG_SHADERS),y)
    REGLINUX_SHADERS_DEPENDENCIES += slang-shaders
    REGLINUX_SHADERS_POST_INSTALL_TARGET_HOOKS = REGLINUX_SHADERS_SLANG
endif

$(eval $(generic-package))
