"""Motion-graphic Short (9:16) for post20 (kids' advent calendars 2026, by age), built from real product photos.
Renders PNG frames with Pillow, then encodes with ffmpeg. No AI generation. Style copied from make_needoh_v2.py.
Products and ratings come from js/data.js (catalog check, early October 2026). No prices anywhere (owner rule)."""
import math, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SLUG = 'advent'
OUT = os.path.expanduser('~/Downloads/toyscout-video')  # frames + mp4 go here, outside the repo
SITE = '/Users/ahmet/Downloads/Toyscout/assets'
W, H, FPS = 1080, 1920, 30
DUR = 11.0
WARP = 12.5 / 11.0
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
SW = card(f'{P}/B0G5QKD8ZS.jpg', 760)                         # LEGO Star Wars Advent Calendar 2026 (#1)
SW_FIGS = rounded(Image.open(f'{P}/B0G5QKD8ZS_2.jpg').convert('RGB').crop((0, 420, 1500, 1500)).resize((600, 432), Image.LANCZOS), 40)
SES = card(f'{P}/0794448828.jpg', 330)                       # Sesame Street storybook calendar
CITY = card(f'{P}/B0G5QJP2BW.jpg', 330)                      # LEGO City Advent Calendar 2026
GEM = card(f'{P}/B0B75R26QM.jpg', 330)                       # National Geographic Gemstone
HOOK = [card(f'{P}/0794448828.jpg', 420), card(f'{P}/B0G1TZTY5K.jpg', 420), card(f'{P}/B0B75R26QM.jpg', 420)]
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

def scene_alpha(t, a, b, fade=0.25):
    return clamp((t - a) / fade) * clamp((b - t) / fade)

# ---------- scenes ----------
ROWS = [  # (card, age pill, colour, name, rating line) — real catalog numbers
    (SES, 'TODDLERS', PINK, 'Sesame Street', '4.8 ★ · 680 ratings', '24 mini books'),
    (CITY, 'AGES 5+', BLUE, 'LEGO City 2026', '4.7 ★ · 52 ratings', 'Mini builds + playmat'),
    (GEM, 'AGES 8–12', GREEN, 'Nat Geo Gemstone', '4.6 ★ · 3,727 ratings', '24 real gems'),
]

