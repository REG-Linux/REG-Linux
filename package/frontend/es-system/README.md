# es-system

The `es-system` Rust binary generates `rs_systems.cfg` (XML, consumed by REG-Station's system list) and `rs_features.json` (consumed by REG-Station's menu builder) from the YAML sources at build time. `es_systems.yml` defines system metadata and controls what text appears in the per-system `_info.txt` files inside `roms/`. `es_features.yml` declares per-emulator option menus consumed by REG-Station alongside regmsgd's lua generators. The `roms/` subdirectory bundles freely-licensed homebrew titles that ship pre-installed.

## On-device regeneration

The package cross-compiles the binary to `/usr/bin/es-system` as well. It is never invoked automatically — not at boot, not by REG-Station, not by regmsgd — and a stock image always runs the compile-time output in `/usr/share/regstation/`. It exists so a system list can be changed on a running device:

```sh
es-system regenerate
```

Inputs resolve `/userdata/system/configs/es-system/` first, then `/usr/share/es-system/`, per file. So the command works unmodified out of the box (regenerating byte-identically to the build), and you override only what you actually edited:

| File | Shipped in `/usr/share/es-system/` | Purpose |
|---|---|---|
| `es_systems.yml` | yes | system catalogue |
| `es_features.yml` | yes | per-emulator option menus |
| `installed-packages.conf` | yes | the `BR2_PACKAGE_*=y` set this image was built with — drives `requireAnyOf` gating |
| `arch.conf` | yes | arch tag used to filter features |
| `blacklisted-words.txt` | yes | translation blacklist (build-time only today) |

`launcher-defaults.yml` / `launcher-defaults-arch.yml` are read from `/usr/share/regmsg/launcher/` and deliberately not overridable here: regmsgd reads them from that same path (`launcher::system_map`), so a private copy would let the frontend and the launcher disagree about which emulator a system uses.

Output is written to `/userdata/system/configs/regstation/`, which every consumer already prefers over `/usr/share/regstation/` — REG-Station's `SystemData::getConfigPath()` and `CustomFeatures::loadFeatures()`, and regmsgd's `library::systems::config_path()`. Restart the frontend to pick it up.

Because those generated files win unconditionally, they are gated on the image version: `S12populateshare` renames them to `*.stale` when `/usr/share/reglinux/system.version` no longer matches `/userdata/system/data.version`. Without that, an OS update that ships a new emulator would be hidden forever behind a config generated against the old package set. Re-run `es-system regenerate` after an update to reapply your changes.

Useful flags: `--user-dir`, `--data-dir`, `--output-dir`, `--launcher-dir`, `--config`, `--arch`, `--format xml|json` (defaults to `json`, the only features format REG-Station reads).
