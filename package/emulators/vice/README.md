# vice

**Commodore 8-bit emulator suite**

Upstream: https://vice-emu.sourceforge.io/

## Version

- **Version**: 3.10
- **License**: GPL-2.0

## Description

VICE is an emulator collection which emulates the following Commodore computers:

- **C64** / **C64-DTV** (Commodore 64)
- **C128** (Commodore 128)
- **VIC20** (VIC-20)
- **PET** (all models)
- **PLUS4** (Commodore 16/Plus4)
- **CBM-II** (aka C610)

## Build System

Uses **autotools** (`./configure && make && make install`).

Each emulator target is built separately with `-j1` to avoid build issues.

## Dependencies

### Runtime Dependencies

| Package      | Purpose                            |
| ------------ | ---------------------------------- |
| `sdl2`       | Video, audio, input (includes X11) |
| `sdl2_image` | Image loading                      |
| `alsa-lib`   | Audio output                       |
| `libcurl`    | Network updates                    |
| `giflib`     | GIF image support                  |
| `jpeg`       | JPEG image support                 |
| `libpng`     | PNG image support                  |
| `zlib`       | Compression                        |
| `lame`       | MP3 encoding                       |
| `libvorbis`  | Ogg Vorbis decoding                |
| `mpg123`     | MP3 decoding                       |
| `flac`       | FLAC decoding                      |

**Note**: SDL2 automatically pulls in X11 dependencies (libX11, libXext, libXv, libXrandr, libXinerama) when building with X11 support.

### Build Dependencies (host tools)

| Package         | Purpose                                   |
| --------------- | ----------------------------------------- |
| `host-xa`       | 6502 cross-assembler (required for build) |
| `host-dos2unix` | Line ending conversion                    |

## Configuration

### Emulator Targets

Each emulator binary can be individually enabled/disabled in `Config.in`:

| Target    | Emulator     | Default     | Notes                                     |
| --------- | ------------ | ----------- | ----------------------------------------- |
| `x64`     | C64          | ✅ Enabled  | Standard C64 emulator                     |
| `x64sc`   | C64          | ❌ Optional | Single-cycle accurate (requires fast CPU) |
| `x64dtv`  | C64-DTV      | ❌ Optional | C64-DTV emulator (requires fast CPU)      |
| `xscpu64` | C64 SuperCPU | ❌ Optional | SuperCPU emulator (requires fast CPU)     |
| `x128`    | C128         | ✅ Enabled  | Commodore 124 emulator                    |
| `xvic`    | VIC-20       | ✅ Enabled  | VIC-20 emulator                           |
| `xplus4`  | Plus/4       | ✅ Enabled  | Commodore Plus/4 emulator                 |
| `xpet`    | PET          | ✅ Enabled  | PET/CBM emulator                          |
| `xcbm2`   | CBM-II       | ✅ Enabled  | CBM-II (C610) emulator                    |

### Audio Features

All audio formats are enabled by default:

- **MP3**: LAME (encoding) + mpg123 (decoding)
- **FLAC**: FLAC decoding
- **Ogg Vorbis**: Vorbis decoding
- **MIDI**: ALSA sequencer support

### Graphics

- **Backend**: SDL2
- **UI**: SDL2-based (not GTK3)
- **X11**: Required for windowing on Linux

## Installation Paths

| Path               | Content                                |
| ------------------ | -------------------------------------- |
| `/usr/bin/x64`     | C64 emulator (if enabled)              |
| `/usr/bin/x64sc`   | C64 single-cycle emulator (if enabled) |
| `/usr/bin/x64dtv`  | C64-DTV emulator (if enabled)          |
| `/usr/bin/xscpu64` | C64 SuperCPU emulator (if enabled)     |
| `/usr/bin/x128`    | C128 emulator (if enabled)             |
| `/usr/bin/xvic`    | VIC-20 emulator (if enabled)           |
| `/usr/bin/xplus4`  | Plus/4 emulator (if enabled)           |
| `/usr/bin/xpet`    | PET emulator (if enabled)              |
| `/usr/bin/xcbm2`   | CBM-II emulator (if enabled)           |
| `/usr/share/vice/` | ROMs, palettes, documentation          |

**Note**: Unselected emulator binaries are removed during post-install to save space.

## Patches

### `000-fix-segfault.patch`

Fixes a segmentation fault in `menu_screenshot.c` when the menu pointer is NULL.

**Upstream status**: Should be submitted upstream.

## Known Issues

### Build Issues

1. **Serial build required**: Each target must be built with `-j1` due to race conditions.
2. **LDFLAGS workaround**: `-lSDL2` explicitly added to LDFLAGS to ensure proper linking.

### Runtime Issues

1. **X11 required**: Even with SDL2, X11 is needed for windowing on Linux.
2. **Fast CPU recommended**: `x64sc`, `x64dtv`, and `xscpu64` require fast CPUs for fullspeed emulation.
3. **ROMs required**: Kernal, BASIC, and character ROMs needed for accurate emulation.

## Performance Notes

### Weak CPU Optimization

For MIPS, ARM1176JZF-S, and Cortex-A7 CPUs, ReSID (accurate SID emulation) is disabled:

```makefile
--without-resid
```

This uses FastSID instead, which is less accurate but much faster on weak CPUs.

## References

- **Official Website**: https://vice-emu.sourceforge.io/
- **SourceForge**: https://sourceforge.net/projects/vice-emu/
- **Documentation**: https://vice-emu.sourceforge.io/vice_toc.html
- **GitHub Mirror**: https://github.com/vice-emu/vice

## See Also

- [libretro-vice](../libretro/libretro-vice) - Libretro core version
