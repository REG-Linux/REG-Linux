# REG-Linux Package Update Checker

Uses [nvchecker](https://github.com/lilydjwg/nvchecker) to automatically check for new versions of all packages under `package/`.

## Pre-requisites

* `pip install nvchecker` (or `pip3`, `pipx`)
* `jq` (install with `apt install jq`)
* `git`
* A GitHub API token is strongly recommended (60 req/hr without, 5000/hr with). The script auto-detects tokens from `gh auth` or the `GITHUB_TOKEN` env var. You can also manually create `scripts/nvchecker/keyfile.toml`:

```toml
[keys]
github = "your_github_api_token"
```

## Usage

```bash
# Check all packages (skip commit-based for speed)
scripts/nvchecker/check_all_updates.sh --no-commits

# Only show packages with updates
scripts/nvchecker/check_all_updates.sh --no-commits --updates-only

# Filter by category
scripts/nvchecker/check_all_updates.sh --no-commits --category emulators

# Check specific packages only
scripts/nvchecker/check_all_updates.sh --select openrct2,gzdoom,flycast

# Update specific packages (writes new version to .mk files)
scripts/nvchecker/check_all_updates.sh --update openrct2,play

# Update ALL packages with available updates
scripts/nvchecker/check_all_updates.sh --no-commits --update ALL

# Check a specific directory or .mk file
scripts/nvchecker/check_all_updates.sh package/ports/
scripts/nvchecker/check_all_updates.sh package/emulators/flycast/flycast.mk

# JSON output for scripting
scripts/nvchecker/check_all_updates.sh --no-commits --json

# Debug scanning
scripts/nvchecker/check_all_updates.sh --verbose --select flycast
```

### Options

| Option | Description |
|---|---|
| `--updates-only` | Only show packages with available updates |
| `--no-commits` | Skip commit-hash-based packages (much faster) |
| `--category CAT` | Filter to one category (emulators, ports, engines, etc.) |
| `--select PKG,...` | Only check these packages (comma-separated) |
| `--update PKG,...` | Check and write new versions to .mk files |
| `--update ALL` | Update every package that has an update |
| `--json` | Machine-readable JSON output |
| `--verbose` | Show debug info during scanning |

### Categories

`emulators`, `ports`, `engines`, `retroarch`, `gpu`, `system`, `libraries`, `audio`, `network`, `controllers`, `emulationstation`, `frontends`, `themes`, `bezels`, `fonts`, `firmwares`, `boot`, `batocera`, `games`, `fpga`, `cases`, `toolchain`, `utils`

## Internals

The script handles two kinds of package versions:

* **Tag-based** (e.g. `v2.6`, `1.5.5`): nvchecker compares tags/releases directly
* **Commit-based** (40-char hex hash): the script fetches the commit date for proper comparison

### packages.exclude

Packages that can't be checked (e.g. mercurial repos). One package name per line.

### overrides.conf

Per-package nvchecker parameter overrides. Syntax: `<package>.<nvchecker_param>=<value>`.

Common overrides:
* `<pkg>.use_latest_tag="true"` — repos with tags but no releases
* `<pkg>.include_prereleases="true"` — repos with only pre-releases
* `<pkg>.exclude_regex="..."` — filter out unwanted tags
* `<pkg>.source="gitlab"` — override auto-detected source type

## Common errors

### 404 on releases/latest
The repo has tags but no releases. Add to `overrides.conf`:
```
<package>.use_latest_tag="true"
```

### Rate limited
Without a GitHub token, you're limited to 60 API calls/hour. Run `gh auth login` or set `GITHUB_TOKEN`.

## Links

* https://nvchecker.readthedocs.io/en/latest/index.html
* https://github.com/lilydjwg/nvchecker
