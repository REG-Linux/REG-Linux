# Lightspark Flash emulator

Lightspark is REG-Linux's GPLv3 Flash runtime alternative.

## Configuration
- **Version:** 0.9.0 release (February 2025) with additional fixes for GLES.
- **Config selects:** freetype, pcre, jpeg, libpng, SDL2, Cairo, FFmpeg, libcurl, Pango, rtmpdump, and optionally libglew when desktop OpenGL is available.
- **Build system:** CMake; disables browser plugins and lets the build decide between desktop GL and GLES2 depending on `BR2_PACKAGE_HAS_LIBGL`. Adds SSE2 on x86_64 and `-DEGL_NO_X11` when GLES is forced.

## Extras
- Applies `001-wip-following-0.9.0-release.patch` to restore GLES support that broke in upstream 0.9.0.
- Installs `flash.lightspark.keys` under `/usr/share/evmapy` so the emulator can pair with the REG-Linux frontend.
