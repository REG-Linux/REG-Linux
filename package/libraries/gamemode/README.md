# GameMode - REG-Linux Package

## Overview

**GameMode** is a daemon/library for Linux that allows games to request a set of temporary optimizations to be applied to the host OS and/or a game process.

- **Version:** 1.8.2
- **Upstream:** https://github.com/FeralInteractive/gamemode
- **License:** BSD-3-Clause

## Features

GameMode applies the following optimizations when activated:

- **CPU Governor:** Switches to performance governor
- **CPU Core Parking:** Parks non-essential cores
- **GPU Clock:** Adjusts GPU frequency (when supported)
- **Split Lock Mitigate:** Adjusts CPU configuration
- **I/O Priority:** Prioritizes game processes
- **Process Scheduling:** Adjusts scheduling priority

## Package Structure

```
package/libraries/gamemode/
├── Config.in                      # Buildroot configuration
├── gamemode.mk                    # Package Makefile
├── gamemode.conf                  # D-Bus configuration
├── S60gamemoded                   # Init script (init.d)
├── 001-allow-gamemode-daemon-no-systemd.patch
├── 002-allow-gamemode-no-polkit.patch
└── 003-use-system-bus.patch
```

## Dependencies

| Dependency | Description                                                |
| ---------- | ---------------------------------------------------------- |
| `dbus`     | Messaging system for inter-process communication           |
| `basu`     | Standalone libsystemd implementation (systemd replacement) |
| `inih`     | INI file parser for configuration                          |

## Build Configuration

The package is built using **Meson** with the following options:

```makefile
GAMEMODE_CONF_OPTS = -Dwith-sd-bus-provider=basu
GAMEMODE_CONF_OPTS += -Dwith-examples=false
GAMEMODE_CONF_OPTS += -Dwith-dbus-service-dir=/usr/share/dbus-1/system-services
```

### Why `basu`?

REG-Linux uses **init-d** instead of **systemd**. The `basu` is a standalone implementation of systemd APIs (sd-bus, sd-daemon, etc.) that allows GameMode to function without depending on systemd.

## Patches

### 001-allow-gamemode-daemon-no-systemd.patch

**Purpose:** Add support for `basu` as sd-bus provider.

**Changes:**

- Adds `basu` option in `meson_options.txt`
- Conditions systemd includes with `#ifndef USE_BASU`
- Removes `sd_notify*` calls when using basu (not supported)

**Modified files:**

- `daemon/gamemode-context.c`
- `daemon/gamemode-dbus.c`
- `daemon/gamemoded.c`
- `meson.build`
- `meson_options.txt`

### 002-allow-gamemode-no-polkit.patch

**Purpose:** Remove polkit/pkexec dependency for systems without polkit.

**Justification:** In REG-Linux, the gamemoded daemon is started as root via init.d, making pkexec unnecessary for privilege elevation.

**Changes:**

- Removes `pkexec` from command calls in:
    - `gamemode-gpu.c` (gpuclockctl)
    - `gamemode-context.c` (procsysctl, cpugovctl)
    - `gamemode-cpu.c` (cpucorectl)

**Security Note:** This approach is safe because:

- The daemon can only be started as root (via init.d script)
- Linux filesystem and permissions already protect resources
- It's a common practice in embedded/simplified systems

### 003-use-system-bus.patch

**Purpose:** Change from D-Bus session bus to system bus.

**Justification:** As a system daemon, gamemoded should use the system bus for communication, allowing any user/session to communicate with it.

**Changes:**

- `daemon/gamemode-dbus.c`: `sd_bus_open_user()` → `sd_bus_open_system()`
- `lib/client_impl.c`: `DBUS_BUS_SESSION` → `DBUS_BUS_SYSTEM`

## Configuration Files

### gamemode.conf (D-Bus)

**Installation path:** `/etc/dbus-1/system.d/gamemode.conf`

**Function:** Configure access permissions for the GameMode service on D-Bus.

```xml
<policy user="root">
  <allow own="com.feralinteractive.GameMode"/>
</policy>
<policy context="default">
  <allow send_destination="com.feralinteractive.GameMode"/>
  <allow send_destination="com.feralinteractive.GameMode" send_type="method_call"/>
</policy>
```

**Policies:**

- Only **root** can "own" the service (start the daemon)
- **Any user** can send messages/method calls to the service (required for games)

### S60gamemoded (Init Script)

**Installation path:** `/etc/init.d/S60gamemoded`

**Function:** Manage the gamemoded daemon during system startup/shutdown.

