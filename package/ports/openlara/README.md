# OpenLara

Tomb Raider 1 open-source engine. Upstream: https://github.com/XProger/OpenLara

Has no CMake or autotools; the recipe calls `$(TARGET_CXX)` directly with `sdl2-config` flags. Selects GL on x86_64 or GLES2/GLES3 on other targets. On OdroidC5 with Mali GPU, `-lmali` is appended to the link line.
