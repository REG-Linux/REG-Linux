# OpenMW

Morrowind engine reimplementation. Upstream: https://github.com/OpenMW/openmw

Requires desktop GL (`libgl`). Bundles OSG and MyGUI in-tree (`USE_SYSTEM_OSG/MYGUI=OFF`). `OSG_WINDOWING_SYSTEM` is set to `X11` when Xorg is present, otherwise `None`. A cross-compile hack sets `DRUN_RESULT_VAR=1` to skip the LuaJIT custom-allocator runtime test. All non-game tools (launcher, OpenCS, navmesh tool, etc.) are disabled.
