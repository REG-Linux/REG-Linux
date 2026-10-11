# VCMI

Heroes of Might and Magic 3 engine reimplementation. Upstream: https://github.com/vcmi/vcmi

Uses Ninja. Installs to `/usr/vcmi/` with `-DENABLE_MONOLITHIC_INSTALL=ON`. The launcher and translations require Qt6; without it, the server is also disabled. Adds `libexecinfo` on musl. MMAI is disabled pending onnxruntime support.
