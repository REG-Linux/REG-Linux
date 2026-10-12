# ikemen

**MUGEN-compatible fighting engine (Ikemen GO)**

Upstream: https://github.com/ikemen-engine/Ikemen-GO

## Version

- **Commit**: `3a6286127d14167e14e14c4b1be9a50c13114b23` (March 16, 2026)
- **Branch**: master

## Architecture

- **Supported**: Any architecture supported by Go with CGO and SDL2
- **Build tags**: `!raw && !android` for desktop features (dialogs, windowing)

## Dependencies

### Runtime Dependencies

| Package   | Purpose                                                               | Required? |
| --------- | --------------------------------------------------------------------- | --------- |
| `libgtk3` | Message dialogs via `sqweek/dialog` (ShowInfoDialog, ShowErrorDialog) | ✅ Yes    |
| `sdl2`    | Windowing, input (keyboard/gamepad), audio output, OpenGL context     | ✅ Yes    |
| `libgl`   | OpenGL 3.3 Core rendering                                             | ✅ Yes    |

**Note**: SDL2 automatically pulls in required X11 dependencies (X11, Xcursor, Xrandr, Xinerama) when building with X11 support.

### Build Dependencies (Go modules)

The following Go modules are automatically fetched during build:

| Module                            | Purpose                                        |
| --------------------------------- | ---------------------------------------------- |
| `github.com/veandco/go-sdl2`      | SDL2 bindings for Go (windowing, input, audio) |
| `github.com/go-gl/gl/v3.3-core`   | OpenGL 3.3 Core bindings                       |
| `github.com/go-gl/mathgl`         | 3D math library (matrices, vectors)            |
| `github.com/gopxl/beep/v2`        | Audio mixing and streaming                     |
| `github.com/sqweek/dialog`        | Native file/message dialogs (GTK3 on Linux)    |
| `github.com/yuin/gopher-lua`      | Lua VM for game scripting                      |
| `github.com/flopp/go-findfont`    | System font discovery                          |
| `github.com/tidwall/gjson`        | JSON parsing                                   |
| `github.com/tidwall/sjson`        | JSON modification                              |
| `gopkg.in/ini.v1`                 | INI file parsing                               |
| `golang.org/x/mobile`             | Mobile support utilities                       |
| `github.com/ikemen-engine/reisen` | Vulkan support (optional)                      |
| `github.com/qmuntal/gltf`         | 3D model loading (glTF format)                 |
| `github.com/lukegb/dds`           | DDS texture loading                            |
| `github.com/assemblaj/ggpo`       | Rollback netcode                               |

### Removed Dependencies

| Package   | Reason                                   |
| --------- | ---------------------------------------- |
| `libglfw` | Migrated to SDL2 for windowing and input |
| `openal`  | Audio now uses SDL2 + Beep instead       |

## Build System

### Build Process

Ikemen GO uses a **custom Makefile** with Go modules:

```makefile
# 1. Clean up go.mod (remove orphaned dependencies like glfw)
go mod tidy

# 2. Build with CGO enabled
make Ikemen_GO_Linux
```

### Build Tags

| Tag        | Effect                                        |
| ---------- | --------------------------------------------- |
| `!raw`     | Enables desktop features (dialogs, windowing) |
| `!android` | Enables desktop-specific code paths           |

Files affected:

- `util_desktop.go` - Dialog functions, font loading, renderer selection
- `input_sdl.go` - SDL2 input handling
- `audio_sdl.go` - SDL2 audio output
- `system_sdl.go` - SDL2 system integration

### Graphics Backends

| Backend             | File               | Status          |
| ------------------- | ------------------ | --------------- |
| **OpenGL 3.3 Core** | `render_gl33.go`   | ✅ Primary      |
| **OpenGL ES 3.2**   | `render_gles32.go` | ⚠️ Alternative  |
| **Vulkan 1.3**      | `render_vk.go`     | 🔧 Experimental |

Default: OpenGL 3.3 Core (can be changed via config)

## Patches

No patches currently required. The package builds cleanly with the upstream Makefile.

## Installation Paths

