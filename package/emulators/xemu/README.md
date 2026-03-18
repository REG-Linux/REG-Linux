# xemu

Original Xbox emulator (QEMU-based). Upstream: https://github.com/xemu-project/xemu

Uses autotools configure (`--target-list=i386-softmmu`). `host-libcurl` is required at build time for downloading metadata. KVM, VNC, tools, docs, and guest-agent are all disabled.
