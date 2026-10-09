"""Motion-graphic Short (9:16, ~18.6 s) for post14 (which Play-Doh pack should you buy, every size compared),
built from real product photos. Renders PNG frames with Pillow, then encodes with ffmpeg. No AI generation.
Structure and style copied from make_advent.py. Packs compared by count / can size / use, ratings from js/data.js.
No prices anywhere (owner rule)."""
import math, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SLUG = 'playdoh'
OUT = os.path.expanduser('~/Downloads/toyscout-video')  # frames + mp4 go here, outside the repo
SITE = '/Users/ahmet/Downloads/Toyscout/assets'
W, H, FPS = 1080, 1920, 30
DUR = 18.6
WARP = 1.0
FR = os.path.join(OUT, f'frames_{SLUG}'); os.makedirs(FR, exist_ok=True)

CREAM = (255, 246, 232); NAVY = (27, 42, 74); RED = (232, 64, 42); BLUE = (40, 120, 220)
PINK = (236, 72, 153); GREEN = (46, 160, 90); GOLD = (214, 150, 20); WHITE = (255, 255, 255)
F_ROUND = '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf'
F_UNI = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
def font(sz, f=F_ROUND): return ImageFont.truetype(f, sz)

# ---------- assets ----------
def cutout_white(im, thr=238):
    im = im.convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r > thr and g > thr and b > thr: px[x, y] = (r, g, b, 0)
    return im

def rounded(im, r=48):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *im.size), r, fill=255)
    o = im.convert('RGBA'); o.putalpha(m); return o

def card(path, size, crop=None, pad=0.06, r=44):
    """Product photo on a white rounded card (photos have white backgrounds, so this reads clean)."""
    im = Image.open(path).convert('RGB')
    if crop: im = im.crop(crop)
    inner = int(size * (1 - 2 * pad)); im.thumbnail((inner, inner), Image.LANCZOS)
    c = Image.new('RGB', (size, size), WHITE); c.paste(im, ((size - im.width) // 2, (size - im.height) // 2))
    return rounded(c, r)

P = f'{SITE}/products'
TWELVE = card(f'{P}/B07BC44JFC.jpg', 760)                     # Play-Doh 12-pack of 4-oz cans (#1 for one child)
TWELVE_TOP = card(f'{P}/B07BC44JFC_1.jpg', 760, pad=0.03)     # real top-down photo of the 12 open cans
TEN = card(f'{P}/B00JM5GW10.jpg', 330)                         # classic 10-pack of 2-oz cans
T36 = card(f'{P}/B00JM5GZGW.jpg', 330)                         # 36-pack of 3-oz cans
T42 = card(f'{P}/B087N9N6HH.jpg', 330)                         # 42-pack of 1-oz cans
C65 = card(f'{P}/B09NRS8C5Y_2.jpg', 760, pad=0.03)             # 65-pack with its colour chart
HOOK = [card(f'{P}/B00JM5GW10.jpg', 420), card(f'{P}/B09NRS8C5Y.jpg', 420), card(f'{P}/B07BC44JFC.jpg', 420)]
logo = cutout_white(Image.open(f'{SITE}/logo-blocks.png'), 245)
logo = logo.crop(logo.getbbox()); logo = logo.resize((200, int(logo.height * 200 / logo.width)), Image.LANCZOS)

# ---------- easing ----------
def clamp(x): return max(0.0, min(1.0, x))
def ease_out(t): return 1 - (1 - t) ** 3
def ease_back(t, s=1.7):
    t -= 1; return t * t * ((s + 1) * t + s) + 1
def prog(t, a, b): return clamp((t - a) / (b - a))

# ---------- drawing helpers ----------
def bg(t):
    im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im)
    for i, (c, r, sp) in enumerate([((255, 214, 214), 520, 0.35), ((214, 236, 222), 600, 0.25), ((255, 236, 190), 420, 0.45)]):
        cx = W * (0.2 + 0.6 * i / 2) + 120 * math.sin(t * sp + i)
        cy = H * (0.25 + 0.3 * i) + 140 * math.cos(t * sp * 1.3 + i)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(90))

