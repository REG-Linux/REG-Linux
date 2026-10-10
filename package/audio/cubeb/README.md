# cubeb

**Cross-platform audio library**

Upstream: https://github.com/mozilla/cubeb

## Version

- **Current**: 0.2.20
- **License**: ISC

## Description

Cubeb is a cross-platform audio library that provides a consistent API for playing and recording audio across different platforms and audio systems.

Originally developed by Mozilla for Firefox, cubeb is now used by many applications including RetroArch, Cemu, and other multimedia applications.

## Features

- **Cross-platform**: Works on Linux, Windows, macOS, Android, iOS
- **Multiple backends**: ALSA, PulseAudio, JACK, sndio, AudioUnit, WASAPI
- **Low-latency**: Optimized for real-time audio playback
- **Audio mixing**: Multiple audio streams mixing
- **Device enumeration**: List available audio devices
- **Volume control**: Per-stream volume control
- **Stream parameters**: Sample rate, channels, format negotiation

## Backends

### Linux Backends

| Backend | Status | Package | Notes |
|---------|--------|---------|-------|
| **ALSA** | ✅ Tier-3 | `alsa-lib` | Default for embedded |
| **PulseAudio** | ✅ Tier-1 (Rust) / Tier-4 (C) | `pulseaudio` | Desktop Linux |
| **JACK** | ✅ Tier-3 | `jack2` | Professional audio |

### Backend Tiers

- **Tier-1**: Actively maintained, CI coverage, critical for Firefox
- **Tier-3**: Maintainers/patches accepted, status unclear
- **Tier-4**: Deprecated, obsolete, scheduled for removal

## Dependencies

### Mandatory

| Package | Purpose |
|---------|---------|
| `alsa-lib` | ALSA backend (default) |
| `speexdsp` | Audio processing (resampling, echo cancellation) |

### Optional

| Package | Purpose | Config Option |
|---------|---------|---------------|
| `pulseaudio` | PulseAudio backend | `BR2_PACKAGE_CUBEB_BACKEND_PULSEAUDIO` |
| `jack2` | JACK backend | `BR2_PACKAGE_CUBEB_BACKEND_JACK` |

### Build Tools

| Package | Purpose |
|---------|---------|
| `cmake` | Build system |
| `host-pkgconf` | pkg-config |

## Build Configuration

### CMake Options

```cmake
-DCMAKE_BUILD_TYPE=Release
-DBUILD_SHARED_LIBS=ON
-DBUILD_TESTS=OFF
-DENABLE_SANITIZERS=OFF
-DBUILD_RUST_LIBS=OFF
```

### Backend Selection

```cmake
# ALSA backend (default)
-DBUILD_BACKEND_ALSA=ON

# PulseAudio backend
-DBUILD_BACKEND_PULSEAUDIO=ON

# JACK backend
-DBUILD_BACKEND_JACK=ON
```

### Rust Backends

```cmake
# Disabled by default (requires Rust toolchain)
-DBUILD_RUST_LIBS=OFF

# Enable for PulseAudio Rust backend (better support)
-DBUILD_RUST_LIBS=ON
```

**Note**: Rust backends provide better support (Tier-1 for PulseAudio) but require Rust toolchain. For embedded systems, C backends (Tier-3) are sufficient.

## Configuration (Buildroot)

### Minimal (ALSA only)

```
BR2_PACKAGE_CUBEB=y
BR2_PACKAGE_CUBEB_BACKEND_ALSA=y
# BR2_PACKAGE_CUBEB_BACKEND_PULSEAUDIO is not set
# BR2_PACKAGE_CUBEB_BACKEND_JACK is not set
```

### Desktop (PulseAudio)

```
BR2_PACKAGE_CUBEB=y
BR2_PACKAGE_CUBEB_BACKEND_ALSA=y
BR2_PACKAGE_CUBEB_BACKEND_PULSEAUDIO=y
# BR2_PACKAGE_CUBEB_BACKEND_JACK is not set
```

