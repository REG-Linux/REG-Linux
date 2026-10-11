#!/usr/bin/env python3
"""
yaml-tier-filter.py — rewrite installed rendering-defaults YAMLs so every
`shader: <path>` reference points to a preset that was actually installed for
the current tier. References to presets filtered out by tier are either
replaced with a known-safe fallback or removed so the entry inherits from the
YAML's `default:` block.

Rationale: the tier system is authoritative. YAMLs inherited from the batocera
fork may reference shaders above the selected tier; those must be stripped at
install time rather than force-installed.

Called from reglinux-shaders.mk during INSTALL after tier-install.py.
"""
import argparse
import re
from pathlib import Path

# Matches a YAML "shader: <value>" line (with optional leading whitespace and
# trailing comment). Captures indent, key-and-colon, value, and trailing.
SHADER_LINE_RE = re.compile(
    r'^(?P<indent>\s*)shader:\s*(?P<value>[^#\r\n]*?)(?P<trail>\s*(?:#.*)?)\s*$'
)


def preset_installed(shader_ref: str, shaders_root: Path) -> bool:
    """Return True if either <root>/<ref>.glslp or <root>/slang-shaders/<ref>.slangp exists."""
    ref = shader_ref.strip().strip('"').strip("'")
    if not ref:
        return True  # empty shader: line is valid (means "no shader")
    if (shaders_root / f"{ref}.glslp").is_file():
        return True
    if (shaders_root / "slang-shaders" / f"{ref}.slangp").is_file():
        return True
    return False


def rewrite_yaml(yml_path: Path, shaders_root: Path, fallback: str | None) -> tuple[int, int]:
    """Rewrite one YAML in place. Returns (dropped, kept) counts for reporting."""
    try:
        lines = yml_path.read_text(errors="replace").splitlines(keepends=True)
    except OSError:
        return (0, 0)

    dropped = 0
    kept = 0
    out = []
    for line in lines:
        m = SHADER_LINE_RE.match(line)
        if not m:
            out.append(line)
            continue
        value = m.group("value").strip().strip('"').strip("'")
        if preset_installed(value, shaders_root):
            out.append(line)
            kept += 1
            continue

        dropped += 1
        if fallback:
            newline = line.rstrip("\r\n")
            newline = re.sub(
                r'shader:\s*[^#\r\n]*',
                f"shader: {fallback}",
                newline,
                count=1,
            )
            suffix = "\r\n" if line.endswith("\r\n") else ("\n" if line.endswith("\n") else "")
            out.append(newline + suffix)
        # else: drop the line entirely (system inherits from `default:`)

    if dropped:
        yml_path.write_text("".join(out))
    return (dropped, kept)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--yaml-dir",
        required=True,
        help="Directory containing installed rendering-defaults*.yml files (recurses).",
    )
    ap.add_argument(
        "--shaders-root",
        required=True,
        help="Root dir of installed shader presets (e.g. /usr/share/reglinux/shaders).",
    )
    ap.add_argument(
        "--fallback",
        default="interpolation/sharp-bilinear-simple",
        help="Shader path to substitute for missing refs (T0-safe). "
        "Pass empty string to drop the line instead.",
    )
    args = ap.parse_args()

    yaml_dir = Path(args.yaml_dir)
    shaders_root = Path(args.shaders_root)
    fallback = args.fallback or None

    # If the chosen fallback isn't installed either, drop lines instead of substituting.
    if fallback and not preset_installed(fallback, shaders_root):
        fallback = None

    total_dropped = 0
    total_kept = 0
    for yml in sorted(yaml_dir.rglob("*.yml")):
        dropped, kept = rewrite_yaml(yml, shaders_root, fallback)
        total_dropped += dropped
        total_kept += kept

    print(
        f"  YAML filter: kept {total_kept} tier-safe refs, "
        f"rewrote {total_dropped} tier-violating refs"
        + (f" to '{fallback}'" if fallback else " (lines dropped)")
    )


if __name__ == "__main__":
    main()
