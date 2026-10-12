# RetroArch for REG Linux

**RetroArch** is a free, ad-free, spyware-free, and open source cross platform frontend/framework for emulators, games, video players, and media players.

Upstream: https://www.libretro.com/

---

## Package Structure

```
retroarch/
├── Config.in                          # Buildroot configuration
├── retroarch.mk                       # Package build recipe
├── retroarch.hash                     # Hash verification
├── README.md                          # This file
│
├── Patches (custom REG Linux patches):
│   ├── 002-fix_configure.patch        # [REMOVED - no longer needed]
│   ├── 003-coreinfos.patch            # Custom core info display
│   ├── 004-cheevos-sounds.patch       # Achievement sound fixes
│   ├── 005-extend-udev-buttons.patch  # Extended controller button support
│   ├── 010-pad-lots-buttons.patch     # Additional gamepad buttons
│   ├── 011-cheevos-screenshot-filename.patch  # Achievement screenshot naming
│   ├── 012-achievementcall.patch      # Achievement call fixes
│   ├── 015-mousebuttons.patch         # Mouse button support
│   ├── 016-mouse-can-have-key.patch   # Mouse keyboard interaction
│   ├── 018-disable-draw-splash-screen.patch   # Disable startup splash
│   ├── 023-change-dot-config-path-to-configs.patch  # REG Linux config path
│   ├── 999-hotfix-crash-wayland-gl-context.patch  # Wayland OpenGL crash fix
│   └── xxx-opengl-hybrid.patch.disabled # [DISABLED] OpenGL hybrid rendering
│
└── Sub-packages:
    ├── libretro-core-info/            # Core information files
    ├── retroarch-assets/              # UI assets (XMB, RGUI, Ozone)
    ├── retroarch-joypad-autoconfig/   # Controller autoconfig profiles
    └── shaders/                       # Shader collections
        ├── common-shaders/
        ├── glsl-shaders/
        └── slang-shaders/
```

---

## Main Package: retroarch

### Version
- **Current**: 1.22.2
- **Source**: Source-only tarball from GitHub releases

### Dependencies

#### Mandatory (always selected)
| Package | Purpose |
|---------|---------|
| `dejavu` | Fonts for UI |
| `retroarch-assets` | UI assets (icons, themes) |
| `retroarch-assets-ozone` | Ozone menu assets (GLES3 only) |
| `libretro-core-info` | Core metadata files |
| `gamemode` | Performance optimization daemon |
| `hidapi` | HID device support |
| `libusb` | USB device support |
| `alsa-lib` | Audio output (Linux) |

#### Conditional
| Package | Purpose | Config Option |
|---------|---------|---------------|
| `ffmpeg` | Video recording/encoding | `BR2_PACKAGE_FFMPEG` |
| `flac` | FLAC audio support | `BR2_PACKAGE_FLAC` |
| `sdl2` | SDL2 input/audio driver | `BR2_PACKAGE_SDL2` |
| `pulseaudio` | PulseAudio output | `BR2_PACKAGE_PULSEAUDIO` |
| `pipewire` | PipeWire output | `BR2_PACKAGE_PIPEWIRE` |
| `libglvnd` | Desktop OpenGL | `BR2_PACKAGE_HAS_LIBGL` |
| `libgles` | OpenGL ES | `BR2_PACKAGE_HAS_GLES3` or `BR2_PACKAGE_HAS_GLES2` |
| `libegl` | EGL support | `BR2_PACKAGE_HAS_LIBEGL` |
| `vulkan-headers` | Vulkan support | `BR2_PACKAGE_REGLINUX_VULKAN` |
| `vulkan-loader` | Vulkan runtime | `BR2_PACKAGE_REGLINUX_VULKAN` |
| `slang-shaders` | Slang shader support | `BR2_PACKAGE_REGLINUX_VULKAN` |
| `wayland` | Wayland display server | `BR2_PACKAGE_WAYLAND` |
| `wayland-protocols` | Wayland protocols | `BR2_PACKAGE_WAYLAND` |
| `libxkbcommon` | XKB keymap | `BR2_PACKAGE_WAYLAND` |
| `freetype` | Font rendering | `BR2_PACKAGE_FREETYPE` |
| `zlib` | Compression | `BR2_PACKAGE_ZLIB` |
| `udev` | Device management | `BR2_PACKAGE_UDEV` |

