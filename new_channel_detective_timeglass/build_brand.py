#!/usr/bin/env python3
"""Render the Ben's Casebook draft kit. No YouTube account is touched.

The mascot and photorealistic backdrop are generated source images, so the
7680x4320 export is an upscaled artwork canvas, not native-detail 8K footage.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
ASSET = ROOT / 'assets'
FONT_HEAD = ASSET / 'fonts/Anton-Regular.ttf'
FONT_BODY = ASSET / 'fonts/DMSans.ttf'
IVORY = (247, 244, 225)
LIME = (211, 242, 103)


def circular_preview(im: Image.Image, size=98):
    preview = im.resize((size, size), Image.Resampling.LANCZOS).convert('RGBA')
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size-1, size-1), fill=255)
    preview.putalpha(mask)
    preview.save(ROOT / 'preview_profile_circle_98.png')


def make_profile():
    source = Image.open(ASSET / 'male_detective_portrait_v2.png').convert('RGB')
    # Keep the male detective's hat, face AND left-hand lens in circular crop.
    portrait = source.crop((70, 40, 960, 930))
    portrait.resize((800, 800), Image.Resampling.LANCZOS).save(ROOT / 'profile_upload_800.png', optimize=True)
    portrait.resize((2048, 2048), Image.Resampling.LANCZOS).save(ROOT / 'profile_2048_upscaled.png', optimize=True)
    circular_preview(portrait)


def mascot_cutout():
    """Key out the near-uniform ivory field; keep the hand, hat, lens and outline."""
    source = Image.open(ASSET / 'male_detective_portrait_v2.png').convert('RGB')
    pixels = np.asarray(source).astype('float32')
    # The generated white field varies +/- 2. Foreground has much larger
    # color distance; a soft ramp preserves antialiased contours.
    background = np.array([245, 246, 237], dtype='float32')
    dist = np.max(np.abs(pixels - background), axis=2)
    alpha = np.uint8(np.clip((dist-9) * (255/35), 0, 255))
    rgba = source.convert('RGBA')
    rgba.putalpha(Image.fromarray(alpha, 'L'))
    rgba.save(ASSET / 'male_detective_cutout_v2.png', optimize=True)
    return rgba


def composite_banner(scale=1):
    w, h = 2560*scale, 1440*scale
    background = Image.open(ASSET / 'realistic_case_room_background.png').convert('RGB')
    im = ImageOps.fit(background, (w, h), method=Image.Resampling.LANCZOS).convert('RGBA')
    character = mascot_cutout().resize((520*scale, 520*scale), Image.Resampling.LANCZOS)
    xy = (520*scale, 502*scale)  # Keep the whole fedora in the mobile-safe crop.
    # A small soft shadow seats the drawn subject in the photographic scene.
    shadow = Image.new('RGBA', im.size, (0,0,0,0))
    dark_shape = Image.new('RGBA', character.size, (0,0,0,0))
    dark_shape.putalpha(character.getchannel('A').point(lambda a: int(a*.45)))
    shadow.alpha_composite(dark_shape, (xy[0]+9*scale, xy[1]+13*scale))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16*scale))
    black = Image.new('RGBA', im.size, (0,0,0,150))
    black.putalpha(shadow.getchannel('A'))
    im = Image.alpha_composite(im, black)
    im.alpha_composite(character, xy)
    # Restrained type stays inside centered [510,2050]x[510,930].
    # No decorative title panel: this is one continuous investigation scene.
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(str(FONT_HEAD), 138*scale)
    sub = ImageFont.truetype(str(FONT_BODY), 37*scale)
    eyebrow = ImageFont.truetype(str(FONT_BODY), 25*scale)
    x = 1056*scale
    def title(word, y, color):
        bbox = d.textbbox((0, 0), word, font=f, stroke_width=0)
        assert x + (bbox[2]-bbox[0]) <= 2042*scale, (word, bbox)
        d.text((x+4*scale, y+5*scale), word, font=f, fill=(2,14,18,230))
        d.text((x, y), word, font=f, fill=(*color,255))
    title("BEN'S", 555*scale, IVORY)
    title('CASEBOOK', 695*scale, LIME)
    d.line((x, 858*scale, 1340*scale, 858*scale), fill=(*LIME,245), width=4*scale)
    d.text((x, 869*scale), "LET'S FOLLOW THE CLUES.",
           font=sub, fill=(*IVORY,255), stroke_width=1*scale,
           stroke_fill=(3,16,20,180))
    # Gently framed original scene, not ornamental logo or fake evidence label.
    return im.convert('RGB')


def make_banner():
    im = composite_banner()
    output = ROOT / 'banner_upload_2560x1440.jpg'
    im.save(output, quality=94, optimize=True, progressive=True, subsampling=0)
    assert output.stat().st_size <= 6*1024*1024, output.stat().st_size
    # 8K export: source imagery is upscaled; type and compositing are re-rendered.
    eight = composite_banner(3)
    eight.save(ROOT / 'banner_8k_7680x4320_upscaled_artwork.jpg',
               quality=88, optimize=True, progressive=True, subsampling=0)
    im.crop((510,510,2050,930)).save(ROOT/'preview_mobile_safe.jpg',quality=94)
    im.crop((0,510,2560,930)).save(ROOT/'preview_desktop.jpg',quality=92)
    im.resize((1280,720),Image.Resampling.LANCZOS).save(ROOT/'preview_tv.jpg',quality=92)
    for path in [output, ROOT/'banner_8k_7680x4320_upscaled_artwork.jpg']:
        print(path.name, path.stat().st_size)

if __name__ == '__main__':
    make_profile()
    make_banner()
