#!/usr/bin/env python3
"""
tier-install.py  —  REG-Linux shader install filter
Copies presets with tier <= max_tier plus ALL referenced assets:
  - shader source files (.glsl, .slang)
  - LUT textures (.png, .jpg, .tga, .bmp)
  - include files (.inc, .h) referenced from shader sources (transitive)
"""
import argparse, json, os, re, shutil
from pathlib import Path

TIER_ORDER = ["T0", "T1", "T2", "T3", "T4"]

def tier_le(a, b):
    return TIER_ORDER.index(a) <= TIER_ORDER.index(b)

# Extensions tracked in preset key = value lines
PRESET_ASSET_EXT = re.compile(r'\.(glsl|slang|png|jpg|jpeg|tga|bmp|inc)$', re.I)
# Extensions that may themselves reference .inc files
SOURCE_EXT = re.compile(r'\.(glsl|slang)$', re.I)
# #include "foo.inc" or #include <foo.inc>
INCLUDE_RE = re.compile(r'#include\s+[<"]([^>"]+)[>"]')

def resolve(ref: str, base_dir: Path, root: Path):
    for candidate in [base_dir / ref, root / ref]:
        try:
            c = candidate.resolve()
            if c.exists():
                return c
        except Exception:
            pass
    return None

def collect_includes(src: Path, root: Path, seen: set) -> list:
    """Recursively collect .inc (and .h) files referenced from a shader source."""
    deps = []
    if src in seen:
        return deps
    seen.add(src)
    try:
        text = src.read_text(errors="replace")
    except Exception:
        return deps
    for m in INCLUDE_RE.finditer(text):
        ref = m.group(1)
        dep = resolve(ref, src.parent, root)
        if dep and dep not in seen:
            deps.append(dep)
            deps.extend(collect_includes(dep, root, seen))
    return deps

def parse_preset_refs(preset_path: Path, root: Path) -> list:
    """Return all local asset paths referenced by a preset file."""
    refs = []
    try:
        text = preset_path.read_text(errors="replace")
    except Exception:
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
        dep = resolve(val, preset_path.parent, root)
        if dep:
            refs.append(dep)
    return refs

def install_file(src: Path, root: Path, dest_root: Path):
    try:
        rel = src.relative_to(root)
    except ValueError:
        return  # outside root
    dst = dest_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest",   required=True)
    ap.add_argument("--glsl-root",  required=True)
    ap.add_argument("--slang-root", required=True)
    ap.add_argument("--destdir",    required=True)
    ap.add_argument("--max-tier",   required=True, choices=TIER_ORDER)
    ap.add_argument("--categories-file",
                    help="Optional JSON with per-tier category blocklist "
                         "(see tier-categories-blocklist.json).")
    args = ap.parse_args()

    manifest   = json.load(open(args.manifest))["presets"]
    glsl_root  = Path(args.glsl_root).resolve()
    slang_root = Path(args.slang_root).resolve()
    glsl_dest  = Path(args.destdir)
    slang_dest = Path(args.destdir) / "slang-shaders"

    blocked_categories = set()
    if args.categories_file and Path(args.categories_file).is_file():
        cats = json.load(open(args.categories_file)).get("blocklist", {})
        blocked_categories = set(cats.get(args.max_tier, []))

    inc_seen   = {}   # root -> set of already-visited include files
    n_ok = n_skip = n_miss = n_cat = 0

    for rel_path, info in manifest.items():
        if not tier_le(info["tier"], args.max_tier):
            n_skip += 1
            continue
        if info.get("category") in blocked_categories:
            n_cat += 1
            continue

        is_slang  = info["type"] == "slangp"
        root      = slang_root if is_slang else glsl_root
        dest      = slang_dest if is_slang else glsl_dest
        src       = root / rel_path

        if not src.exists():
            n_miss += 1
            continue

        install_file(src, root, dest)

        seen = inc_seen.setdefault(id(root), set())
        for dep in parse_preset_refs(src, root):
            install_file(dep, root, dest)
            # Recursively pull in .inc files from shader sources
            if SOURCE_EXT.search(dep.suffix):
                for inc in collect_includes(dep, root, seen):
                    install_file(inc, root, dest)

        n_ok += 1

    msg = f"  Installed {n_ok} presets  skipped {n_skip} (>{args.max_tier})"
    if n_cat:
        msg += f"  skipped {n_cat} (category blocked)"
    if n_miss:
        msg += f"  missing {n_miss}"
    print(msg)

if __name__ == "__main__":
    main()
