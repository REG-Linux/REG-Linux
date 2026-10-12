# Yamagi Quake II family

Yamagi Quake II client and mission packs. Upstream: https://github.com/yquake2

Each mission pack (`yquake2-xatrix`, `yquake2-rogue`, `yquake2-ctf`, `yquake2-zaero`) installs its `game.so` via the `datainit` tree so first-boot populate lands it in `/userdata/roms/quake2/<packname>/`, next to the base client and the user's own `.pak` files, so the base client can load it. SDL3 is preferred when available, with SDL2 as fallback.

`yquake2-ref-vk` (https://github.com/yquake2/ref_vk) adds a Vulkan renderer (`ref_vk.so`), auto-selected alongside the base client on boards with `BR2_PACKAGE_REGLINUX_VULKAN` (same flag flycast/xemu/fteqw gate their own Vulkan support on). It's a separate upstream repo, not part of the main `yquake2/yquake2` CMake build, built via its own plain Makefile (no CMake, no glslangValidator needed at build time -- shaders ship pre-compiled to SPIR-V as C arrays) and installed the same way as the mission packs, next to `ref_gl1.so`/`ref_gl3.so`/`ref_gles3.so`. Select "Vulkan" from the in-game video menu, or `vid_renderer vk` + `vid_restart`.
