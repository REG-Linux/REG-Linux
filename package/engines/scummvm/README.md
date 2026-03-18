# scummvm

Adventure game interpreter (ScummVM). Upstream: https://github.com/scummvm/scummvm

GL/GLES renderer is selected per-platform; plugins (dynamic loading) are enabled on non-x86_64 targets. Tremor is used instead of libvorbis on ARM/MIPS toolchains. NEON, SSE2, and AVX2 code paths are enabled where supported.
