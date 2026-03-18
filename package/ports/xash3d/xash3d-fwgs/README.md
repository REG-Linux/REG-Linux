# xash3d-fwgs

Half-Life engine reimplementation. Upstream: https://github.com/FWGS/xash3d-fwgs

Uses `waf-package`. On GLES platforms `--disable-gl --enable-gl4es` is passed; on platforms without any GL only `--disable-gl` is set, leaving the renderer unsupported. `--enable-packaging` and `--disable-menu-changegame` are always set.
