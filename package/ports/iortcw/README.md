# IORTCW

Return to Castle Wolfenstein source port. Upstream: https://github.com/iortcw/iortcw

Builds SP and MP separately from `SP/` and `MP/` subdirectories. On x86_64, VOIP, codec, bloom, and the rend2 renderer are enabled; on AArch64 and RISC-V they are disabled and GLES is used instead. A `wolfconfig.cfg` is copied to the datainit tree to ensure fullscreen on first launch.
