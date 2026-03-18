# applewin

Apple II emulator (audetto's Linux port). Upstream: https://github.com/audetto/AppleWin

Builds the `sa2` SDL3 frontend (renamed to `applewin` on install). `host-xxd` is required to generate binary resource headers at build time. OpenGL is enabled only when desktop GL is present (`-DSA2_OPENGL=ON/OFF`).
