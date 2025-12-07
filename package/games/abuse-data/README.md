# Abuse data pack

Provides the original data files for *Abuse*, consumed by the `abuse` package.

## Build notes
- **Version:** 2.00 tarball (Public Domain) downloaded from `abuse.zoy.org`.
- **Build system:** simple `generic-package` that untars the archive and installs its contents under `/usr/share/abuse`.
- **Notes:** the README highlights that the same files are also delivered through the content downloader (Pacman package), so this Buildroot package exists mostly for reference/backwards compatibility.
