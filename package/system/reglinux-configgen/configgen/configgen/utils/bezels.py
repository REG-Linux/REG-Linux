import os
import systemFiles
import struct
from PIL import Image, ImageOps
from .videoMode import getAltDecoration

from .logger import get_logger
eslog = get_logger(__name__)

def getBezelInfos(rom, bezel, systemName, emulator):
    """
    Locate the appropriate bezel overlay image and related files based on
    ROM name, system name, and emulator used.

    The search follows a prioritized list:
    1. Game-specific user/system overlays
    2. System-specific overlays (with optional alternative decoration)
    3. Default overlays (fallback)

    Returns:
        dict or None: Dictionary containing paths to bezel files and metadata.
    """
    altDecoration = getAltDecoration(systemName, rom, emulator)
    romBase = os.path.splitext(os.path.basename(rom))[0]

    candidates = []

    # Priority: game-specific overlays
    candidates += [
        ("games", systemFiles.overlayUser, True, f"{systemName}/{romBase}"),
        ("games", systemFiles.overlaySystem, True, f"{systemName}/{romBase}"),
        ("games", systemFiles.overlayUser, True, romBase),
        ("games", systemFiles.overlaySystem, True, romBase),
    ]

    # System-specific overlays (with or without altDecoration)
    if altDecoration != 0:
        candidates.append(("systems", systemFiles.overlayUser, False, f"{systemName}-{altDecoration}"))
    candidates.append(("systems", systemFiles.overlayUser, False, systemName))
    if altDecoration != 0:
        candidates.append(("systems", systemFiles.overlaySystem, False, f"{systemName}-{altDecoration}"))
    candidates.append(("systems", systemFiles.overlaySystem, False, systemName))

    # Default fallback overlays
    if altDecoration != 0:
        candidates.append(("", systemFiles.overlayUser, True, f"default-{altDecoration}"))
    candidates.append(("", systemFiles.overlayUser, True, "default"))
    if altDecoration != 0:
        candidates.append(("", systemFiles.overlaySystem, True, f"default-{altDecoration}"))
    candidates.append(("", systemFiles.overlaySystem, True, "default"))

    for subfolder, basepath, bezel_game, name in candidates:
        prefix = f"{basepath}/{bezel}/{subfolder}/" if subfolder else f"{basepath}/{bezel}/"
        overlay_png_file = f"{prefix}{name}.png"
        if os.path.exists(overlay_png_file):
            eslog.debug(f"Original bezel file used: {overlay_png_file}")
            return {
                "png": overlay_png_file,
                "info": f"{prefix}{name}.info",
                "layout": f"{prefix}{name}.lay",
                "mamezip": f"{prefix}{name}.zip",
                "specific_to_game": bezel_game
            }

    return None

def fast_image_size(image_file):
    """
    Return the size (width, height) of a PNG image by reading its header.
    Much faster than using PIL.Image.open().size.

    Returns:
        (int, int): Width and height of the image, or (-1, -1) if error.
    """
    if not os.path.exists(image_file):
        return -1, -1
    with open(image_file, 'rb') as fhandle:
        head = fhandle.read(32)
        if len(head) != 32 or struct.unpack('>i', head[4:8])[0] != 0x0d0a1a0a:
            return -1, -1
        return struct.unpack('>ii', head[16:24])

def resize_with_fill(img, target_size, stretch=False, fillcolor="black"):
    """
    Resize an image with padding or stretching.

    Args:
        img (Image): Source image.
        target_size (tuple): Desired size.
        stretch (bool): Stretch instead of pad.
        fillcolor (str): Background color.

    Returns:
        Image: The resized image.
    """
    return ImageOps.fit(img, target_size) if stretch else ImageOps.pad(img, target_size, color=fillcolor, centering=(0.5, 0.5))

