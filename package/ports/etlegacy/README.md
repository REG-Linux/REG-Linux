# ET: Legacy

Open-source Wolfenstein: Enemy Territory continuation. Upstream: https://github.com/etlegacy/etlegacy

Uses the GLES renderer on AArch64 and RISC-V; the GL renderer on x86. The Vulkan and renderer2 paths are disabled due to build issues. `legacy_2.83-dirty.pk3` is copied to `/usr/share/etlegacy/`. Default basedir is `/userdata/roms/etlegacy`. Adds `libexecinfo` on musl. GL, GLEW, and GLU are added only when Xwayland is present.
