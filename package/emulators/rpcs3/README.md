# rpcs3

PlayStation 3 emulator. Upstream: https://github.com/RPCS3/rpcs3

Requires LLVM and Qt6. `-DUSE_NATIVE_INSTRUCTIONS=OFF` and `-DSTATIC_LINK_LLVM=OFF` are set for cross-compilation. All system libraries (curl, ffmpeg, libpng, libusb, pugixml, rtmidi, zlib, zstd) are used from staging rather than the bundled copies.