def resizeImage(input_png, output_png, screen_width, screen_height, bezel_stretch=False):
    """
    Resize a bezel image to match screen size, maintaining alpha if needed.
    """
    imgin = Image.open(input_png)
    fillcolor = 'black'
    eslog.debug(f"Resizing bezel: image mode {imgin.mode}")
    if imgin.mode != "RGBA":
        alphaPaste(input_png, output_png, imgin, fillcolor, (screen_width, screen_height), bezel_stretch)
    else:
        imgout = resize_with_fill(imgin, (screen_width, screen_height), stretch=bezel_stretch, fillcolor=fillcolor)
        imgout.save(output_png, mode="RGBA", format="PNG")

def padImage(input_png, output_png, screen_width, screen_height, bezel_width, bezel_height, bezel_stretch=False):
    """
    Pad the bezel image to match screen size.
    """
    imgin = Image.open(input_png)
    fillcolor = 'black'
    eslog.debug(f"Padding bezel: image mode {imgin.mode}")
    if imgin.mode != "RGBA":
        alphaPaste(input_png, output_png, imgin, fillcolor, (screen_width, screen_height), bezel_stretch)
    else:
        imgout = resize_with_fill(imgin, (screen_width, screen_height), stretch=bezel_stretch, fillcolor=fillcolor)
        imgout.save(output_png, mode="RGBA", format="PNG")

def tatooImage(input_png, output_png, system):
    """
    Overlay a controller image ("tattoo") on top of the bezel, depending on system config.
    """
    tattoo_file = None
    tattoo = None
    try:
        if system.config['bezel.tattoo'] == 'system':
            tattoo_file = f'/usr/share/reglinux/controller-overlays/{system.name}.png'
            if not os.path.exists(tattoo_file):
                tattoo_file = '/usr/share/reglinux/controller-overlays/generic.png'
            tattoo = Image.open(tattoo_file)
        elif system.config['bezel.tattoo'] == 'custom' and os.path.exists(system.config['bezel.tattoo_file']):
            tattoo_file = system.config['bezel.tattoo_file']
            tattoo = Image.open(tattoo_file)
        else:
            tattoo_file = '/usr/share/reglinux/controller-overlays/generic.png'
            tattoo = Image.open(tattoo_file)
    except:
        eslog.error(f"Error opening tattoo image: {tattoo_file}")
        return

    back = Image.open(input_png).convert("RGBA")
    tattoo = tattoo.convert("RGBA") if tattoo else None

    if not tattoo:
        eslog.error("Tattoo image could not be loaded, skipping tattoo overlay.")
        return

    w, h = fast_image_size(input_png)
    tw, th = fast_image_size(tattoo_file)

    if system.config.get('bezel.resize_tattoo') == 0:
        if tw > w or th > h:
            pcent = float(w / tw)
            th = int(th * pcent)
            tattoo = tattoo.resize((w, th), Image.Resampling.BICUBIC)
    else:
        twtemp = int((225 / 1920) * w)
        pcent = float(twtemp / tw)
        th = int(th * pcent)
        tattoo = tattoo.resize((twtemp, th), Image.Resampling.BICUBIC)
        tw = twtemp

    margin = int((20 / 1080) * h)
    corner = system.config.get('bezel.tattoo_corner', 'NW').upper()

    tattooCanvas = Image.new("RGBA", back.size)
    if corner == 'NE':
        tattooCanvas.paste(tattoo, (w - tw, margin))
    elif corner == 'SE':
        tattooCanvas.paste(tattoo, (w - tw, h - th - margin))
    elif corner == 'SW':
        tattooCanvas.paste(tattoo, (0, h - th - margin))
    else:
        tattooCanvas.paste(tattoo, (0, margin))

    back = Image.alpha_composite(back, tattooCanvas)
    imgnew = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    imgnew.paste(back, (0, 0, w, h))
    imgnew.save(output_png, mode="RGBA", format="PNG")

