# felix86

x86_64 emulator targeting RISC-V hosts. Upstream: https://github.com/OFFTKP/felix86

Thunking (host GL/Vulkan library passthrough) is enabled only when desktop GL, Vulkan, and X11 are all present simultaneously (`-DBUILD_THUNKING=ON/OFF`).