| Path                           | Content                                        |
| ------------------------------ | ---------------------------------------------- |
| `/usr/bin/ikemen`              | Main executable                                |
| `/usr/share/ikemen/`           | Game data, characters, stages (user-installed) |
| `~/.ikemen/` or `~/Ikemen-GO/` | User configuration, saves, replays             |

## Configuration

### Video Settings

Config file location: `~/.ikemen/config.ini` or `Ikemen-GO/config.ini`

```ini
[Video]
Renderer = GL33  ; Options: GL33, GLES32, VK
Fullscreen = 1
Width = 1920
Height = 1080
RefreshRate = 60
VSync = 1
```

### Input Configuration

Gamepad mappings use SDL2 GameController format:

```ini
[Input]
P1.Input = sdl
P1.Device = 0
P1.Up = 12
P1.Down = 13
P1.Left = 14
P1.Right = 15
P1.A = 1
P1.B = 0
; ... etc
```

### Audio Settings

```ini
[Audio]
Volume = 100
Channels = 2
SampleRate = 44100
```

## Technical Details

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Ikemen GO                         │
├─────────────┬─────────────┬─────────────────────────┤
│   Input     │   Audio     │      Graphics           │
│   (SDL2)    │  (SDL2+Beep)│    (OpenGL 3.3/Vulkan)  │
├─────────────┴─────────────┴─────────────────────────┤
│              Desktop Utilities                       │
│         (sqweek/dialog → GTK3 on Linux)             │
└─────────────────────────────────────────────────────┘
```

### Key Components

| Component            | Implementation                 |
| -------------------- | ------------------------------ |
| **Game Logic**       | Lua scripting (gopher-lua)     |
| **Rollback Netcode** | GGPO (assemblaj/ggpo)          |
| **Audio Mixing**     | Beep v2 with SDL2 output       |
| **Font Rendering**   | OpenGL bitmap fonts + FreeType |
| **Image Loading**    | PNG, DDS formats               |
| **Video Playback**   | FFmpeg (external dependency)   |
| **Message Dialogs**  | sqweek/dialog (GTK3 on Linux)  |

### Memory Management

- Uses Go's garbage collector for most allocations
- OpenGL textures/buffers managed manually via `runtime.Pinner`
- Arena allocator (`arena` package) for performance-critical code

## Known Issues

### Build Issues

1. **go.mod may contain orphaned dependencies**: The `glfw` package is still listed but not used. Fixed by running `go mod tidy` before build.

2. **CGO required**: Cannot build with `CGO_ENABLED=0` due to SDL2 and GTK3 dependencies.

### Runtime Issues

1. **GTK3 dialogs on Wayland**: May show X11 warning dialogs on pure Wayland sessions. Consider using XWayland.

2. **Gamepad hotplugging**: SDL2 gamepad detection works, but some controllers may need manual mapping via `SDL_GAMECONTROLLERCONFIG`.

3. **Vulkan support**: The Vulkan renderer (`render_vk.go`) is experimental and may not work on all hardware.

## Migration Notes (GLFW → SDL2)

The project migrated from GLFW to SDL2 for better cross-platform support:

| Feature        | Before (GLFW) | After (SDL2)              |
| -------------- | ------------- | ------------------------- |
| Windowing      | GLFW          | SDL2                      |
| Input          | GLFW          | SDL2 GameController       |
| Audio          | Beep + Oto    | SDL2 Audio + Beep         |
| OpenGL Context | GLFW          | SDL2 GLContext            |
| Dialogs        | sqweek/dialog | sqweek/dialog (unchanged) |

**Benefits:**

- Better gamepad support (SDL2 GameController API)
- Audio output integrated with main event loop
- More consistent cross-platform behavior
- Easier Android/iOS porting in the future

## References

- **Official Website**: https://ikemen-engine.github.io/
- **GitHub**: https://github.com/ikemen-engine/Ikemen-GO
- **Wiki**: https://github.com/ikemen-engine/Ikemen-GO/wiki
- **MUGEN Compatibility**: Designed for MUGEN 1.1+ content
- **Discord**: https://discord.gg/ikemengo

## See Also

- [MUGEN](https://www.electrobyte.net/mugen/) - Original fighting game engine
- [Ikemen ZE](https://github.com/IKEMEN-Project/Ikemen) - Predecessor project
- [GGPO](https://github.com/poncle/ggpo) - Rollback netcode library
