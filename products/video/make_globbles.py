"""Motion-graphic Short (9:16) for Crayola Globbles, built from real product photos (post8 squishy guide).
Renders PNG frames with Pillow, then encodes with ffmpeg. No AI generation. No prices (owner rule).
Usage: python3 products/video/make_globbles.py            # frames + mp4 + cover
       python3 products/video/make_globbles.py --preview  # only a few check frames + cover"""
import math, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SLUG = 'globbles'
OUT = os.path.expanduser('~/Downloads/toyscout-video')  # frames + mp4 go here, outside the repo
SITE = '/Users/ahmet/Downloads/Toyscout/assets'
W, H, FPS = 1080, 1920, 30
DUR = 12.5
FR = os.path.join(OUT, f'frames_{SLUG}'); os.makedirs(FR, exist_ok=True)

CREAM = (255, 246, 232); NAVY = (27, 42, 74); RED = (232, 64, 42); BLUE = (40, 120, 220)
PINK = (236, 72, 153); GREEN = (46, 160, 90); PURPLE = (124, 58, 237); WHITE = (255, 255, 255)
F_ROUND = '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf'
F_UNI = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
def font(sz, f=F_ROUND): return ImageFont.truetype(f, sz)

# ---------- assets (real Amazon listing photos from assets/products) ----------
def P(name): return Image.open(f'{SITE}/products/{name}.jpg').convert('RGB')

def cutout_white(im, thr=238):
    im = im.convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r > thr and g > thr and b > thr: px[x, y] = (r, g, b, 0)
    return im

def ball(src, cx, cy, r, drop=None):
    """Cut one ball out of a white-background photo: circle mask AND non-white pixels, soft edge."""
    c = src.crop((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6))
    m = Image.new('L', c.size, 0); ImageDraw.Draw(m).ellipse((6, 6, 6 + 2 * r, 6 + 2 * r), fill=255)
    nw = c.convert('L').point(lambda v: 0 if v > 240 else 255)
    if drop:  # remove pixels of a neighbouring ball (by colour)
        px = c.load(); q = nw.load()
        for yy in range(c.height):
            for xx in range(c.width):
                if drop(*px[xx, yy]): q[xx, yy] = 0
    from PIL import ImageChops
    m = ImageChops.multiply(m, nw).filter(ImageFilter.GaussianBlur(1.5))
    o = c.convert('RGBA'); o.putalpha(m); return o

g1 = P('B07HDX46HS_1')
BALLS = [ball(g1, 352, 1255, 158),   # pink
         ball(g1, 1160, 672, 150),   # orange
         ball(g1, 792, 1200, 148, lambda r, g, b: r > 170),   # green (drop yellow)
         ball(g1, 968, 912, 146, lambda r, g, b: g < 110),    # blue (drop purple)
         ball(g1, 1260, 966, 152, lambda r, g, b: g > 120)]   # purple (drop blue)

def rounded(im, r=48):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *im.size), r, fill=255)
    o = im.convert('RGBA'); o.putalpha(m); return o

def card(im, w, r=44, border=10):
    im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    base = Image.new('RGBA', (im.width + 2 * border, im.height + 2 * border), (0, 0, 0, 0))
    ImageDraw.Draw(base).rounded_rectangle((0, 0, *base.size), r + border, fill=WHITE + (255,))
    base.paste(rounded(im, r), (border, border), rounded(im, r)); return base

pack = card(P('B07HDX46HS'), 660)
wall = card(P('B07HDX46HS_5'), 460)
squish = card(P('B07HDX46HS_2'), 460)
gum = cutout_white(P('B0C6XBP4CW').crop((640, 10, 1270, 720)))       # NeeDoh Gumdrop (blue)
gum = gum.resize((360, int(gum.height * 360 / gum.width)), Image.LANCZOS)
mochi = card(P('B0HDBBT31F'), 400, r=36, border=8)
logo = cutout_white(Image.open(f'{SITE}/logo-blocks.png'), 245)
logo = logo.crop(logo.getbbox()); logo = logo.resize((200, int(logo.height * 200 / logo.width)), Image.LANCZOS)

# ---------- easing ----------
def clamp(x): return max(0.0, min(1.0, x))
def ease_out(t): return 1 - (1 - t) ** 3
def ease_in(t): return t ** 2
def ease_back(t, s=1.7):
    t -= 1; return t * t * ((s + 1) * t + s) + 1
