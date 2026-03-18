# EDuke32 / Fury

Build Engine port for Duke Nukem 3D and Ion Fury. Upstream: https://voidpoint.io/terminx/eduke32

The build runs twice — once for `eduke32` and once with `FURY=1` — using a custom Makefile. `STARTUP_WINDOW=0` and `HAVE_GTK2=0` are hardwired to suppress the desktop launcher dialog. Selects GLES when no desktop GL is present. Adds `libexecinfo` on musl.