def alphaPaste(input_png, output_png, imgin, fillcolor, screensize, bezel_stretch):
    """
    Paste the alpha channel from an image into a resized canvas.
    Handles non-RGBA images and crops to match aspect ratio.
    """
    imgin = Image.open(input_png)
    if 'transparency' not in imgin.info:
        raise Exception("no transparent pixels in the image, abort")

    alpha = imgin.split()[-1]
    ix, iy = fast_image_size(input_png)
    sx, sy = screensize
    i_ratio = float(ix) / float(iy)
    s_ratio = float(sx) / float(sy)

    if i_ratio - s_ratio > 0.01:
        new_x = int(ix * s_ratio / i_ratio)
        delta = int(ix - new_x)
        alpha = alpha.crop((delta // 2, 0, new_x + delta // 2, iy))
        ix = new_x

    imgnew = Image.new("RGBA", (ix, iy), (0, 0, 0, 255))
    imgnew.paste(alpha, (0, 0, ix, iy))
    imgout = resize_with_fill(imgnew, screensize, stretch=bezel_stretch, fillcolor=fillcolor)
    imgout.save(output_png, mode="RGBA", format="PNG")

def gunBordersSize(bordersSize):
    """
    Return preset values for gun border sizes depending on text config.
    """
    if bordersSize == "thin":
        return 1, 0
    if bordersSize == "medium":
        return 2, 0
    if bordersSize == "big":
        return 2, 1
    return 0, 0

def gunBorderImage(input_png, output_png, innerBorderSizePer=2, outerBorderSizePer=3, innerBorderColor="#ffffff", outerBorderColor="#000000"):
    """
    Draws outer and inner borders on the bezel image for lightgun detection.
    """
    from PIL import ImageDraw
    w, h = fast_image_size(input_png)
    outerBorderSize = max(1, h * outerBorderSizePer // 100)
    outerShapes = [ [(0, 0), (w, outerBorderSize)], [(w-outerBorderSize, 0), (w, h)],
                    [(0, h-outerBorderSize), (w, h)], [(0, 0), (outerBorderSize, h)] ]

    innerBorderSize = max(1, w * innerBorderSizePer // 100)
    innerShapes = [ [(outerBorderSize, outerBorderSize), (w-outerBorderSize, outerBorderSize+innerBorderSize)],
                    [(w-outerBorderSize-innerBorderSize, outerBorderSize), (w-outerBorderSize, h-outerBorderSize)],
                    [(outerBorderSize, h-outerBorderSize-innerBorderSize), (w-outerBorderSize, h-outerBorderSize)],
                    [(outerBorderSize, outerBorderSize), (outerBorderSize+innerBorderSize, h-outerBorderSize)] ]

    back = Image.open(input_png)
    imgnew = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    imgnew.paste(back, (0, 0, w, h))
    draw = ImageDraw.Draw(imgnew)

    for shape in outerShapes:
        draw.rectangle(shape, fill=outerBorderColor)
    for shape in innerShapes:
        draw.rectangle(shape, fill=innerBorderColor)

    imgnew.save(output_png, mode="RGBA", format="PNG")
    return outerBorderSize + innerBorderSize

def gunsBorderSize(w, h, innerBorderSizePer=2, outerBorderSizePer=3):
    """
    Calculate combined border height used for lightgun overlay.
    """
    return (h * (innerBorderSizePer + outerBorderSizePer)) // 100

def gunsBordersColorFomConfig(config):
    """
    Return hex color for gun borders from config string.
    """
    return {
        "red": "#ff0000",
        "green": "#00ff00",
        "blue": "#0000ff",
        "white": "#ffffff"
    }.get(config.get("controllers.guns.borderscolor"), "#ffffff")

def createTransparentBezel(output_png, width, height):
    """
    Create a fully transparent bezel PNG of given size.
    """
    from PIL import ImageDraw
    imgnew = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    imgnewdraw = ImageDraw.Draw(imgnew)
    imgnew.save(output_png, mode="RGBA", format="PNG")