def prog(t, a, b): return clamp((t - a) / (b - a))

# ---------- drawing helpers ----------
def bg(t):
    im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im)
    for i, (c, r, sp) in enumerate([((255, 214, 224), 520, 0.35), ((214, 232, 255), 600, 0.25), ((255, 236, 190), 420, 0.45)]):
        cx = W * (0.2 + 0.6 * i / 2) + 120 * math.sin(t * sp + i)
        cy = H * (0.25 + 0.3 * i) + 140 * math.cos(t * sp * 1.3 + i)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(90))

def text_c(d, y, s, f, fill, stroke=0, sf=None, cx=W / 2):
    w = d.textlength(s, font=f); d.text((cx - w / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sf)

def paste_c(canvas, im, cx, cy, scale=1.0, sx=1.0, sy=1.0, alpha=1.0, rot=0):
    w = max(1, int(im.width * scale * sx)); h = max(1, int(im.height * scale * sy))
    p = im.resize((w, h), Image.LANCZOS)
    if rot: p = p.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = p.split()[3].point(lambda v: int(v * alpha)); p.putalpha(a)
    canvas.paste(p, (int(cx - p.width / 2), int(cy - p.height / 2)), p)

def pill(canvas, cx, cy, s, f, fg, bgc, alpha=1.0, pad=(44, 22)):
    d0 = ImageDraw.Draw(canvas); tw = d0.textlength(s, font=f); th = f.size
    layer = Image.new('RGBA', (int(tw + pad[0] * 2), int(th + pad[1] * 2)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer); ld.rounded_rectangle((0, 0, *layer.size), layer.height // 2, fill=bgc + (int(255 * alpha),))
    ld.text((pad[0], pad[1] - th * 0.12), s, font=f, fill=fg + (int(255 * alpha),))
    canvas.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)

def shadow(canvas, cx, cy, w, alpha=0.25):
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((cx - w / 2, cy - 30, cx + w / 2, cy + 30), fill=(0, 0, 0, int(255 * alpha)))
    sh = sh.filter(ImageFilter.GaussianBlur(22)); canvas.paste(sh, (0, 0), sh)

def scene_alpha(t, a, b, fade=0.25):
    return clamp((t - a) / fade) * clamp((b - t) / fade)

# hook: balls fly up from below and stick to the "ceiling" band
CEIL = 640                                 # y of the ceiling line
HOOK_BALLS = [  # (ball idx, x, launch time, size)
    (0, 230, -0.6, 0.72), (4, 540, 0.2, 0.72), (1, 850, 0.9, 0.72)]   # only the 3 balls that cut out cleanly

def ceiling(im, A):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, CEIL - 120, W - 60, CEIL), 30, fill=(250, 230, 205, int(255 * A)))
    for x in range(110, W - 60, 120):                 # little ceiling-tile seams
        d.line((x, CEIL - 110, x, CEIL - 10), fill=(232, 206, 176, int(255 * A)), width=4)

def hook(im, t, A, static=False):
    d = ImageDraw.Draw(im)
    y = 270 + (0 if static else 5 * math.sin(t * 3))
    text_c(d, y, 'WHY KIDS THROW', font(100), NAVY + (int(255 * A),))
    text_c(d, y + 120, 'THESE AT THE CEILING', font(84), RED + (int(255 * A),))
    ceiling(im, A)
    for k, (bi, x, t0, sc) in enumerate(HOOK_BALLS):
        b = BALLS[bi]; r = b.height * sc / 2
        if static: tt = 9.0
        else: tt = t - t0
        if tt < 0: continue
        fly = 0.55
        if tt < fly:                                    # flying up from below the frame
            p = ease_out(tt / fly)
            cy = 1900 - (1900 - (CEIL + r * 0.92)) * p
            paste_c(im, b, x, cy, sc, 0.9, 1.1, A, rot=int(tt * 400) % 360)
        else:                                           # stuck: splat squash, then a slow wobble
            st = tt - fly
            sq = 0.28 * math.exp(-st * 5) * math.cos(st * 18)
            sy = 1 - 0.18 - sq; sx = 1 + 0.12 + sq * 0.6
            cy = CEIL + r * sy * 0.92
            paste_c(im, b, x, cy, sc, sx, sy, A)

