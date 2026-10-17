# rockchip-old kernel patches (RK3288 / RK3328)

LibreELEC's maintained Rockchip patch stack for the older SoCs, taken from
LibreELEC.tv `packages/linux/patches/rockchip-old` at commit
`0b59256ef1a8e95bc7aa7c57fb3c62acb05bf0a4` (last change to the directory:
`6902d1901911`, 2026-08-23). LibreELEC applies it on Linux 7.2; here it is
used on 6.18:

- `rockchip-0019` is rebased (DRM_COLOR_FORMAT_YCBCR420 spelling on 6.18),
  `rockchip-0020`/`0022` use 6.18's struct drm_atomic_state (7.x renamed it).
- `rockchip-0055` (IEP) passes copy_frame_flags to v4l2_m2m_buf_copy_metadata(),
  which 6.18 still takes (7.x dropped it).
- LibreELEC's rkvdec series `0029`-`0035` targets the 7.x rkvdec rewrite, so
  it is replaced by `rockchip-0029-REG-1001-*`: the same fixes (plus the RK3328
  VP9 QoS fix), from the Jonas Karlman / Randy Li / Alex Bee series shipped by
  Batocera and LibreELEC for 6.12, rebased on 6.18 and squashed by REG-Linux
  (original sign-offs kept).
- `rockchip-0048-REG-2000-*` is the WIP HEVC backend + variants (Jonas Karlman,
  Alex Bee, Nicolas Dufresne) that 7.x has upstream, rebased and ported to the
  6.18 `get_image_fmt` rkvdec API by REG-Linux (original sign-offs kept).
