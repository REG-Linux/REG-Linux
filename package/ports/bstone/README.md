# bstone (Blake Stone)

`bstone` packages the Blake Stone (Aliens Of Gold / Planet Strike) source port maintained by bibendovsky.

## Build notes
- **Version:** v1.2.16 (May 2025 release).
- **Config:** selects `SDL2`, `OpenAL`, and copies the `bstone.keys` file into `/usr/share/evmapy` for the REG-Linux frontend.
- **Build system:** CMake release build that forces static output and installs the binary into `/usr/bin`.
- **Extras:** the package stage copies the evmapy keys so the controller mappings are available on the target.
