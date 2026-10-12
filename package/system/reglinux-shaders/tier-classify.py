#!/usr/bin/env python3
"""
tier-classify.py  —  build-time shader tier manifest generator
Called from reglinux-shaders.mk during the BUILD phase on the host.
"""
import argparse, re, json, os
from pathlib import Path
from collections import defaultdict

TIER_ORDER = ["T0","T1","T2","T3","T4"]

def parse_preset(path):
    kv = {}
    try:
        text = path.read_text(errors="replace")
    except Exception:
        return {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^(\w+)\s*=\s*"?([^"#\r\n]*)"?', line)
        if m:
            kv[m.group(1).strip()] = m.group(2).strip().strip('"')
    return kv

def bv(s): return s.strip().lower() in ("true","1","yes")

def classify_glslp(path):
    kv = parse_preset(path)
    if not kv:
        return {"tier":"T2","passes":0,"luts":0,"flags":["parse_error"]}
    try: n = int(kv.get("shaders","1"))
    except ValueError: n = 1
    flags = []
    has_float  = any(bv(kv.get(f"float_framebuffer{i}","false")) for i in range(n))
    has_srgb   = any(bv(kv.get(f"srgb_framebuffer{i}","false"))  for i in range(n))
    has_mipmap = any(bv(kv.get(f"mipmap_input{i}","false"))       for i in range(n))
    has_fb     = any(
        bv(kv.get(f"feedback_pass{i}","false")) or
        "prev" in kv.get(f"alias{i}","").lower() or
        "feedback" in kv.get(f"alias{i}","").lower()
        for i in range(n))
    tex_str   = kv.get("textures","")
    has_hist  = "history" in tex_str.lower() or any(
        re.search(r'\bprev\d*\b', kv.get(f"alias{i}",""), re.I) for i in range(n))
    n_luts = len([t for t in tex_str.split(";") if t.strip()]) if tex_str else 0
    if has_float:  flags.append("float_fb")
    if has_srgb:   flags.append("srgb_fb")
    if has_mipmap: flags.append("mipmap")
    if has_fb:     flags.append("feedback")
    if has_hist:   flags.append("history")
    if n_luts:     flags.append(f"luts:{n_luts}")
    if   n >= 9: tier = "T4"
    elif n >= 5: tier = "T3"
    elif n >= 3: tier = "T2"
    elif n == 2: tier = "T1"
    else:        tier = "T0"
    if (has_fb or has_hist) and TIER_ORDER.index(tier) < 3: tier = "T3"
    if has_float             and TIER_ORDER.index(tier) < 2: tier = "T2"
    if has_srgb              and TIER_ORDER.index(tier) < 1: tier = "T1"
    return {"tier":tier,"passes":n,"luts":n_luts,"flags":flags}

def classify_slangp(path):
    kv = parse_preset(path)
    try: n = int(kv.get("shaders","1"))
    except ValueError: n = 1
    flags = ["vulkan_only"]
    tex_str = kv.get("textures","")
    n_luts = len([t for t in tex_str.split(";") if t.strip()]) if tex_str else 0
    if n_luts: flags.append(f"luts:{n_luts}")
    if any(bv(kv.get(f"float_framebuffer{i}","false")) for i in range(n)): flags.append("float_fb")
    if any(bv(kv.get(f"feedback_pass{i}","false"))     for i in range(n)): flags.append("feedback")
    return {"tier":"T4","passes":n,"luts":n_luts,"flags":flags}

def collect(root, ext, classifier):
    results = {}
    for p in sorted(root.rglob(f"*.{ext}")):
        rel = str(p.relative_to(root))
        info = classifier(p)
        info["type"] = ext
        parts = p.relative_to(root).parts
        info["category"] = parts[0] if len(parts) > 1 else "root"
        results[rel] = info
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glsl-root",  required=True)
    ap.add_argument("--slang-root", required=True)
    ap.add_argument("--output",     required=True)
    args = ap.parse_args()
    glsl  = collect(Path(args.glsl_root),  "glslp",  classify_glslp)
    slang = collect(Path(args.slang_root), "slangp", classify_slangp)
    by_tier = defaultdict(int)
    for v in {**glsl, **slang}.values(): by_tier[v["tier"]] += 1
    for t in TIER_ORDER:
        print(f"  {t}: {by_tier[t]} presets")
    out = {
        "meta": {
            "glsl_presets":  len(glsl),
            "slang_presets": len(slang),
            "tiers": {
                "T0": "1-pass GLSL, GLES 2.0 (Mali-400/450, VideoCore IV)",
                "T1": "1-2 pass GLSL, srgb_fb, GLES 3.0+ (Mali-T720/H6, SpacemiT K1)",
                "T2": "<=4 pass GLSL, float_fb, GLES 3.2 (Mali-G31 / RK3326, H616, H700)",
                "T3": "<=8 pass GLSL, feedback/history, GLES 3.2 (Mali-G52/G57 / RK3566/3568/3576, S922X, A311D, A523/T527, RPi4)",
                "T4": "9+ pass GLSL or any slangp, Vulkan (RK3588 Panthor, x86_64, ODROID C5 libmali)",
            },
        },
        "presets": {**glsl, **slang},
    }
    with open(args.output, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {args.output} ({os.path.getsize(args.output)//1024} KB)")

if __name__ == "__main__":
    main()
