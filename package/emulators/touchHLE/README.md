# BR2_PACKAGE_TOUCHHLE

touchHLE is a high-level emulator for iPhone OS apps. It runs on modern desktop operating systems and Android, and is written in Rust. https://github.com/touchHLE/touchHLE

## Build notes

- ``Version``: v0.2.2
- ``Config``: select BR2_PACKAGE_HOST_RUSTC, depends on BR2_PACKAGE_HOST_RUSTC_TARGET_ARCH_SUPPORTS
- ``Build helper``: Rust (rust-package)