def text_c(d, y, s, f, fill, cx=W / 2):
    w = d.textlength(s, font=f); d.text((cx - w / 2, y), s, font=f, fill=fill)

def paste_c(canvas, im, cx, cy, scale=1.0, alpha=1.0, rot=0):
    w = max(1, int(im.width * scale)); h = max(1, int(im.height * scale))
    p = im.resize((w, h), Image.LANCZOS)
    if rot: p = p.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = p.split()[3].point(lambda v: int(v * alpha)); p.putalpha(a)
    canvas.paste(p, (int(cx - p.width / 2), int(cy - p.height / 2)), p)

def pill(canvas, cx, cy, s, f, fg, bgc, alpha=1.0, pad=(44, 22), left=False):
    d0 = ImageDraw.Draw(canvas); tw = d0.textlength(s, font=f); th = f.size
    layer = Image.new('RGBA', (int(tw + pad[0] * 2), int(th + pad[1] * 2)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer); ld.rounded_rectangle((0, 0, *layer.size), layer.height // 2, fill=bgc + (int(255 * alpha),))
    ld.text((pad[0], pad[1] - th * 0.12), s, font=f, fill=fg + (int(255 * alpha),))
    x = cx if left else cx - layer.width / 2
    canvas.paste(layer, (int(x), int(cy - layer.height / 2)), layer)

def soft_shadow(canvas, box, alpha=0.22, r=44):
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(box, r, fill=(60, 40, 20, int(255 * alpha)))
    sh = sh.filter(ImageFilter.GaussianBlur(24)); canvas.paste(sh, (0, 14), sh)

FADE = 0.2
def scene_alpha(t, a, b, fade=FADE):
    # old scene fades out over [b-fade, b], next fades in over [b, b+fade]: never two at full strength
    return clamp((t - a) / fade) * clamp((b - t) / fade)

# scene boundaries (seconds)
T_HOOK, T_PICK, T_CANS, T_SIZES, T_COLORS, T_CHECK, T_CTA = 0.0, 3.0, 6.4, 8.6, 12.4, 14.4, 15.9

# ---------- scenes ----------
ROWS = [  # (card, use pill, colour, name, what, rating line) — real catalog numbers
    (TEN, 'FIRST PACK', BLUE, 'Classic 10-pack', '10 cans × 2 oz', '4.7 ★ · 69,322 ratings'),
    (T36, 'CLASSROOMS', GREEN, '36-pack', '36 cans × 3 oz', '4.8 ★ · 28,814 ratings'),
    (T42, 'PARTY BAGS', PINK, '42-pack', '42 mini cans × 1 oz', '4.9 ★ · 17,567 ratings'),
]

def frame(t):
    im = bg(t).convert('RGBA')
    # faded text goes on its own RGBA layer (Pillow ignores alpha in text fill on an RGBA canvas)
    tl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(tl)

    # S1 hook: title + cards visible from frame 0
    if t < T_PICK:
        A = scene_alpha(t, -1, T_PICK)
        y = 300 + 6 * math.sin(t * 3)
        text_c(d, y, 'WHICH PLAY-DOH', font(94), NAVY + (int(255 * A),))
        text_c(d, y + 130, 'PACK', font(108), NAVY + (int(255 * A),))
        text_c(d, y + 268, 'SHOULD YOU BUY?', font(84), RED + (int(255 * A),))
        for i, (dx, rot) in enumerate([(-270, 9), (270, -9), (0, 0)]):
            p = ease_back(prog(t, -0.45 + i * 0.12, 0.15 + i * 0.12))
            if p <= 0: continue
            cy = 1150 + (1 - clamp(p)) * 500 + 8 * math.sin(t * 2 + i)
            paste_c(im, HOOK[i], W / 2 + dx, cy, 0.9 * max(p, 0.01), A * clamp(p * 2), rot)
        pill(im, W / 2, 1460, 'Every size compared', font(54), WHITE, GREEN, A * ease_out(prog(t, 0.9, 1.3)))

    # S2 #1 pick for one child: 12-pack of 4-oz cans, rating count-up
    if T_PICK < t < T_CANS:
        A = scene_alpha(t, T_PICK, T_CANS); u = t - T_PICK
        pill(im, W / 2, 320, '#1 PICK – ONE CHILD', font(58), WHITE, RED, A)
        text_c(d, 395, '12-pack, 4-oz cans', font(90), NAVY + (int(255 * A),))
        text_c(d, 505, 'The biggest cans in a multi-pack', font(52), (90, 90, 90, int(255 * A)))
        z = 0.86 + 0.06 * ease_out(prog(u, 0, 3.4))
        s = 760 * z; soft_shadow(im, (W / 2 - s / 2, 970 - s / 2, W / 2 + s / 2, 970 + s / 2), 0.2 * A)
        paste_c(im, TWELVE, W / 2, 970, z, A)
        k = ease_out(prog(u, 0.4, 1.6)); n = int(25679 * k); r = 4.8 * k
        text_c(d, 1335, f'{r:.1f} ★  ·  {n:,} ratings', font(70, F_UNI), (40, 40, 40, int(255 * A)))
        sub = ease_out(prog(u, 1.7, 2.2))
        text_c(d, 1425, '48 oz in total, ages 2+', font(52), (90, 90, 90, int(255 * A * sub)))

    # S2b close-up: real top-down photo of the open cans
    if T_CANS < t < T_SIZES:
        A = scene_alpha(t, T_CANS, T_SIZES); u = t - T_CANS
        text_c(d, 330, 'Big cans =', font(86), NAVY + (int(255 * A),))
        text_c(d, 440, 'fewer lids to open', font(76), RED + (int(255 * A),))
        p = ease_back(prog(u, 0.0, 0.5))
        z = 0.8 + 0.1 * max(p, 0) + 0.03 * prog(u, 0.5, 2.2); s = 760 * z
        soft_shadow(im, (W / 2 - s / 2, 940 - s / 2, W / 2 + s / 2, 940 + s / 2), 0.2 * A, 40)
        paste_c(im, TWELVE_TOP, W / 2, 940, z, A)
        text_c(d, 1340, 'Enough of each colour', font(64), NAVY + (int(255 * A * ease_out(prog(u, 0.6, 1.0))),))
        text_c(d, 1425, 'for bigger builds', font(56), (90, 90, 90, int(255 * A * ease_out(prog(u, 0.6, 1.0)))))

    # S3 other sizes: three rows slide in
    if T_SIZES < t < T_COLORS:
        A = scene_alpha(t, T_SIZES, T_COLORS); u = t - T_SIZES
        text_c(d, 270, 'Other sizes', font(92), NAVY + (int(255 * A),))
        for i, (cimg, use, col, name, what, rate) in enumerate(ROWS):
            p = ease_out(prog(u, 0.15 + i * 0.4, 0.65 + i * 0.4))
            if p <= 0: continue
            cy = 560 + i * 365; off = (1 - p) * 500
            soft_shadow(im, (60 + off, cy - 165, 390 + off, cy + 165), 0.18 * A * p)
            paste_c(im, cimg, 225 + off, cy, 1.0, A * p)
            x = 425 + off; a = int(255 * A * p)
            pill(im, x, cy - 105, use, font(44), WHITE, col, A * p, pad=(30, 14), left=True)
            d.text((x, cy - 50), name, font=font(58), fill=NAVY + (a,))
            d.text((x, cy + 25), what, font=font(44, F_UNI), fill=(90, 90, 90, a))
            d.text((x, cy + 85), rate, font=font(46, F_UNI), fill=(40, 40, 40, a))

    # S3b most colours: 65-pack with its real colour chart
    if T_COLORS < t < T_CHECK:
        A = scene_alpha(t, T_COLORS, T_CHECK); u = t - T_COLORS
        pill(im, W / 2, 320, 'MOST COLOURS', font(58), WHITE, GOLD, A)
        text_c(d, 395, 'The 65-pack', font(90), NAVY + (int(255 * A),))
        z = 0.94 + 0.06 * ease_out(prog(u, 0, 2.0))
        s = 760 * z; soft_shadow(im, (W / 2 - s / 2, 920 - s / 2, W / 2 + s / 2, 920 + s / 2), 0.2 * A)
        paste_c(im, C65, W / 2, 920, z, A)
        text_c(d, 1330, '60 different colours', font(66), NAVY + (int(255 * A * ease_out(prog(u, 0.4, 0.8))),))
        text_c(d, 1420, '4.8 ★ · 10,047 ratings', font(56, F_UNI), (40, 40, 40, int(255 * A * ease_out(prog(u, 0.8, 1.2)))))

    # S4 checklist
    if T_CHECK < t < T_CTA:
        A = scene_alpha(t, T_CHECK, T_CTA); u = t - T_CHECK
        text_c(d, 420, 'Quick answer', font(96), NAVY + (int(255 * A),))
        for i, s in enumerate(['✓  One child: 4-oz cans', '✓  Many kids: the 36-pack', '✓  Handing out: 1-oz cans']):
            p = ease_back(prog(u, 0.1 + i * 0.25, 0.5 + i * 0.25))
            if p > 0: pill(im, W / 2 + (1 - p) * 300, 760 + i * 230, s, font(56, F_UNI), WHITE, [GREEN, BLUE, RED][i], A * clamp(p))

    # S5 CTA
    if t > T_CTA:
        A = clamp((t - T_CTA) / FADE); u = t - T_CTA
        text_c(d, 360, '6 Play-Doh packs', font(88), NAVY + (int(255 * A),))
        text_c(d, 470, 'every size compared', font(70), (90, 90, 90, int(255 * A)))
        b = 1 + 0.04 * math.sin(u * 6)
        pill(im, W / 2, 760, 'Full guide on toyscout.net', font(70), WHITE, RED, A, pad=(56 * b, 30 * b))
        paste_c(im, logo, W / 2, 1040, ease_back(prog(u, 0.15, 0.65)) + 0.001, alpha=A)
        text_c(d, 1260, 'toyscout.net', font(76), NAVY + (int(255 * A),))
    im.alpha_composite(tl)
    return im.convert('RGB')

def cover():
    im = bg(1.0).convert('RGBA'); d = ImageDraw.Draw(im)
    text_c(d, 440, 'WHICH PLAY-DOH', font(96), NAVY)
    text_c(d, 565, 'PACK SHOULD', font(104), NAVY)
    text_c(d, 705, 'YOU BUY?', font(96), RED)
    for img, dx, rot in [(HOOK[0], -260, 9), (HOOK[1], 260, -9)]:
        paste_c(im, img, W / 2 + dx, 1110, 0.78, 1.0, rot)
    soft_shadow(im, (W / 2 - 230, 1110 - 230, W / 2 + 230, 1110 + 230), 0.25)
    paste_c(im, TWELVE, W / 2, 1110, 0.6)
    pill(im, W / 2, 1430, 'Every size compared', font(56), WHITE, GREEN)
    return im.convert('RGB')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':   # render a few check frames only
        for ts in [0.0, 2.9, 5.0, 7.5, 10.8, 12.3, 13.4, 15.2, 18.4]:
            frame(ts).save(os.path.join(OUT, f'preview_{SLUG}_{ts:.1f}.png'))
        cover().save(os.path.join(OUT, f'cover_{SLUG}.jpg'), quality=92); sys.exit()
    n = int(DUR * FPS)
    for i in range(n):
        frame(i / FPS * WARP).save(os.path.join(FR, f'f{i:04d}.png'))
        if i % 60 == 0: print('frame', i, '/', n, flush=True)
    mp4 = os.path.join(OUT, f'toyscout_{SLUG}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(FR, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', mp4], check=True)
    cover().save(os.path.join(OUT, f'cover_{SLUG}.jpg'), quality=92)
    shutil.rmtree(FR)
    print('wrote', mp4)
