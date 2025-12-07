# Ruffle desktop

`ruffle` compiles the Rust-based Flash emulator desktop binary and ships the REG-Linux key list used for controller mappings.

## Configuration
- **Version:** nightly build (`nightly-2025-10-31`) from the `ruffle-rs/ruffle` repo.
- **Config selections:** requires UDEV, ALSA, and a Rust compiler/toolchain with host `rustc` support.
- **Build system:** uses the `rust-package` helper; the desktop binary is built from `desktop/` and then renamed/stripped as `ruffle` in `/usr/bin`.
- **Post-install:** copies `flash.ruffle.keys` into `/usr/share/evmapy`.
