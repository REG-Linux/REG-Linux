# libretro-holani

Atari Lynx libretro core (Holani). Upstream: https://github.com/lleny/holani-retro

Uses `cargo-package`; requires `host-rustc`, `clang`, and `llvm`. `BINDGEN_EXTRA_CLANG_ARGS` and `LIBCLANG_PATH` are set explicitly to point bindgen at the host clang headers.
