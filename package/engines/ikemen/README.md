# ikemen

MUGEN-compatible fighting engine (Ikemen GO). Upstream: https://github.com/ikemen-engine/Ikemen-GO

Uses `golang-package` but overrides `BUILD_CMDS` to invoke the project's own `Makefile` with `CGO_ENABLED=1` and the cross-toolchain's Go environment variables.
