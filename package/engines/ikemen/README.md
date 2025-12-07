# Ikemen Go engine

Ikemen is a Go-based MUGEN-compatible fighting engine packaged for REG-Linux.

## Build information
- **Version:** pinned to commit `b58b000896b7d9e111727b109a0d4eca1b4bfe33` on the `Ikemen-GO` repo (September 2024 state).
- **Config deps:** requires threaded toolchains with Go support, GTK3, OpenAL, GLFW, and `libgl` for rendering.
- **Build system:** invokes the project `Makefile` via the `golang-package` helper (`IKEMEN_BUILD_CMDS` uses `host-go` environment variables with `CGO_ENABLED`).
- **Post-install:** installs the `ikemen.keys` file under `/usr/share/evmapy`.
