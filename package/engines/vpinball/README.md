# vpinball

Visual Pinball X (GL). Upstream: https://github.com/vpinball/vpinball

The platform-specific `CMakeLists_gl-linux-aarch64.txt` or `CMakeLists_gl-linux-x64.txt` is copied to the source root and its hardcoded `external/include` and `external/lib` paths are rewritten to point at the staging dir. Requires `host-dos2unix` (line-ending normalization) and downloads `libbass.so` from un4seen.com at build time. SoC-specific flags (`-DBUILD_RK3588=ON`, `-DBUILD_RPI=ON`) tune renderer code paths.
