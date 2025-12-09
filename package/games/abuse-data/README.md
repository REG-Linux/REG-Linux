# Abuse data pack

The `abuse-data` package installs the up-to-date 2.00 data archive so `package/games/abuse` can run without bundling the assets directly.

## Build notes

- `Version`: 2.00 public-domain tarball from `abuse.zoy.org`.
- `Dependencies`: none beyond the standard staging (`generic-package`).
- `Build helper`: Generic/Makefile (`generic-package`) that unpacks the archive under `/usr/share/abuse`.
- `Extras`: documented as a fallback since the data is also served through REG-Linux’s content downloader/downloader package.
