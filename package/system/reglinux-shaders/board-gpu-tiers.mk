# board-gpu-tiers.mk
# Include this from each board's defconfig fragment or from a top-level
# BR2_EXTERNAL Config.in to auto-set BR2_PACKAGE_REGLINUX_SHADERS_GPU_TIER.
#
# Usage in a board defconfig:
#   BR2_PACKAGE_REGLINUX_SHADERS=y
#   BR2_PACKAGE_REGLINUX_SHADERS_TIER_T2=y   # ← set the right tier for this board
#
# Reference table (GPU IP → Mesa driver → tier):
#
# SoC(s)                       GPU IP          Mesa driver   Tier  Notes
# ───────────────────────────────────────────────────────────────────────────
# Allwinner H3                 Mali-400 MP2    Panfrost      T0    GLES 2.0 only
# Allwinner H5                 Mali-450 MP4    Panfrost      T0    GLES 2.0 only
# Allwinner H6                 Mali-T720 MP3   Panfrost      T1    GLES 3.1, no Vulkan
# Allwinner H313               Mali-G31 MP2    Panfrost      T2    GLES 3.2, no Vulkan
# Allwinner H616               Mali-G31 MP2    Panfrost      T2    GLES 3.2, no Vulkan
# Allwinner H700               Mali-G31 MP2    Panfrost      T2    GLES 3.2, no Vulkan
# Allwinner A523 / T527        Mali-G57 MC2    Panfrost      T3    Valhall, GLES 3.2
# Allwinner A733               Mali-G57 MC4    Panfrost      T3    Valhall, GLES 3.2
# Rockchip RK3326              Mali-G31 MP2    Panfrost      T2    GLES 3.2, no Vulkan
# Rockchip RK3399              Mali-T860 MP4   Panfrost      T1    GLES 3.1, no Vulkan(*)
# Rockchip RK3566              Mali-G52 2EE    Panfrost      T3    GLES 3.2, no Vulkan
# Rockchip RK3568              Mali-G52 2EE    Panfrost      T3    GLES 3.2, no Vulkan
# Rockchip RK3576              Mali-G52 MC4    Panfrost      T3    GLES 3.2, no Vulkan
# Rockchip RK3588              Mali-G610 MC4   Panthor       T4    Vulkan 1.2 (Panthor)
# Amlogic S905                 Mali-450        Panfrost      T0    GLES 2.0 only
# Amlogic S905X / S905D        Mali-450        Panfrost      T0    GLES 2.0 only
# Amlogic S905X2               Mali-G31 MP2    Panfrost      T2    GLES 3.2, no Vulkan
# Amlogic S905X3 / S905X4-B   Mali-G31 MP2    Panfrost      T2    GLES 3.2, no Vulkan
# Amlogic S922X                Mali-G52 MP6    Panfrost      T3    GLES 3.2, no Vulkan
# Amlogic A311D                Mali-G52 MP8    Panfrost      T3    GLES 3.2, no Vulkan
# ODROID C5 (S905X5M)          Mali-G310 MP4   Panthor       T4    Mesa PanVK Vulkan
# BCM2835 / RPi 0-1            VideoCore IV    vc4           T0    GLES 2.0 only
# BCM2836-2837 / RPi 2-3       VideoCore IV    vc4           T0    GLES 2.0 only
# BCM2711 / RPi 4-400          VideoCore VI    v3d           T3    Mesa Vulkan (v3dv) ok
# SpacemiT K1 (RISC-V)         PowerVR BXE     Zink/IMG      T1    Zink GLES 3.0, no WSI Vk
# SpacemiT K3 (RISC-V)         PowerVR BXM-4-64 Zink/IMG     T1    Zink GLES 3.0, no WSI Vk
# x86_64 v3 / v4               Intel/AMD/Nvid  iris/radv/…   T4    Full GL + Vulkan
#
# (*) RK3399 / Mali-T860: Panfrost supports GL 3.3 / GLES 3.1 but no float_fb
#     in practice. Conservative T1 avoids issues; promote to T2 if validated.
