# Jazz2 Native

Jazz Jackrabbit 2 engine reimplementation. Upstream: https://github.com/deathkiller/jazz2-native

Switches the nCine backend between GLFW (when Xorg + desktop GL are present) and SDL2 with GLES. On OdroidC5 with Mali GPU, `-lmali` is injected into the linker flags. `NCINE_DOWNLOAD_DEPENDENCIES=OFF` prevents in-build fetches.