### Professional Audio (JACK)

```
BR2_PACKAGE_CUBEB=y
BR2_PACKAGE_CUBEB_BACKEND_ALSA=y
# BR2_PACKAGE_CUBEB_BACKEND_PULSEAUDIO is not set
BR2_PACKAGE_CUBEB_BACKEND_JACK=y
```

## Installation

### Target Paths

```
/usr/lib/
├── libcubeb.so          # Shared library
└── libcubeb.so.2        # Versioned symlink

/usr/include/
└── cubeb/
    ├── cubeb.h          # Main header
    └── cubeb_export.h   # Export macros
```

### Staging

Cubeb is installed to staging for development:

```
output/build/cubeb-*/staging/usr/lib/libcubeb.so
output/build/cubeb-*/staging/usr/include/cubeb/
```

## Usage

### C API Example

```c
#include <cubeb/cubeb.h>

cubeb *ctx;
cubeb_init(&ctx, "My Application", NULL);

// Enumerate devices
cubeb_device_collection devices;
cubeb_enumerate_devices(ctx, CUBEB_DEVICE_TYPE_OUTPUT, &devices);

// Create audio stream
cubeb_stream *stream;
cubeb_stream_init(ctx, &stream, "Stream", NULL, &input_params,
                  &output_params, latency, data_callback, state_callback,
                  user_ptr);

// Start playback
cubeb_stream_start(stream);

// Cleanup
cubeb_stream_destroy(stream);
cubeb_destroy(ctx);
```

### Backend Selection

Cubeb automatically selects the best available backend:

1. **PulseAudio** (if available and enabled)
2. **JACK** (if available and enabled)
3. **ALSA** (fallback, always available)

To force a specific backend, use environment variable:

```bash
# Force ALSA backend
export CUBEB_BACKEND=alsa

# Force PulseAudio backend
export CUBEB_BACKEND=pulse

# Force JACK backend
export CUBEB_BACKEND=jack
```

## Known Issues

1. **Rust backends**: Require Rust toolchain, not enabled by default
2. **PulseAudio C backend**: Deprecated (Tier-4), use Rust backend or ALSA
3. **JACK**: Requires JACK server running, not suitable for all embedded systems

## Testing

### Build Test

```bash
make cubeb
make cubeb-dirclean
make cubeb-rebuild
```

### Runtime Test

```bash
# List available backends
cubeb-test --list-backends

# Test audio playback
cubeb-test --test-playback

# Test recording
cubeb-test --test-recording
```

## Applications Using Cubeb

- **Firefox** (original developer)
- **RetroArch** (audio driver)
- **Cemu** (Wii U emulator)
- **mpv** (optional audio backend)
- **Discord** (Linux audio)

## References

- **GitHub**: https://github.com/mozilla/cubeb
- **Documentation**: https://mozilla.github.io/cubeb/
- **AUR Package**: https://aur.archlinux.org/packages/cubeb-git
- **Firefox Audio**: https://wiki.mozilla.org/Audio

## Maintainer Notes

### Updating Version

1. Update `CUBEB_VERSION` in `cubeb.mk`
2. Verify hash with `make cubeb-dirclean && make cubeb`
3. Test with applications (RetroArch, Cemu)

### Adding Rust Backend Support

To enable Rust backends:

1. Add `select BR2_PACKAGE_RUST` to `Config.in`
2. Change `-DBUILD_RUST_LIBS=OFF` to `ON` in `cubeb.mk`
3. Add LDFLAGS for Rust linking
4. Test with PulseAudio backend

### Removing Backends

For minimal builds, disable backends:

```makefile
CUBEB_CONF_OPTS += -DBUILD_BACKEND_JACK=OFF
CUBEB_CONF_OPTS += -DBUILD_BACKEND_PULSEAUDIO=OFF
```

Only ALSA is required for basic functionality.