def frame(t):
    im = bg(t).convert('RGBA'); d = ImageDraw.Draw(im)

    # S1 hook 0–2.6
    if t < 2.65:
        A = scene_alpha(t, -1, 2.65)
        hook(im, t, A)
        a2 = ease_back(prog(t, 1.6, 2.0))
        if a2 > 0:
            pill(im, W / 2, 1300, 'Crayola Globbles', font(76), WHITE, PURPLE, A * clamp(a2))
        d1 = ImageDraw.Draw(im)
        text_c(d1, 1420, 'Stick. Stack. Squish. Sling.', font(52), (90, 90, 90, int(255 * A * clamp(a2))))

    # S2 #1 pick 2.5–5.0: pack photo + rating count-up
    if 2.45 < t < 5.05:
        A = scene_alpha(t, 2.45, 5.05)
        pill(im, W / 2, 320, '#1 STICKY PICK', font(60), WHITE, RED, A)
        text_c(d, 410, 'Crayola Globbles', font(100), NAVY + (int(255 * A),))
        text_c(d, 535, '6-pack sticky squish balls', font(54), (90, 90, 90, int(255 * A)))
        z = 0.94 + 0.06 * ease_out(prog(t, 2.5, 5.0))
        paste_c(im, pack, W / 2, 975, z, alpha=A, rot=-2)
        n = int(21037 * ease_out(prog(t, 2.8, 4.1)))
        d2 = ImageDraw.Draw(im)
        text_c(d2, 1345, f'4.5 ★  ·  {n:,} ratings', font(70, F_UNI), (40, 40, 40, int(255 * A)))
        sub = ease_out(prog(t, 3.9, 4.3))
        text_c(d2, 1440, 'Most-reviewed squishy we track', font(54), (90, 90, 90, int(255 * A * sub)))

    # S3 feature 4.9–7.4: real listing photos slide in
    if 4.85 < t < 7.45:
        A = scene_alpha(t, 4.85, 7.45)
        pl = ease_out(prog(t, 4.9, 5.5)); pr = ease_out(prog(t, 5.8, 6.4))
        paste_c(im, wall, -300 + pl * 600, 735, 1.0, alpha=A, rot=-4)
        paste_c(im, squish, W + 300 - pr * 600, 1065, 1.0, alpha=A, rot=4)
        d3 = ImageDraw.Draw(im)
        a1 = ease_out(prog(t, 5.1, 5.5)); a2 = ease_out(prog(t, 6.0, 6.4))
        text_c(d3, 290, 'Sticks to walls', font(80), NAVY + (int(255 * A * a1),))
        text_c(d3, 385, 'and windows.', font(80), BLUE + (int(255 * A * a1),))
        text_c(d3, 1345, 'Squish it, stretch it,', font(76), NAVY + (int(255 * A * a2),))
        text_c(d3, 1430, 'stack it.', font(76), PINK + (int(255 * A * a2),))

    # S4 other picks 7.3–9.4
    if 7.25 < t < 9.45:
        A = scene_alpha(t, 7.25, 9.45)
        text_c(d, 300, 'Also in our', font(80), NAVY + (int(255 * A),))
        text_c(d, 395, 'squishy guide', font(80), RED + (int(255 * A),))
        p1 = ease_back(prog(t, 7.4, 7.9)); p2 = ease_back(prog(t, 7.8, 8.3))
        d4 = ImageDraw.Draw(im)
        if p1 > 0:
            a = A * clamp(p1)
            shadow(im, 290, 1000, 300, 0.18 * a)
            paste_c(im, gum, 290, 800, 0.85 * max(p1, 0.01), alpha=a)
            d4 = ImageDraw.Draw(im)
            text_c(d4, 1060, 'NeeDoh', font(62), NAVY + (int(255 * a),), cx=290)
            text_c(d4, 1135, 'Gumdrop', font(62), NAVY + (int(255 * a),), cx=290)
            text_c(d4, 1225, '4.4 ★ · 4,453', font(50, F_UNI), (60, 60, 60, int(255 * a)), cx=290)
        if p2 > 0:
            a = A * clamp(p2)
            paste_c(im, mochi, 790, 800, 0.95 * max(p2, 0.01), alpha=a, rot=3)
            d4 = ImageDraw.Draw(im)
            text_c(d4, 1060, 'JOYIN Mini', font(62), NAVY + (int(255 * a),), cx=790)
            text_c(d4, 1135, 'Mochi 200-pack', font(56), NAVY + (int(255 * a),), cx=790)
            text_c(d4, 1225, '4.7 ★ · 3,008', font(50, F_UNI), (60, 60, 60, int(255 * a)), cx=790)
        a3 = ease_out(prog(t, 8.4, 8.8))
        text_c(d4, 1370, 'Dough, mochi or sticky?', font(58), (90, 90, 90, int(255 * A * a3)))

    # S5 checklist 9.3–11.0
    if 9.25 < t < 11.05:
        A = scene_alpha(t, 9.25, 11.05)
        text_c(d, 400, 'Why parents like them', font(84), NAVY + (int(255 * A),))
        for i, s in enumerate(['✓  No sticky residue', '✓  Washes with soap & water', '✓  Ages 3 and up']):
            p = ease_back(prog(t, 9.45 + i * 0.3, 9.85 + i * 0.3))
            if p > 0: pill(im, W / 2 + (1 - p) * 300, 720 + i * 220, s, font(58, F_UNI), WHITE, [GREEN, BLUE, PURPLE][i], A * clamp(p))
        for k, (bi, x) in enumerate([(1, 250), (0, 540), (4, 830)]):
            bp = ease_back(prog(t, 10.3 + k * 0.1, 10.6 + k * 0.1))
            if bp > 0: paste_c(im, BALLS[bi], x, 1380, 0.55 * bp + 0.001, alpha=A)

    # S6 CTA 10.9–12.5
    if t > 10.9:
        A = clamp((t - 10.9) / 0.25)
        text_c(d, 360, 'Best squishy toys 2026', font(80), NAVY + (int(255 * A),))
        text_c(d, 470, 'NeeDoh · mochi · Globbles', font(62, F_UNI), (90, 90, 90, int(255 * A)))
        b = 1 + 0.04 * math.sin((t - 10.9) * 6)
        pill(im, W / 2, 760, 'Full guide on toyscout.net', font(70), WHITE, RED, A, pad=(56 * b, 30 * b))
        paste_c(im, logo, W / 2, 1040, ease_back(prog(t, 11.1, 11.6)) + 0.001, alpha=A)
        d5 = ImageDraw.Draw(im)
        text_c(d5, 1260, 'toyscout.net', font(76), NAVY + (int(255 * A),))
    return im.convert('RGB')

