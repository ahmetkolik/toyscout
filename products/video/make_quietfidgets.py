"""Motion-graphic 9:16 Short: quiet fidget toys for class (blog post17), built from real product photos.
Renders PNG frames with Pillow, then encodes with ffmpeg. No AI generation. No prices.
Usage: python3 make_quietfidgets.py            -> frames + MP4 + cover
       python3 make_quietfidgets.py preview 1 4 -> only write preview PNGs at those times (s)"""
import math, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.expanduser('~/Downloads/toyscout-video')
SITE = '/Users/ahmet/Downloads/Toyscout/assets'
SLUG = 'quietfidgets'
W, H, FPS = 1080, 1920, 30
DUR = 17.0
FR = os.path.join(OUT, f'frames_{SLUG}')

CREAM = (255, 246, 232); NAVY = (27, 42, 74); RED = (232, 64, 42); BLUE = (40, 120, 220)
PINK = (236, 72, 153); GREEN = (46, 160, 90); PURPLE = (124, 77, 200); WHITE = (255, 255, 255)
GREY = (90, 90, 90)
F_ROUND = '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf'
F_UNI = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
def font(sz, f=F_ROUND): return ImageFont.truetype(f, sz)

# ---------- assets (real product photos) ----------
P = f'{SITE}/products'
def load(name): return Image.open(f'{P}/{name}.jpg').convert('RGB')

def rounded(im, r=48):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *im.size), r, fill=255)
    o = im.convert('RGBA'); o.putalpha(m); return o

def card(im, box, size, r=44, border=10):
    """Crop box from photo, resize to square-ish size, put on a white rounded card."""
    ph = im.crop(box).resize(size, Image.LANCZOS)
    c = Image.new('RGBA', (size[0] + 2 * border, size[1] + 2 * border), (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle((0, 0, *c.size), r + border, fill=WHITE + (255,))
    c.paste(rounded(ph, r), (border, border), rounded(ph, r))
    return c

shashibo_main = load('B07W5QM4DP')        # cube + box on white
shashibo_kid = load('B07W5QM4DP_3')       # boy holding the cube (text on right)
stones = load('B0DC69M33Y')               # 6 worry stones + box
stones_hand = load('B0DC69M33Y_2')        # two hands rubbing stones
rubik = load('B092W7D64G')                # cube on white
rubik_hands = load('B092W7D64G_3')        # hands turning cube
popper = load('B0BPN4TMM5')               # hundred board popper on white

# hook fan (3 cards)
hk1 = card(shashibo_kid, (0, 420, 460, 880), (420, 420))
hk2 = card(stones_hand, (300, 450, 1350, 1500), (420, 420))
hk3 = card(rubik_hands, (250, 80, 1250, 1080), (420, 420))
# #1 pick hero
gal_shapes = card(load('B07W5QM4DP_1'), (0, 290, 1000, 1000), (520, 369))
gal_man = card(load('B07W5QM4DP_4'), (480, 180, 1000, 1000), (400, 615))
hero = card(shashibo_main, (170, 170, 830, 830), (640, 640))
# rows
r_stones = card(stones, (0, 0, 1500, 1492), (300, 300), r=36, border=8)
r_rubik = card(rubik, (0, 0, 1500, 1494), (300, 300), r=36, border=8)
r_popper = card(popper, (0, 0, 1500, 1383), (300, 300), r=36, border=8)

def cutout_white(im, thr=245):
    im = im.convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r > thr and g > thr and b > thr: px[x, y] = (r, g, b, 0)
    return im
logo = cutout_white(Image.open(f'{SITE}/logo-blocks.png'))
logo = logo.crop(logo.getbbox()); logo = logo.resize((200, int(logo.height * 200 / logo.width)), Image.LANCZOS)

# ---------- easing ----------
def clamp(x): return max(0.0, min(1.0, x))
def ease_out(t): return 1 - (1 - t) ** 3
def ease_back(t, s=1.7):
    t -= 1; return t * t * ((s + 1) * t + s) + 1
def prog(t, a, b): return clamp((t - a) / (b - a))

# ---------- drawing helpers ----------
def bg(t):
    im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im, 'RGBA')
    for i, (c, r, sp) in enumerate([((214, 240, 226), 520, 0.35), ((214, 232, 255), 600, 0.25), ((255, 236, 190), 420, 0.45)]):
        cx = W * (0.2 + 0.6 * i / 2) + 120 * math.sin(t * sp + i)
        cy = H * (0.25 + 0.3 * i) + 140 * math.cos(t * sp * 1.3 + i)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(90))

def fit(s, sz, maxw=940, f=F_ROUND):
    fo = font(sz, f); d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    while d.textlength(s, font=fo) > maxw and sz > 30:
        sz -= 2; fo = font(sz, f)
    return fo

