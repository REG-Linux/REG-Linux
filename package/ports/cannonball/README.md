# cannonball

OutRun engine reimplementation (Cannonball SE). Upstream: https://github.com/J1mbo/cannonball-se

## Build Configuration

- **Target**: `sdl2gl` on x86_64, `sdl2gles` on all other architectures
- **ROM path**: `/userdata/roms/cannonball/`
- **Config path**: `/userdata/system/configs/cannonball/`

## Dependencies

- **Required**: sdl2, tinyxml2, libegl, libgles
- **Optional**: mpg123 (for MP3 audio support)
- **Toolchain**: C++23 compatible (GCC 12+, Clang 15+)

## Optimization

- LTO enabled for better performance in high-resolution modes
- `-Ofast` optimization flags in Release builds
- RISC-V RVV SIMD support enabled on riscv64 architectures

## Notes

- Requires OutRun revision B ROMs (not included)
- The patch `0001-fix-rvv-vmand-missing-vl-parameter-gcc15.patch` fixes GCC 15 ICE with RVV intrinsics
- The patch `0000-fix-compile-without-mpg123.patch` fixes compilation when mpg123 is disabled
