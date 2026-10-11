#!/usr/bin/env python3
"""
curate-install.py — install the curated per-tier shader shortlist.

Tiers are CUMULATIVE: T(n) installs its own list + every lower-tier list.
T0-T3 install from libretro/glsl-shaders as .glslp.
T4 installs BOTH formats:
  - .slangp from libretro/slang-shaders (for glcore/vulkan backends),
    translating inherited T0-T3 paths through `glslp_to_slangp` when
    slang-shaders uses a different path (null → entry is skipped).
  - .glslp from libretro/glsl-shaders for the cumulative T0-T3 list
    (for cores running on the gl backend; no path translation applied).
This dual install lets the same image serve users on either backend.

For each preset, all transitive assets are pulled in:
  - referenced shader source files (.glsl, .slang)
  - LUT textures (.png, .jpg, .tga, .bmp)
  - `#include`d files from shader sources (recursively)
  - for slangp: `#reference`d presets (recursively — Mega Bezel chains)
"""
import argparse
import json
import re
import shutil
from pathlib import Path

TIERS = ["T0", "T1", "T2", "T3", "T4"]

PRESET_ASSET_EXT = re.compile(r'\.(glsl|slang|png|jpg|jpeg|tga|bmp|inc)$', re.I)
SOURCE_EXT       = re.compile(r'\.(glsl|slang)$', re.I)
INCLUDE_RE       = re.compile(r'#include\s+[<"]([^>"]+)[>"]')
# slangp #reference directive — references another preset file
REFERENCE_RE     = re.compile(r'^\s*#reference\s+[<"]([^>"]+)[>"]', re.M)


def resolve(ref: str, base_dir: Path, root: Path):
    for candidate in (base_dir / ref, root / ref):
        try:
            c = candidate.resolve()
            if c.exists():
                return c
        except OSError:
            pass
    return None


def collect_includes(src: Path, root: Path, seen: set) -> list:
    """Recursively collect .inc/.h files referenced from a shader source."""
    deps = []
    if src in seen:
        return deps
    seen.add(src)
    try:
        text = src.read_text(errors="replace")
    except OSError:
        return deps
    for m in INCLUDE_RE.finditer(text):
        dep = resolve(m.group(1), src.parent, root)
        if dep and dep not in seen:
            deps.append(dep)
            deps.extend(collect_includes(dep, root, seen))
    return deps


def parse_preset_refs(preset: Path, root: Path) -> list:
    """Return all local asset paths referenced by a preset's key=value lines."""
    refs = []
    try:
        text = preset.read_text(errors="replace")
    except OSError:
        return refs
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^\w+\s*=\s*"?([^"#\r\n]+)"?', line)
        if not m:
            continue
        val = m.group(1).strip().strip('"')
        if not PRESET_ASSET_EXT.search(val):
            continue
        dep = resolve(val, preset.parent, root)
        if dep:
            refs.append(dep)
    return refs


def parse_slangp_references(preset: Path, root: Path) -> list:
    """Return all presets referenced via `#reference "…"` lines (slangp chains)."""
    refs = []
    try:
        text = preset.read_text(errors="replace")
    except OSError:
        return refs
    for m in REFERENCE_RE.finditer(text):
        dep = resolve(m.group(1), preset.parent, root)
        if dep:
            refs.append(dep)
    return refs


def install_file(src: Path, root: Path, dest_root: Path):
    try:
        rel = src.resolve().relative_to(root.resolve())
    except ValueError:
        return
    dst = dest_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst)


def install_preset_tree(preset: Path, root: Path, dest_root: Path,
                        preset_seen: set, inc_seen: set, is_slang: bool):
    """Install preset + transitive assets. For slangp, follow #reference chains."""
    if preset in preset_seen:
        return
    preset_seen.add(preset)
    install_file(preset, root, dest_root)

    for dep in parse_preset_refs(preset, root):
        install_file(dep, root, dest_root)
        if SOURCE_EXT.search(dep.suffix):
            for inc in collect_includes(dep, root, inc_seen):
                install_file(inc, root, dest_root)

    if is_slang:
        for ref_preset in parse_slangp_references(preset, root):
            install_preset_tree(ref_preset, root, dest_root,
                                preset_seen, inc_seen, True)


def resolve_tier_presets(tier: str, manifest: dict) -> list:
    """Return the cumulative list of path-refs for this tier (T0..T(n) union).

    For T4, lower-tier glslp paths are translated to slang-shaders paths via
    `glslp_to_slangp`; a null mapping means the entry is dropped. Preserves
    input order while deduplicating.
    """
    is_t4 = tier == "T4"
    translate = manifest.get("glslp_to_slangp", {}) if is_t4 else {}
    out, seen = [], set()
    idx = TIERS.index(tier)
    for t in TIERS[: idx + 1]:
        for ref in manifest.get(t, []):
            if is_t4 and t != "T4" and ref in translate:
                mapped = translate[ref]
                if mapped is None:
                    continue  # no slang equivalent — drop
                ref = mapped
            if ref not in seen:
                seen.add(ref)
                out.append(ref)
    return out


def install_pass(refs: list, root_dir: str, destdir: Path,
                 ext: str, is_slang: bool, label: str) -> None:
    if not refs:
        print(f"  curate-install: no presets resolved for {label}")
        return
    root = Path(root_dir).resolve()
    if not root.is_dir():
        raise SystemExit(f"curate-install: source root not found: {root}")

    preset_seen: set = set()
    inc_seen:    set = set()
    n_ok = n_miss = 0
    for ref in refs:
        preset = root / f"{ref}{ext}"
        if not preset.is_file():
            print(f"  curate-install: MISS {label} {ref}{ext}")
            n_miss += 1
            continue
        install_preset_tree(preset, root, destdir,
                            preset_seen, inc_seen, is_slang)
        n_ok += 1

    msg = (f"  curate-install {label}: installed {n_ok}/{len(refs)} listed presets; "
           f"{len(preset_seen)} preset files total + {len(inc_seen)} include files")
    if n_miss:
        msg += f" ({n_miss} missing)"
    print(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest",   required=True,
                    help="Path to shaders-per-tier.json.")
    ap.add_argument("--tier",       required=True, choices=TIERS)
    ap.add_argument("--glsl-root",  required=True,
                    help="Extracted libretro/glsl-shaders source root.")
    ap.add_argument("--slang-root", required=True,
                    help="Extracted libretro/slang-shaders source root. "
                         "Required for T4; ignored otherwise.")
    ap.add_argument("--destdir",    required=True,
                    help="Install root, e.g. /usr/share/reglinux/shaders.")
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    destdir  = Path(args.destdir)
    destdir.mkdir(parents=True, exist_ok=True)

    if args.tier == "T4":
        # T4 ships both formats so the same image works on the gl
        # backend (.glslp) and the glcore/vulkan backends (.slangp).
        slang_refs = resolve_tier_presets("T4", manifest)
        install_pass(slang_refs, args.slang_root, destdir,
                     ".slangp", True, "T4 (slangp)")
        # Cumulative T0-T3 glsl paths, no glslp_to_slangp translation.
        glslp_refs = resolve_tier_presets("T3", manifest)
        install_pass(glslp_refs, args.glsl_root, destdir,
                     ".glslp", False, "T4 (glslp)")
    else:
        refs = resolve_tier_presets(args.tier, manifest)
        install_pass(refs, args.glsl_root, destdir,
                     ".glslp", False, args.tier)


if __name__ == "__main__":
    main()
