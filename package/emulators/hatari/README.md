# hatari

Atari ST/STe/TT/Falcon emulator.

**Upstream:** https://github.com/hatari/hatari
**Version:** 2.6.1 (v2.6.1)
**License:** GPLv3

## Build Configuration

### Build System

- **Type:** CMake package (`cmake-package`)
- **Build Type:** Release (optimized)
- **Linking:** Static libraries preferred (`-DBUILD_STATIC_LIBS=ON`)
- **LTO:** Enabled via patch (`CMAKE_INTERPROCEDURAL_OPTIMIZATION`)
- **Testing:** Disabled (patch removes `enable_testing()`)
- **Man Pages:** Disabled (reduces build dependencies and size)
- **Icons/Docs:** Not installed (embedded system, saves space)

### Dependencies

| Package      | Buildroot Symbol           | Purpose                               |
| ------------ | -------------------------- | ------------------------------------- |
| SDL2         | `BR2_PACKAGE_SDL2`         | Video, audio, and input handling      |
| zlib         | `BR2_PACKAGE_ZLIB`         | Compression support                   |
| libpng       | `BR2_PACKAGE_LIBPNG`       | PNG image loading (screenshots, GUI)  |
| libcapsimage | `BR2_PACKAGE_LIBCAPSIMAGE` | IPF disk image support (SPS/Kryoflux) |

### Special Build Options

```makefile
CAPSIMAGE_INCLUDE_DIR="$(STAGING_DIR)/usr/include"
```

Explicitly set to locate the CAPS/IPF library headers in the staging directory. Required because libcapsimage uses a non-standard include path structure.

## Patches

### 001-tospath.patch

**Purpose:** Change default TOS ROM path to REG Linux convention
**Changes:**

- Default TOS image path: `/userdata/bios/tos.img` (instead of data dir relative path)
- Allows users to place TOS ROM in the standard BIOS directory

### 002-configpath.patch

**Purpose:** Redirect configuration and save paths to userdata partition
**Changes:**

- `sUserHomeDir` → `/userdata/system/configs/hatari`
- `sHatariHomeDir` → `/userdata/system/configs/hatari`
- Ensures configurations persist across reboots (read-only root filesystem)

### 003-enforce-lto.patch

**Purpose:** Enable Link-Time Optimization for better performance
**Changes:**

- Sets `CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE`
- Reduces binary size and improves execution speed
- Important for CPU-intensive emulation on embedded hardware

### 004-no-testing-no-manpages.patch

**Purpose:** Reduce build size and dependencies
**Changes:**

- Removes `enable_testing()` (no test suite needed for embedded)
- Disables man page generation (`ENABLE_MAN_PAGES=0`)
- Eliminates gzip dependency for documentation

### board/reglinux/patches/riscv64/hatari/001-fix-riscv.patch

**Purpose:** Fix RISC-V architecture build compatibility
**Changes:**

- Renames `REG_A0` to `_REG_A0` in `src/includes/m68000.h`
- Updates references in `src/debug/debugcpu.c` and `src/gemdos.c`
- Resolves conflict with RISC-V system headers that define `REG_A0`

## Platform Availability

Hatari is **excluded** from the following platforms in `Config.in.emulators`:

- **BCM2835** (Raspberry Pi 1/Zero) - Insufficient CPU power
- **JZ4770** (MIPS-based handhelds) - Architecture not supported
- **RK3128** (Low-end TV boxes) - Limited performance

Available on all other platforms (RK3288, RK3326, RK3588, H700, x86-64, etc.)

## Runtime Configuration

### BIOS Files

Place Atari TOS ROM at:

```
/userdata/bios/tos.img
```

### Configuration Files

Stored in:

```
/userdata/system/configs/hatari/
```

### Integration

- **EmulationStation:** Listed in `es-systems.yml` (Atari ST section)
- **Config Generator:** Python generators in `reglinux-configgen` handle:
    - `hatariConfig.py` - Main configuration
    - `hatariControllers.py` - Controller mappings
    - `hatariKeys.py` - Keyboard to joystick mapping
    - `hatariGenerator.py` - System integration

### Installed Binaries

| Binary   | Purpose                                           | Required |
| -------- | ------------------------------------------------- | -------- |
| `hatari` | Main emulator executable (Atari ST/STe/TT/Falcon) | **Yes**  |

**Notes:**

- Only the main emulator is installed to save space
- Utility tools (`hmsa`, `gst2ascii`) are omitted (embedded system)
- Disk conversion can be done on a PC if needed

## Performance Considerations

- **Static linking** reduces runtime dependencies and improves load times
- **LTO enabled** for optimal performance on target hardware
- **No debug symbols** in release builds (production-optimized)
- **Stripped binary** via Buildroot stripping

## Known Limitations

1. **CAPS/IPF Support:** Requires proprietary libcapsimage library from Kryoflux
2. **TOS ROM:** Not included (user must provide own Atari TOS ROM)
3. **Performance:** Falcon emulation requires more powerful hardware (RK3588, x86-64)
4. **Utilities:** `hmsa` and `gst2ascii` not installed (space savings)

## Future Improvements

- [ ] Evaluate shader cache support for OpenGL video backend
- [ ] Add per-game configuration support in configgen
- [ ] Consider shader packs for CRT emulation (if supported by upstream)