def cover():
    im = bg(1.0).convert('RGBA'); d = ImageDraw.Draw(im)
    # title inside central 3:4 area (y ~420–1500)
    text_c(d, 450, 'WHY KIDS THROW', font(104), NAVY)
    text_c(d, 575, 'THESE AT', font(104), RED)
    text_c(d, 700, 'THE CEILING', font(104), RED)
    global CEIL
    old = CEIL; CEIL = 980
    ceiling(im, 1.0)
    for bi, x, sc in [(0, 250, 0.72), (4, 540, 0.72), (1, 830, 0.72)]:
        b = BALLS[bi]; r = b.height * sc / 2
        paste_c(im, b, x, CEIL + r * 0.82 * 0.92, sc, 1.12, 0.82)
    CEIL = old
    pill(im, W / 2, 1330, 'Crayola Globbles', font(80), WHITE, PURPLE)
    d = ImageDraw.Draw(im)
    text_c(d, 1430, 'toyscout.net', font(56), NAVY)
    p = os.path.join(OUT, f'cover_{SLUG}.jpg'); im.convert('RGB').save(p, quality=92); print('wrote', p)

if __name__ == '__main__':
    cover()
    if '--preview' in sys.argv:
        for tt in [0.0, 1.0, 2.2, 4.4, 6.8, 8.9, 10.6, 12.2]:
            frame(tt).save(os.path.join(FR, f'check_{tt:04.1f}.png'))
        print('preview frames in', FR); sys.exit()
    n = int(DUR * FPS)
    for i in range(n):
        frame(i / FPS).save(os.path.join(FR, f'f{i:04d}.png'))
        if i % 60 == 0: print('frame', i, '/', n, flush=True)
    mp4 = os.path.join(OUT, f'toyscout_{SLUG}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(FR, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', mp4], check=True)
    shutil.rmtree(FR)
    print('wrote', mp4)
