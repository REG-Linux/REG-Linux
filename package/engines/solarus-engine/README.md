# Solarus

Lua-scripted action-RPG engine. Upstream: https://gitlab.com/solarus-games/solarus

Staging install is enabled so that game packages can link against `libsolarus.so`. GLES is enabled when the target has no desktop GL. Write directory is hardwired to `/userdata/saves/solarus`. The Qt5 launcher GUI is disabled; only the headless library and SDL2 runtime are built.
