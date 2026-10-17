#!/bin/bash
#
# Compress opaque theme textures to ETC1 PKM/PKZ sidecars for GLES2 targets.
#
# Usage: compress-theme-etc1.sh <theme_dir> [uberetc1_path] [dwebp_path] [effort]
#
# For every .jpg, .png and .webp without alpha, produces a .pkm + .pkz
# sidecar. The original file is kept (used by non-GLES2 renderers).
#
# Notes:
#   - The 'effort' arg is accepted for back-compat with the previous
#     etc2comp pipeline. It is ignored: uberetc1 always runs at full
#     Uber quality.
#   - REG-Station prefers .pkz when both sidecars exist; .pkm is kept as
#     a fallback while the PKZ rollout is in progress.
#

THEME_DIR="$1"
UBERETC1="${2:-uberetc1}"
DWEBP="${3:-dwebp}"
EFFORT="${4:-100}"  # accepted for back-compat; ignored by uberetc1

if [ -z "$THEME_DIR" ] || [ ! -d "$THEME_DIR" ]; then
    echo "Usage: $0 <theme_dir> [uberetc1_path] [dwebp_path] [effort]"
    exit 1
fi

if ! command -v "$UBERETC1" >/dev/null 2>&1; then
    echo "Error: uberetc1 not found at '$UBERETC1'"
    exit 1
fi

if ! command -v "$DWEBP" >/dev/null 2>&1; then
    echo "Warning: dwebp not found at '$DWEBP' — .webp files will be skipped"
    DWEBP=""
fi

COMPRESSED=0
SKIPPED=0
ERRORS=0

# Check if a PNG has an alpha channel via its IHDR color type byte.
# Color types with alpha: 4 (greyscale+alpha), 6 (truecolor+alpha).
# Indexed (3) may have tRNS but we conservatively skip those too.
png_has_alpha() {
    local file="$1"
    # IHDR is at offset 8 (after PNG signature), color type is at byte 25
    local ctype=$(od -An -tx1 -j25 -N1 "$file" 2>/dev/null | tr -d ' ')
    case "$ctype" in
        04|06|03) return 0 ;;  # has or may have alpha
        *)        return 1 ;;  # opaque (0=greyscale, 2=truecolor)
    esac
}

# Check if a WebP has an alpha channel via its VP8L/VP8X headers.
webp_has_alpha() {
    local file="$1"
    # VP8X chunk (extended format): alpha flag is bit 4 of byte at offset 20
    local magic=$(od -An -tx1 -j12 -N4 "$file" 2>/dev/null | tr -d ' ')
    if [ "$magic" = "56503858" ]; then  # "VP8X"
        local flags=$(od -An -tx1 -j20 -N1 "$file" 2>/dev/null | tr -d ' ')
        local alpha=$(( 0x$flags & 0x10 ))
        [ "$alpha" -ne 0 ] && return 0
        return 1
    fi
    # VP8L chunk (lossless): alpha_is_used is bit 28 of the 4-byte header at offset 21-24
    # Bit 28 falls in byte 3 (offset 24), at bit position 4
    if [ "$magic" = "5650384c" ]; then  # "VP8L"
        local b=$(od -An -tu1 -j24 -N1 "$file" 2>/dev/null | tr -d ' ')
        local alpha=$(( (b >> 4) & 1 ))
        [ "$alpha" -ne 0 ] && return 0
        return 1
    fi
    # VP8 (lossy) without VP8X: no alpha
    return 1
}

while read -r img; do
    stem="${img%.*}"
    pkm="${stem}.pkm"

    # Skip if PKM already exists and is newer than source
    if [ -f "$pkm" ] && [ "$pkm" -nt "$img" ]; then
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    ext=$(echo "${img##*.}" | tr '[:upper:]' '[:lower:]')

    # Skip PNGs with alpha channel
    if [ "$ext" = "png" ] && png_has_alpha "$img"; then
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Handle WebP: decode to temp PNG, check alpha, compress, clean up
    if [ "$ext" = "webp" ]; then
        if [ -z "$DWEBP" ]; then
            SKIPPED=$((SKIPPED + 1))
            continue
        fi
        if webp_has_alpha "$img"; then
            SKIPPED=$((SKIPPED + 1))
            continue
        fi
        tmp_png="${stem}.etc1tmp.png"
        "$DWEBP" "$img" -o "$tmp_png" -quiet 2>/dev/null
        if [ $? -ne 0 ] || [ ! -f "$tmp_png" ]; then
            ERRORS=$((ERRORS + 1))
            rm -f "$tmp_png"
            continue
        fi
        # uberetc1 emits both .pkm and .pkz next to the output stem.
        "$UBERETC1" "$tmp_png" -output "$pkm" 2>/dev/null
        if [ $? -eq 0 ] && [ -f "$pkm" ]; then
            COMPRESSED=$((COMPRESSED + 1))
        else
            ERRORS=$((ERRORS + 1))
        fi
        rm -f "$tmp_png"
        continue
    fi

    # Compress JPG/PNG to ETC1 PKM (+ PKZ alongside)
    "$UBERETC1" "$img" -output "$pkm" 2>/dev/null
    if [ $? -eq 0 ] && [ -f "$pkm" ]; then
        COMPRESSED=$((COMPRESSED + 1))
    else
        ERRORS=$((ERRORS + 1))
    fi
done < <(find "$THEME_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \))

echo "ETC1 compression: $COMPRESSED compressed (.pkm+.pkz pairs), $SKIPPED skipped, $ERRORS errors in $THEME_DIR"
