# yquake2 client

Yamagi Quake II engine. Upstream: https://github.com/yquake2/yquake2

Renderer modules are built selectively: GL1 and GL3 only when `BR2_PACKAGE_HAS_LIBGL`, GLES3 only when `BR2_PACKAGE_HAS_GLES3`. The software renderer is always included. All binaries and renderer `.so` files install under `/usr/yquake2/`. SDL3 is preferred over SDL2 when available.