def text_at(canvas, x, y, s, f, fill):
    # Pillow ignores the alpha of text fills, so draw opaque on a layer and fade the layer.
    a = fill[3] if len(fill) == 4 else 255
    if a <= 0: return
    l, t, r, b = f.getbbox(s); layer = Image.new('RGBA', (int(r) + 6, int(b) + 6), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((0, 0), s, font=f, fill=tuple(fill[:3]) + (255,))
    if a < 255: layer.putalpha(layer.split()[3].point(lambda v: v * a // 255))
    canvas.paste(layer, (int(x), int(y)), layer)

def text_c(d, y, s, f, fill, stroke=0, sf=None):
    w = d.textlength(s, font=f); text_at(d._image, (W - w) / 2, y, s, f, fill)

def paste_c(canvas, im, cx, cy, scale=1.0, alpha=1.0, rot=0):
    w = max(1, int(im.width * scale)); h = max(1, int(im.height * scale))
    p = im.resize((w, h), Image.LANCZOS)
    if rot: p = p.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = p.split()[3].point(lambda v: int(v * alpha)); p.putalpha(a)
    canvas.paste(p, (int(cx - p.width / 2), int(cy - p.height / 2)), p)

def pill(canvas, cx, cy, s, f, fg, bgc, alpha=1.0, pad=(44, 22)):
    d0 = ImageDraw.Draw(canvas); tw = d0.textlength(s, font=f); th = f.size
    layer = Image.new('RGBA', (int(tw + pad[0] * 2), int(th + pad[1] * 2)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer); ld.rounded_rectangle((0, 0, *layer.size), layer.height // 2, fill=bgc + (int(255 * alpha),))
    ld.text((pad[0], pad[1] - th * 0.12), s, font=f, fill=fg + (255,))
    if alpha < 1: layer.putalpha(layer.split()[3].point(lambda v: int(v * alpha)))
    canvas.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)

def shadow(canvas, cx, cy, w, alpha=0.25):
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((cx - w / 2, cy - 30, cx + w / 2, cy + 30), fill=(0, 0, 0, int(255 * alpha)))
    sh = sh.filter(ImageFilter.GaussianBlur(22)); canvas.paste(sh, (0, 0), sh)

def scene_alpha(t, a, b, fade=0.2):
    return clamp((t - a) / fade) * clamp((b - t) / fade)

ROWS = [  # (card, name, rating, count, note, colour)
    (r_stones, 'Worry Stones', '4.6', 1915, 'Quietest pick', GREEN),
    (r_rubik, "Rubik's Cube", '4.7', 10762, 'Silent in a pocket', BLUE),
    (r_popper, 'hand2mind Popper', '4.8', 1436, 'Counting aid 1–100', PURPLE),
]

# ---------- frames ----------
def frame(t, hook_static=False):
    im = bg(t); d = ImageDraw.Draw(im, 'RGBA')  # RGB canvas so RGBA fills blend

    # S1 hook 0–2.8: title visible from frame 0, three photo cards fan in
    if t < 3.0:
        A = scene_alpha(t, -1, 3.0)
        y = 290 + 6 * math.sin(t * 3)
        f1 = fit("FIDGETS THAT WON'T", 100); f2 = fit('ANNOY THE TEACHER', 100)
        text_c(d, y, "FIDGETS THAT WON'T", f1, NAVY + (int(255 * A),))
        text_c(d, y + 130, 'ANNOY THE TEACHER', f2, RED + (int(255 * A),))
        for i, (c, cx, cy, rot) in enumerate([(hk1, 300, 1000, 8), (hk3, 780, 1000, -8), (hk2, 540, 1160, 0)]):
            p = 1.0 if hook_static else ease_back(prog(t, 0.05 + i * 0.18, 0.5 + i * 0.18))
            if p > 0: paste_c(im, c, cx, cy + (1 - clamp(p)) * 120, 0.9 * max(p, 0.01), A * clamp(p * 1.5), rot)
        d = ImageDraw.Draw(im, 'RGBA')
        if hook_static: return im
        pill(im, W / 2, 1440, 'Quiet picks for class', font(54), WHITE, GREEN, A * ease_out(prog(t, 0.9, 1.3)))

    # S2 #1 pick 2.6–5.7
    if 3.0 < t < 6.6:
        A = scene_alpha(t, 3.0, 6.6)
        pill(im, W / 2, 320, '#1 QUIET PICK', font(60), WHITE, RED, A)
        text_c(d, 410, 'Shashibo Puzzle Cube', fit('Shashibo Puzzle Cube', 92), NAVY + (int(255 * A),))
        z = 0.94 + 0.06 * ease_out(prog(t, 3.0, 6.6))
        shadow(im, W / 2, 1265, 560, 0.18 * A)
        paste_c(im, hero, W / 2, 890, z, A)
        n = int(82973 * ease_out(prog(t, 3.4, 4.9)))
        d2 = ImageDraw.Draw(im, 'RGBA')
        text_c(d2, 1310, f'4.6 ★  ·  {n:,} ratings', font(68, F_UNI), (40, 40, 40, int(255 * A)))
        sub = ease_out(prog(t, 4.8, 5.3))
        text_c(d2, 1410, 'Silent, shape-shifting magnets', fit('Silent, shape-shifting magnets', 56), GREY + (int(255 * A * sub),))

    # S3 #1 pick close-up from real gallery photos 6.6–9.6
    if 6.6 < t < 9.6:
        A = scene_alpha(t, 6.6, 9.6)
        a1 = ease_out(prog(t, 6.8, 7.2)); a2 = ease_out(prog(t, 7.6, 8.0))
        text_c(d, 290, 'Folds into 100+ shapes', fit('Folds into 100+ shapes', 84), NAVY + (int(255 * A * a1),))
        text_c(d, 395, 'Strong magnets inside', fit('Strong magnets inside', 64), BLUE + (int(255 * A * a1),))
        pl = ease_out(prog(t, 6.7, 7.3)); pr = ease_out(prog(t, 7.4, 8.0))
        if pl > 0: paste_c(im, gal_shapes, -300 + pl * 640, 700, 1.0, A, rot=-4)
        if pr > 0: paste_c(im, gal_man, W + 260 - pr * 550, 1150, 1.0, A, rot=4)
        d = ImageDraw.Draw(im, 'RGBA')
        pill(im, 300, 1150, 'Shashibo', font(52), WHITE, RED, A * a2)

    # S4 three more quiet picks
    if 9.6 < t < 13.2:
        A = scene_alpha(t, 9.6, 13.2)
        text_c(d, 290, 'More quiet picks', font(88), NAVY + (int(255 * A),))
        for i, (c, name, rt, cnt, note, col) in enumerate(ROWS):
            p = ease_out(prog(t, 9.8 + i * 0.5, 10.3 + i * 0.5))
            if p <= 0: continue
            cy = 620 + i * 340; off = (1 - p) * 260
            a = A * p
            paste_c(im, c, 250 - off, cy, 1.0, a, rot=[-3, 3, -3][i])
            dd = ImageDraw.Draw(im, 'RGBA')
            x = 440 + off
            text_at(im, x, cy - 120, name, fit(name, 58, 560), NAVY + (int(255 * a),))
            text_at(im, x, cy - 40, f'{rt} ★ · {cnt:,} ratings', font(44, F_UNI), (40, 40, 40, int(255 * a)))
            # note pill, left-aligned
            fo = font(40); tw = dd.textlength(note, font=fo)
            pill(im, x + (tw + 64) / 2, cy + 70, note, fo, WHITE, col, a, pad=(32, 16))

    # S4 checklist 8.8–10.7
    if 13.2 < t < 15.2:
        A = scene_alpha(t, 13.2, 15.2)
        text_c(d, 420, 'Class-ready check', font(92), NAVY + (int(255 * A),))
        for i, s in enumerate(['✓  No clicking or rattling', '✓  Small enough for a pocket', '✓  Hard to break']):
            p = ease_back(prog(t, 13.4 + i * 0.3, 13.8 + i * 0.3))
            if p > 0: pill(im, W / 2 + (1 - p) * 300, 760 + i * 230, s, font(58, F_UNI), WHITE, [GREEN, BLUE, RED][i], A * clamp(p))

    # S5 CTA 10.6–12.5
    if t > 15.2:
        A = clamp((t - 15.2) / 0.2)
        text_c(d, 360, '8 quiet fidgets,', font(84), NAVY + (int(255 * A),))
        text_c(d, 470, 'all rated 4.4 ★ or better', font(62, F_UNI), GREY + (int(255 * A),))
        b = 1 + 0.04 * math.sin((t - 15.2) * 6)
        pill(im, W / 2, 760, 'Full guide on toyscout.net', font(70), WHITE, RED, A, pad=(56 * b, 30 * b))
        paste_c(im, logo, W / 2, 1040, ease_back(prog(t, 15.4, 15.9)) + 0.001, A)
        d5 = ImageDraw.Draw(im, 'RGBA')
        text_c(d5, 1260, 'toyscout.net', font(76), NAVY + (int(255 * A),))
    return im

def cover():
    im = frame(1.6, hook_static=True)
    d = ImageDraw.Draw(im, 'RGBA')
    pill(im, W / 2, 1440, '4 quiet picks on toyscout.net', font(54), WHITE, GREEN)
    return im.convert('RGB')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        for s in sys.argv[2:]:
            frame(float(s)).convert('RGB').save(os.path.join(OUT, f'preview_{SLUG}_{s}.png'))
        cover().save(os.path.join(OUT, f'preview_{SLUG}_cover.png'))
        sys.exit()
    os.makedirs(FR, exist_ok=True)
    n = int(DUR * FPS)
    for i in range(n):
        frame(i / FPS).convert('RGB').save(os.path.join(FR, f'f{i:04d}.png'))
        if i % 60 == 0: print('frame', i, '/', n, flush=True)
    mp4 = os.path.join(OUT, f'toyscout_{SLUG}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(FR, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', mp4], check=True)
    cover().save(os.path.join(OUT, f'cover_{SLUG}.jpg'), quality=92)
    shutil.rmtree(FR)
    print('wrote', mp4)