#### Auto-detected (not in DEPENDENCIES)
| Package | Purpose |
|---------|---------|
| `libpng` | PNG image support (auto-detected) |
| `libjpeg` | JPEG image support (auto-detected) |

### Build Configuration

#### Graphics Backend Selection

| Target | Backend | Menu Driver | Notes |
|--------|---------|-------------|-------|
| **x86_64 (Desktop)** | OpenGL | Ozone | Full GL support |
| **GLES3 devices** | OpenGL ES 3.x | Ozone | Recommended for modern ARM |
| **GLES2 devices** | OpenGL ES 2.x | XMB | Fallback for older ARM |
| **Qualcomm/Asahi** | OpenGL ES 3.2 | Ozone | Full GLES3.2 support |

#### Audio Backend Priority

1. **ALSA** (mandatory) - Direct hardware access
2. **PulseAudio** (optional) - If enabled
3. **PipeWire** (optional) - If enabled

#### Input Drivers

- **udev** (Linux) - Recommended
- **libusb** - USB controller support
- **hidapi** - HID device support
- **SDL2** - SDL controller support

### Configure Options

```makefile
# Always enabled:
--enable-threads
--enable-networking
--enable-translate
--enable-hid
--enable-libusb
--enable-xdelta
--enable-lua
--enable-rgui
--enable-alsa

# Always disabled:
--disable-oss
--disable-qt
--disable-discord
--disable-cdrom
--disable-videocore
--disable-x11

# Conditional:
--enable-ffmpeg (if BR2_PACKAGE_FFMPEG)
--enable-flac (if BR2_PACKAGE_FLAC)
--enable-sdl2 (if BR2_PACKAGE_SDL2)
--enable-pulse (if BR2_PACKAGE_PULSEAUDIO)
--enable-pipewire (if BR2_PACKAGE_PIPEWIRE)
--enable-opengl (if BR2_PACKAGE_HAS_LIBGL)
--enable-opengles3 (if BR2_PACKAGE_HAS_GLES3)
--enable-opengles (if BR2_PACKAGE_HAS_GLES2)
--enable-egl (if BR2_PACKAGE_HAS_LIBEGL)
--enable-vulkan (if BR2_PACKAGE_REGLINUX_VULKAN)
--enable-wayland (if BR2_PACKAGE_WAYLAND)
```

---

## Patches

### Active Patches

| Patch | Purpose | Status |
|-------|---------|--------|
| `003-coreinfos.patch` | Add custom core info display (`-x` flag) | ✅ Active |
| `004-cheevos-sounds.patch` | Fix achievement sound playback | ✅ Active |
| `005-extend-udev-buttons.patch` | Extended udev button mappings | ✅ Active |
| `010-pad-lots-buttons.patch` | Support for additional gamepad buttons | ✅ Active |
| `011-cheevos-screenshot-filename.patch` | Fix achievement screenshot naming | ✅ Active |
| `012-achievementcall.patch` | Fix achievement notification sounds | ✅ Active |
| `015-mousebuttons.patch` | Mouse button support improvements | ✅ Active |
| `016-mouse-can-have-key.patch` | Mouse-keyboard interaction fixes | ✅ Active |
| `018-disable-draw-splash-screen.patch` | Disable startup splash screen | ✅ Active |
| `023-change-dot-config-path-to-configs.patch` | Change config path to `/configs/retroarch` (REG Linux convention) | ✅ Active |
| `999-hotfix-crash-wayland-gl-context.patch` | Fix crash with Wayland + OpenGL context | ✅ Active |

### Removed Patches

| Patch | Purpose | Reason |
|-------|---------|--------|
| `002-fix_configure.patch` | pkg-config detection workaround | Broken workaround, no longer needed |

### Disabled Patches

| Patch | Purpose | Status |
|-------|---------|--------|
| `xxx-opengl-hybrid.patch.disabled` | OpenGL hybrid rendering | Disabled (not needed for REG Linux) |

---

## Sub-packages

### 1. libretro-core-info

**Purpose**: Core information files for all libretro cores.

**Install Path**: `/usr/share/libretro/info/`

**Features**:
- Core metadata (name, version, extensions)
- Symlinks for compatibility (e.g., `beetle-saturn_libretro.info` → `mednafen_saturn_libretro.info`)

### 2. retroarch-assets

