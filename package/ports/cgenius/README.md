# Commander Genius

Commander Keen engine reimplementation. Upstream: https://github.com/gerstrong/Commander-Genius

The Cosmos episode module is cloned from a separate repository during post-extract and compiled with `-DBUILD_COSMOS=1`. Adds `libbacktrace`/`libexecinfo` on musl. Installs `cgenius.keys` into `/usr/share/evmapy/`.
