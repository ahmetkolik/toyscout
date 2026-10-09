"""Motion-graphic Short (9:16, ~17 s) for post18 (best action figures for kids in 2026, by age), built from real product photos.
Renders PNG frames with Pillow, then encodes with ffmpeg. No AI generation. Structure and style copied from make_advent.py.
Products and ratings come from js/data.js (all nine post18 picks are rated 4.5 stars or better). No prices anywhere (owner rule)."""
import math, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SLUG = 'actionfigures'
OUT = os.path.expanduser('~/Downloads/toyscout-video')  # frames + mp4 go here, outside the repo
SITE = '/Users/ahmet/Downloads/Toyscout/assets'
W, H, FPS = 1080, 1920, 30
DUR = 17.4
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
BUZZ = card(f'{P}/B07PQFT83F.jpg', 760)                      # Disney Store Buzz Lightyear talking figure (most-reviewed)
BUZZ_GLOW = rounded(Image.open(f'{P}/B07PQFT83F_4.jpg').convert('RGB').resize((640, 640), Image.LANCZOS), 40)  # real photo, lights on
DUOS = card(f'{P}/B0BLJT568Q.jpg', 330)                      # Fisher-Price Little People Disney Princess Story Duos
SPIDEY = card(f'{P}/B0CP481DTZ.jpg', 330)                    # Spidey and his Amazing Friends Friends & Foes Pack
OPTI = card(f'{P}/B077YYP739.jpg', 330)                      # Transformers Heroic Optimus Prime
OPTI_ROBOT = card(f'{P}/B077YYP739.jpg', 520, pad=0.04)
_t = Image.open(f'{P}/B077YYP739_2.jpg').convert('RGB').crop((0, 0, 1000, 560)); _t.thumbnail((600, 336), Image.LANCZOS)
_c = Image.new('RGB', (660, 380), WHITE); _c.paste(_t, ((660 - _t.width) // 2, (380 - _t.height) // 2))
OPTI_TRUCK = rounded(_c, 44)                                  # real photo of the truck mode
HOOK = [card(f'{P}/B083XNCRS3.jpg', 420), card(f'{P}/B077YYP739.jpg', 420), card(f'{P}/B07PQFT83F.jpg', 420)]
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

def atext(d, xy, s, f, fill):
    """Text with real alpha: Pillow ignores the alpha of a text fill on an RGBA canvas, so draw on a layer and paste."""
    canvas = d._image; l, t, r, b = d.textbbox((0, 0), s, font=f); pad = 8
    layer = Image.new('RGBA', (r + 2 * pad, b + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad, pad), s, font=f, fill=fill[:3] + (255,))
    a = fill[3] if len(fill) > 3 else 255
    if a < 255: layer.putalpha(layer.split()[3].point(lambda v: v * a // 255))
    canvas.paste(layer, (int(xy[0]) - pad, int(xy[1]) - pad), layer)

def text_c(d, y, s, f, fill, cx=W / 2):
    w = d.textlength(s, font=f); atext(d, (cx - w / 2, y), s, f, fill)

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
    ld = ImageDraw.Draw(layer); ld.rounded_rectangle((0, 0, *layer.size), layer.height // 2, fill=bgc + (255,))
    ld.text((pad[0], pad[1] - th * 0.12), s, font=f, fill=fg + (255,))
    if alpha < 1: layer.putalpha(layer.split()[3].point(lambda v: int(v * max(alpha, 0))))
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
T_HOOK, T_PICK, T_GLOW, T_AGE, T_OPTI, T_CHECK, T_CTA = 0.0, 3.0, 6.6, 9.0, 12.4, 14.4, 15.9

def fit(d, s, size, maxw, f=F_ROUND):
    while size > 30 and d.textlength(s, font=font(size, f)) > maxw: size -= 2
    return font(size, f)

# ---------- scenes ----------
ROWS = [  # (card, age pill, colour, name, rating line, what) — real catalog numbers
    (DUOS, 'UNDER 3', PINK, 'Little People Duos', '4.8 ★ · 5,376 ratings', '8 Disney figures'),
    (SPIDEY, 'AGES 3–5', BLUE, 'Spidey & Friends', '4.9 ★ · 2,733 ratings', 'Heroes + villains'),
    (OPTI, 'AGES 6–8', GREEN, 'Optimus Prime', '4.6 ★ · 11,601 ratings', 'Robot + truck'),
]

def frame(t):
    im = bg(t).convert('RGBA'); d = ImageDraw.Draw(im)

    # S1 hook: title + cards visible from frame 0
    if t < T_PICK:
        A = scene_alpha(t, -1, T_PICK)
        y = 300 + 6 * math.sin(t * 3)
        text_c(d, y, 'THE ACTION', font(112), NAVY + (int(255 * A),))
        text_c(d, y + 130, 'FIGURES', font(112), NAVY + (int(255 * A),))
        text_c(d, y + 268, 'FOR EVERY AGE', font(84), RED + (int(255 * A),))
        for i, (dx, rot) in enumerate([(-270, 9), (270, -9), (0, 0)]):
            p = ease_back(prog(t, -0.45 + i * 0.12, 0.15 + i * 0.12))
            if p <= 0: continue
            cy = 1150 + (1 - clamp(p)) * 500 + 8 * math.sin(t * 2 + i)
            paste_c(im, HOOK[i], W / 2 + dx, cy, 0.9 * max(p, 0.01), A * clamp(p * 2), rot)
        pill(im, W / 2, 1460, 'All rated 4.5 ★ or better', font(54, F_UNI), WHITE, GREEN, A * ease_out(prog(t, 0.9, 1.3)))

    # S2 most-reviewed pick: Buzz Lightyear, rating count-up
    if T_PICK < t < T_GLOW:
        A = scene_alpha(t, T_PICK, T_GLOW); u = t - T_PICK
        pill(im, W / 2, 320, 'MOST-REVIEWED – AGES 3–5', font(54), WHITE, RED, A)
        text_c(d, 395, 'Buzz Lightyear', font(98), NAVY + (int(255 * A),))
        text_c(d, 510, 'Talking action figure', font(62), (90, 90, 90, int(255 * A)))
        z = 0.86 + 0.06 * ease_out(prog(u, 0, 3.6))
        s = 760 * z; soft_shadow(im, (W / 2 - s / 2, 970 - s / 2, W / 2 + s / 2, 970 + s / 2), 0.2 * A)
        paste_c(im, BUZZ, W / 2, 970, z, A)
        k = ease_out(prog(u, 0.4, 1.6)); n = int(49775 * k); r = 4.7 * k
        d2 = ImageDraw.Draw(im)
        text_c(d2, 1335, f'{r:.1f} ★  ·  {n:,} ratings', font(70, F_UNI), (40, 40, 40, int(255 * A)))
        sub = ease_out(prog(u, 1.7, 2.2))
        text_c(d2, 1425, '#1 in Action Figures at our check', font(48), (90, 90, 90, int(255 * A * sub)))

    # S2b lights on: real photo of the glowing figure
    if T_GLOW < t < T_AGE:
        A = scene_alpha(t, T_GLOW, T_AGE); u = t - T_GLOW
        text_c(d, 300, 'Press the buttons:', font(82), NAVY + (int(255 * A),))
        text_c(d, 410, '10+ phrases, wing release', font(64), RED + (int(255 * A),))
        text_c(d, 495, 'and laser lights', font(64), RED + (int(255 * A),))
        p = ease_back(prog(u, 0.0, 0.5))
        soft_shadow(im, (W / 2 - 320, 960 - 320, W / 2 + 320, 960 + 320), 0.2 * A, 40)
        paste_c(im, BUZZ_GLOW, W / 2, 960, 0.85 + 0.15 * max(p, 0) + 0.03 * prog(u, 0.5, 2.4), A)
        text_c(d, 1360, 'Easy gift for a Toy Story fan', font(60), NAVY + (int(255 * A * ease_out(prog(u, 0.7, 1.1))),))

    # S3 by age: three rows slide in
    if T_AGE < t < T_OPTI:
        A = scene_alpha(t, T_AGE, T_OPTI); u = t - T_AGE
        text_c(d, 270, 'Pick by age', font(92), NAVY + (int(255 * A),))
        for i, (cimg, age, col, name, rate, what) in enumerate(ROWS):
            p = ease_out(prog(u, 0.15 + i * 0.4, 0.65 + i * 0.4))
            if p <= 0: continue
            cy = 560 + i * 365; off = (1 - p) * 500
            soft_shadow(im, (60 + off, cy - 165, 390 + off, cy + 165), 0.18 * A * p)
            paste_c(im, cimg, 225 + off, cy, 1.0, A * p)
            x = 425 + off; a = int(255 * A * p)
            pill(im, x, cy - 105, age, font(44), WHITE, col, A * p, pad=(30, 14), left=True)
            dd = ImageDraw.Draw(im)
            atext(dd, (x, cy - 50), name, fit(dd, name, 58, 590), NAVY + (a,))
            atext(dd, (x, cy + 25), what, font(44), (90, 90, 90, a))
            atext(dd, (x, cy + 85), rate, fit(dd, rate, 46, 590, F_UNI), (40, 40, 40, a))

    # S3b ages 6-8 detail: robot and truck, both real photos
    if T_OPTI < t < T_CHECK:
        A = scene_alpha(t, T_OPTI, T_CHECK); u = t - T_OPTI
        pill(im, W / 2, 320, 'AGES 6–8', font(58), WHITE, GREEN, A)
        text_c(d, 395, 'Two toys in one', font(84), NAVY + (int(255 * A),))
        p1 = ease_back(prog(u, 0.0, 0.45)); p2 = ease_back(prog(u, 0.35, 0.8))
        soft_shadow(im, (W / 2 - 195, 740 - 195, W / 2 + 195, 740 + 195), 0.18 * A)
        paste_c(im, OPTI_ROBOT, W / 2, 740, 0.6 + 0.15 * max(p1, 0), A * clamp(p1 * 2))
        if p2 > 0:
            text_c(d, 945, '↓', font(70, F_UNI), RED + (int(255 * A * clamp(p2)),))
            soft_shadow(im, (W / 2 - 330, 1210 - 190, W / 2 + 330, 1210 + 190), 0.18 * A * clamp(p2))
            paste_c(im, OPTI_TRUCK, W / 2, 1210, 0.9 + 0.1 * max(p2, 0), A * clamp(p2 * 2))
        text_c(d, 1440, 'Robot to truck in 6 steps', font(58), NAVY + (int(255 * A * ease_out(prog(u, 0.8, 1.2))),))

    # S4 checklist
    if T_CHECK < t < T_CTA:
        A = scene_alpha(t, T_CHECK, T_CTA); u = t - T_CHECK
        text_c(d, 420, 'Before you buy', font(96), NAVY + (int(255 * A),))
        for i, s in enumerate(['✓  Check the age on the box', '✓  Under 3: no small parts', '✓  More joints = less rough play']):
            p = ease_back(prog(u, 0.1 + i * 0.25, 0.5 + i * 0.25))
            if p > 0: pill(im, W / 2 + (1 - p) * 300, 760 + i * 230, s, font(54, F_UNI), WHITE, [GREEN, BLUE, RED][i], A * clamp(p))

    # S5 CTA
    if t > T_CTA:
        A = clamp((t - T_CTA) / FADE); u = t - T_CTA
        text_c(d, 360, '9 action figures', font(88), NAVY + (int(255 * A),))
        text_c(d, 470, 'sorted by age', font(70), (90, 90, 90, int(255 * A)))
        b = 1 + 0.04 * math.sin(u * 6)
        pill(im, W / 2, 760, 'Full guide on toyscout.net', font(70), WHITE, RED, A, pad=(56 * b, 30 * b))
        paste_c(im, logo, W / 2, 1040, ease_back(prog(u, 0.15, 0.65)) + 0.001, alpha=A)
        d5 = ImageDraw.Draw(im)
        text_c(d5, 1260, 'toyscout.net', font(76), NAVY + (int(255 * A),))
    return im.convert('RGB')

def cover():
    im = bg(1.0).convert('RGBA'); d = ImageDraw.Draw(im)
    text_c(d, 440, 'THE ACTION', font(116), NAVY)
    text_c(d, 575, 'FIGURES', font(116), NAVY)
    text_c(d, 715, 'FOR EVERY AGE', font(88), RED)
    for img, dx, rot in [(HOOK[0], -260, 9), (HOOK[1], 260, -9)]:
        paste_c(im, img, W / 2 + dx, 1110, 0.78, 1.0, rot)
    soft_shadow(im, (W / 2 - 230, 1110 - 230, W / 2 + 230, 1110 + 230), 0.25)
    paste_c(im, BUZZ, W / 2, 1110, 0.6)
    pill(im, W / 2, 1430, '2026 – sorted by age', font(56), WHITE, GREEN)
    return im.convert('RGB')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':   # render a few check frames only
        for ts in [0.0, 2.9, 5.0, 7.8, 10.8, 13.5, 15.2, 17.2]:
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