**Purpose**: UI assets (icons, themes, backgrounds).

**Install Path**: `/usr/share/libretro/assets/`

**Included Assets**:
- `rgui/` - RGUI menu theme
- `glui/` - GLUI menu theme
- `xmb/monochrome/` - XMB monochrome icons
- `ozone/` - Ozone menu assets (GLES3 only)

### 3. retroarch-joypad-autoconfig

**Purpose**: Controller auto-configuration profiles.

**Install Path**: `/usr/share/reglinux/datainit/system/configs/retroarch/autoconfig/`

**Included Profiles**:
- `hid/` - HID controllers
- `linuxraw/` - Linux raw input
- `sdl2/` - SDL2 controllers
- `udev/` - udev controllers
- `x/` - XInput controllers
- `xinput/` - XInput profiles
- `rocknix/` - Additional profiles from ROCKNIX

### 4. shaders

**Purpose**: Shader collections for video processing.

#### 4.1 common-shaders
**Purpose**: Common shader presets.

#### 4.2 glsl-shaders
**Purpose**: GLSL shader collection.

#### 4.3 slang-shaders
**Purpose**: Slang shader collection (requires Vulkan).

---

## Configuration

### Default Config Path

REG Linux uses `/configs/retroarch/` instead of `~/.config/retroarch/`:

```
/configs/retroarch/
├── retroarch.cfg           # Main configuration
├── autoconfig/             # Controller profiles
├── cores/                  # Core-specific configs
├── overlays/               # Overlay configs
├── playlists/              # Game playlists
└── screenshots/            # Screenshots
```

### D-Bus Configuration

GameMode requires D-Bus configuration:

```bash
/etc/dbus-1/system.d/gamemode.conf
```

Installed automatically by gamemode package.

### Init Script

GameMode daemon starts at boot:

```bash
/etc/init.d/S60gamemoded
```

---

## Build Notes

### Cross-Compilation Fixes

1. **PKG_CONFIG_PATH**: Set to find libs in sysroot
   ```makefile
   PKG_CONFIG_PATH=$(STAGING_DIR)/usr/lib/pkgconfig:$(STAGING_DIR)/usr/share/pkgconfig
   ```

2. **Internal Headers**: Added to CFLAGS
   ```makefile
   -I$(@D)/libretro-common/include -I$(@D)
   ```

3. **Unsafe Include Removal**: Strip `-I/usr/include` from CFLAGS
   ```makefile
   CFLAGS="$(subst -I/usr/include,,$(TARGET_CFLAGS)) ..."
   ```

### Known Issues

1. **gamemode**: Requires D-Bus and daemon running. May be disabled for minimal builds.

2. **Wayland + OpenGL**: Patch `999-hotfix-crash-wayland-gl-context.patch` fixes crash.

3. **Ozone Menu**: Only available on GLES3 devices. GLES2 devices use XMB.

4. **libpng/libjpeg**: Auto-detected, not in DEPENDENCIES. Will be available if other packages select them.

---

## Testing

### Build Test

```bash
make retroarch
make retroarch-dirclean
make retroarch-rebuild
```

### Runtime Test

```bash
# Start RetroArch
retroarch

# Check config path
retroarch --config /configs/retroarch/retroarch.cfg

# List cores
retroarch --menu
```

### Feature Verification

```bash
# Check gamemode integration
gamemode-request -r

# Check Wayland support
retroarch --video-driver gl

# Check ALSA audio
retroarch --audio-driver alsa
```

---

## References

- **Official Website**: https://www.libretro.com/
- **GitHub**: https://github.com/libretro/RetroArch
- **Documentation**: https://docs.libretro.com/
- **Libretro Cores**: https://docs.libretro.com/gaming/cores/

---

## Maintainer Notes

### Adding New Patches

1. Create patch in `package/retroarch/retroarch/`
2. Number sequentially (e.g., `024-my-patch.patch`)
3. Test with `make retroarch-rebuild`
4. Document in this README

### Updating Version

1. Update `RETROARCH_VERSION` in `retroarch.mk`
2. Update hash in `retroarch.hash`
3. Test all patches apply cleanly
4. Verify runtime functionality

### Removing Patches

When upstreaming patches:
1. Check if patch is in upstream RetroArch
2. Remove from `retroarch/` directory
3. Update this README
4. Test build without patch