**Supported commands:**

```bash
/etc/init.d/S60gamemoded start    # Start the daemon
/etc/init.d/S60gamemoded stop     # Stop the daemon
/etc/init.d/S60gamemoded restart  # Restart the daemon
/etc/init.d/S60gamemoded status   # Check daemon status
```

**Implementation details:**

- Uses `start-stop-daemon` for process management
- PID file: `/var/run/gamemoded.pid`
- Daemon: `/usr/bin/gamemoded`
- Runs in background (`-b`)
- Creates PID file automatically (`-m`)

## Installation and Hooks

### GAMEMODE_INSTALL_CONFIG

Installs the D-Bus configuration file:

```makefile
mkdir -p $(TARGET_DIR)/etc/dbus-1/system.d
cp gamemode.conf $(TARGET_DIR)/etc/dbus-1/system.d/gamemode.conf
```

### GAMEMODE_INSTALL_INIT_SYSV

Installs the init script:

```makefile
$(INSTALL) -D -m 0755 S60gamemoded $(TARGET_DIR)/etc/init.d/S60gamemoded
```

## Usage

### On the System

1. **Start the daemon:**

    ```bash
    /etc/init.d/S60gamemoded start
    ```

2. **Check status:**

    ```bash
    /etc/init.d/S60gamemoded status
    ```

3. **Stop the daemon:**
    ```bash
    /etc/init.d/S60gamemoded stop
    ```

### In Games/Applications

Games can use GameMode in two ways:

#### 1. Via LD_PRELOAD (Recommended)

```bash
gamemoderun ./my-game
```

#### 2. Via API

```c
#include <gamemode.h>

gamemode_request_start();
// ... game code ...
gamemode_request_end();
```

#### 3. Manually

```bash
# Request start
gdbus call --system com.feralinteractive.GameMode \
  /com/feralinteractive/GameMode \
  com.feralinteractive.GameMode.RegisterGame \
  <PID>

# Request end
gdbus call --system com.feralinteractive.GameMode \
  /com/feralinteractive/GameMode \
  com.feralinteractive.GameMode.UnregisterGame \
  <PID>
```

## Custom Configuration

GameMode can be configured via `/etc/gamemode.ini` file. Example:

```ini
[general]
softrealtime=auto
renice=15

[cpu]
governor=performance
parking=true

[gpu]
apply_clock_limits=false
```

Consult upstream documentation for all available options.

## Troubleshooting

### Daemon does not start

1. Check if D-Bus is running:

    ```bash
    /etc/init.d/S30dbus-daemon status
    ```

2. Check system logs:

    ```bash
    tail -f /var/log/messages
    ```

3. Test manually:
    ```bash
    /usr/bin/gamemoded -v
    ```

### Games cannot connect

1. Check D-Bus permissions:

    ```bash
    cat /etc/dbus-1/system.d/gamemode.conf
    ```

2. Check if daemon is running:

    ```bash
    ps aux | grep gamemoded
    ```

3. Test connection:
    ```bash
    gdbus call --system com.feralinteractive.GameMode \
      /com/feralinteractive/GameMode \
      org.freedesktop.DBus.Peer.Ping
    ```

## REG-Linux Integration Notes

### Systemd vs Init-D

| Feature            | Systemd            | REG-Linux (init-d)   |
| ------------------ | ------------------ | -------------------- |
| Service management | systemd units      | init.d scripts       |
| Bus provider       | libsystemd         | basu                 |
| Daemon activation  | systemd activation | manual via init.d    |
| Polkit             | Required           | Not necessary (root) |

### Why this integration works?

1. **basu** provides compatibility with systemd APIs
2. **D-Bus system bus** allows communication between users
3. **init.d script** manages the daemon as root
4. **No polkit** simplifies the architecture

## References

- **Official Repository:** https://github.com/FeralInteractive/gamemode
- **Documentation:** https://github.com/FeralInteractive/gamemode/blob/master/README.md
- **basu:** https://git.sr.ht/~emersion/basu
- **D-Bus:** https://www.freedesktop.org/wiki/Software/dbus/

## Maintenance

### Version Update

To update the package:

1. Change `GAMEMODE_VERSION` in `gamemode.mk`
2. Verify patches still apply
3. Test build and functionality
4. Update this README if necessary

### Adding Patches

1. Create patch at upstream code root
2. Name as `NNN-descriptive.patch`
3. Add references in `gamemode.mk` (automatic via buildroot)
4. Document in this README

---

**Last updated:** 2026-03-20
**Maintainer:** REG-Linux Team
