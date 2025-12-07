# BR2_PACKAGE_GOPHER64

See Buildroot configs for details.

## Build notes

- ``Version``: v1.1.9
- ``Config``: select BR2_PACKAGE_HOST_RUSTC, depends on BR2_PACKAGE_HOST_RUSTC_TARGET_ARCH_SUPPORTS, depends on BR2_PACKAGE_CLANG, depends on BR2_PACKAGE_WAYLAND, depends on BR2_PACKAGE_ALSA_LIB, depends on BR2_PACKAGE_HAS_LIBGL, depends on BR2_PACKAGE_XWAYLAND, depends on BR2_PACKAGE_VULKAN_HEADERS, depends on BR2_PACKAGE_VULKAN_LOADER
- ``Build helper``: Rust (rust-package)
- ``Extras``: applies patches: 001-lto-auto.patch