def frame(t):
    im = bg(t).convert('RGBA'); d = ImageDraw.Draw(im)

    # S1 hook 0–2.8: title visible from frame 0, three calendars fan in
    if t < 2.8:
        A = scene_alpha(t, -1, 2.8)
        y = 300 + 6 * math.sin(t * 3)
        text_c(d, y, 'THE ADVENT', font(112), NAVY + (int(255 * A),))
        text_c(d, y + 130, 'CALENDAR', font(112), NAVY + (int(255 * A),))
        text_c(d, y + 268, 'KIDS ACTUALLY WANT', font(80), RED + (int(255 * A),))
        for i, (dx, rot) in enumerate([(-270, 9), (270, -9), (0, 0)]):
            p = ease_back(prog(t, -0.45 + i * 0.12, 0.15 + i * 0.12))
            if p <= 0: continue
            cy = 1150 + (1 - clamp(p)) * 500
            paste_c(im, HOOK[i], W / 2 + dx, cy, 0.9 * max(p, 0.01), A * clamp(p * 2), rot)
        pill(im, W / 2, 1460, 'Sorted by age – 2026', font(54), WHITE, GREEN, A * ease_out(prog(t, 0.9, 1.3)))

    # S2 #1 pick 2.6–5.8: LEGO Star Wars, rating count-up
    if 2.55 < t < 5.85:
        A = scene_alpha(t, 2.55, 5.85)
        pill(im, W / 2, 320, '#1 PICK – AGES 6+', font(58), WHITE, RED, A)
        text_c(d, 395, 'LEGO Star Wars', font(98), NAVY + (int(255 * A),))
        text_c(d, 510, 'Advent Calendar 2026', font(62), (90, 90, 90, int(255 * A)))
        z = 0.86 + 0.06 * ease_out(prog(t, 2.6, 5.8))
        s = 760 * z; soft_shadow(im, (W / 2 - s / 2, 970 - s / 2, W / 2 + s / 2, 970 + s / 2), 0.2 * A)
        paste_c(im, SW, W / 2, 970, z, A)
        n = int(74 * ease_out(prog(t, 3.0, 4.2))); r = 4.9 * ease_out(prog(t, 3.0, 4.2))
        d2 = ImageDraw.Draw(im)
        text_c(d2, 1335, f'{r:.1f} ★  ·  {n} ratings', font(70, F_UNI), (40, 40, 40, int(255 * A)))
        sub = ease_out(prog(t, 4.2, 4.7))
        text_c(d2, 1425, 'Best-rated calendar in our guide', font(52), (90, 90, 90, int(255 * A * sub)))

    # S2b inside the doors 5.7–6.9: real minifigure photo
    if 5.65 < t < 7.0:
        A = scene_alpha(t, 5.65, 7.0)
        text_c(d, 330, 'Behind the doors:', font(82), NAVY + (int(255 * A),))
        text_c(d, 440, 'Mando + Grogu in', font(70), RED + (int(255 * A),))
        text_c(d, 525, 'holiday sweaters', font(70), RED + (int(255 * A),))
        p = ease_back(prog(t, 5.7, 6.2))
        soft_shadow(im, (W / 2 - 300, 1000 - 216, W / 2 + 300, 1000 + 216), 0.2 * A, 40)
        paste_c(im, SW_FIGS, W / 2, 1000, 0.85 + 0.15 * max(p, 0), A)
        text_c(d, 1330, '+ 8 mini vehicles', font(66), NAVY + (int(255 * A * ease_out(prog(t, 6.1, 6.5))),))

    # S3 by age 6.9–9.6: three rows slide in
    if 6.85 < t < 9.7:
        A = scene_alpha(t, 6.85, 9.7)
        text_c(d, 270, 'Pick by age', font(92), NAVY + (int(255 * A),))
        for i, (cimg, age, col, name, rate, what) in enumerate(ROWS):
            p = ease_out(prog(t, 7.0 + i * 0.35, 7.5 + i * 0.35))
            if p <= 0: continue
            cy = 560 + i * 365; off = (1 - p) * 500
            soft_shadow(im, (60 + off, cy - 165, 390 + off, cy + 165), 0.18 * A * p)
            paste_c(im, cimg, 225 + off, cy, 1.0, A * p)
            x = 425 + off; a = int(255 * A * p)
            pill(im, x, cy - 105, age, font(44), WHITE, col, A * p, pad=(30, 14), left=True)
            dd = ImageDraw.Draw(im)
            dd.text((x, cy - 50), name, font=font(58), fill=NAVY + (a,))
            dd.text((x, cy + 25), what, font=font(44), fill=(90, 90, 90, a))
            dd.text((x, cy + 85), rate, font=font(46, F_UNI), fill=(40, 40, 40, a))

    # S4 checklist 9.6–11.0
    if 9.55 < t < 11.05:
        A = scene_alpha(t, 9.55, 11.05)
        text_c(d, 420, 'Before you buy', font(96), NAVY + (int(255 * A),))
        for i, s in enumerate(['✓  Check the age on the box', '✓  Under 3? Pick a book one', '✓  New 2026 sets: fewer ratings']):
            p = ease_back(prog(t, 9.7 + i * 0.25, 10.1 + i * 0.25))
            if p > 0: pill(im, W / 2 + (1 - p) * 300, 760 + i * 230, s, font(56, F_UNI), WHITE, [GREEN, PINK, BLUE][i], A * clamp(p))

    # S5 CTA 11.0–12.5
    if t > 10.95:
        A = clamp((t - 10.95) / 0.25)
        text_c(d, 360, '9 advent calendars', font(88), NAVY + (int(255 * A),))
        text_c(d, 470, 'sorted by age', font(70), (90, 90, 90, int(255 * A)))
        b = 1 + 0.04 * math.sin((t - 11.0) * 6)
        pill(im, W / 2, 760, 'Full guide on toyscout.net', font(70), WHITE, RED, A, pad=(56 * b, 30 * b))
        paste_c(im, logo, W / 2, 1040, ease_back(prog(t, 11.1, 11.6)) + 0.001, alpha=A)
        d5 = ImageDraw.Draw(im)
        text_c(d5, 1260, 'toyscout.net', font(76), NAVY + (int(255 * A),))
    return im.convert('RGB')

def cover():
    im = bg(1.0).convert('RGBA'); d = ImageDraw.Draw(im)
    text_c(d, 440, 'THE ADVENT', font(116), NAVY)
    text_c(d, 575, 'CALENDAR', font(116), NAVY)
    text_c(d, 715, 'KIDS ACTUALLY WANT', font(82), RED)
    for img, dx, rot in [(HOOK[0], -260, 9), (HOOK[2], 260, -9)]:
        paste_c(im, img, W / 2 + dx, 1110, 0.78, 1.0, rot)
    soft_shadow(im, (W / 2 - 230, 1110 - 230, W / 2 + 230, 1110 + 230), 0.25)
    paste_c(im, SW, W / 2, 1110, 0.6)
    pill(im, W / 2, 1430, '2026 – sorted by age', font(56), WHITE, GREEN)
    return im.convert('RGB')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':   # render a few check frames only
        for ts in [0.0, 1.5, 4.5, 6.4, 8.8, 10.4, 12.2]:
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
