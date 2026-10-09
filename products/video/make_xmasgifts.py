"""Motion-graphic Short (9:16, ~17 s) for post15 (Christmas gifts for kids by age), built from real product photos.
Renders PNG frames with Pillow, then encodes with ffmpeg. No AI generation. Structure and style copied from make_advent.py.
Products and ratings come from js/data.js (catalog check, early October 2026). No prices anywhere (owner rule)."""
import math, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SLUG = 'xmasgifts'
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
MEGA = card(f'{P}/B007GE75HY.jpg', 760)                        # Mega Bloks First Builders Big Building Bag (#1, ages 0-2)
MEGA_KID = rounded(Image.open(f'{P}/B007GE75HY_1.jpg').convert('RGB').crop((0, 0, 1425, 1290)).resize((640, 579), Image.LANCZOS), 40)
BLUEY = card(f'{P}/B083XNCRS3.jpg', 330)                      # Bluey Family Figure 4-Pack (3-5)
TACO = card(f'{P}/B077Z1R28P.jpg', 330)                       # Taco Cat Goat Cheese Pizza (6-8)
BANANA = card(f'{P}/1932188126.jpg', 330)                     # Bananagrams (9-12)
OCTO = card(f'{P}/B07H48YNJ2.jpg', 640)                       # TeeTurtle Reversible Octopus
HOOK = [card(f'{P}/B083XNCRS3.jpg', 420), card(f'{P}/B06XZ9K244.jpg', 420), card(f'{P}/B07H48YNJ2.jpg', 420)]
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

def text_at(canvas, x, y, s, f, fill):
    # Pillow ignores the alpha in a text fill on an RGBA canvas, so faded text goes on its own layer
    a = fill[3] if len(fill) == 4 else 255
    if a <= 0: return
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((x, y), s, font=f, fill=tuple(fill[:3]) + (255,))
    if a < 255: layer.putalpha(layer.split()[3].point(lambda v: v * a // 255))
    canvas.alpha_composite(layer)

def text_c(d, y, s, f, fill, cx=W / 2):
    w = d.textlength(s, font=f); text_at(d._image, cx - w / 2, y, s, f, fill)

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
T_HOOK, T_PICK, T_CLOSE, T_AGE, T_OCTO, T_CHECK, T_CTA = 0.0, 3.0, 6.6, 9.0, 12.4, 14.4, 15.9

# ---------- scenes ----------
ROWS = [  # (card, age pill, colour, name, what, rating line) - real catalog numbers (js/data.js)
    (BLUEY, 'AGES 3–5', PINK, 'Bluey Family', 'Bingo, Chilli + Bandit', '4.8 ★ · 25,043 ratings'),
    (TACO, 'AGES 6–8', BLUE, 'Taco Cat Goat', 'Fast slap card game', '4.8 ★ · 54,925 ratings'),
    (BANANA, 'AGES 9–12', GREEN, 'Bananagrams', '144 letter tiles', '4.9 ★ · 26,903 ratings'),
]

def frame(t):
    im = bg(t).convert('RGBA'); d = ImageDraw.Draw(im)

    # S1 hook: title + cards visible from frame 0
    if t < T_PICK:
        A = scene_alpha(t, -1, T_PICK)
        y = 300 + 6 * math.sin(t * 3)
        text_c(d, y, 'CHRISTMAS', font(124), RED + (int(255 * A),))
        text_c(d, y + 140, 'GIFTS KIDS', font(112), NAVY + (int(255 * A),))
        text_c(d, y + 270, 'ACTUALLY ASK FOR', font(84), NAVY + (int(255 * A),))
        for i, (dx, rot) in enumerate([(-270, 9), (270, -9), (0, 0)]):
            p = ease_back(prog(t, -0.45 + i * 0.12, 0.15 + i * 0.12))
            if p <= 0: continue
            cy = 1150 + (1 - clamp(p)) * 500 + 8 * math.sin(t * 2 + i)
            paste_c(im, HOOK[i], W / 2 + dx, cy, 0.9 * max(p, 0.01), A * clamp(p * 2), rot)
        pill(im, W / 2, 1460, 'One pick per age', font(54), WHITE, GREEN, A * ease_out(prog(t, 0.9, 1.3)))

    # S2 #1 pick: Mega Bloks, rating count-up
    if T_PICK < t < T_CLOSE:
        A = scene_alpha(t, T_PICK, T_CLOSE); u = t - T_PICK
        pill(im, W / 2, 320, 'AGES 0–2', font(58), WHITE, RED, A)
        text_c(d, 395, 'Mega Bloks', font(98), NAVY + (int(255 * A),))
        text_c(d, 510, 'First Builders Big Bag', font(62), (90, 90, 90, int(255 * A)))
        z = 0.86 + 0.06 * ease_out(prog(u, 0, 3.6))
        s = 760 * z; soft_shadow(im, (W / 2 - s / 2, 970 - s / 2, W / 2 + s / 2, 970 + s / 2), 0.2 * A)
        paste_c(im, MEGA, W / 2, 970, z, A)
        k = ease_out(prog(u, 0.25, 1.45)); n = int(132122 * k); r = 4.8
        d2 = ImageDraw.Draw(im)
        text_c(d2, 1335, f'{r:.1f} ★  ·  {n:,} ratings', font(68, F_UNI), (40, 40, 40, int(255 * A * clamp(k * 4))))
        sub = ease_out(prog(u, 1.7, 2.2))
        text_c(d2, 1425, 'Most-reviewed toy we track', font(52), (90, 90, 90, int(255 * A * sub)))

    # S2b close-up: real lifestyle photo from the listing
    if T_CLOSE < t < T_AGE:
        A = scene_alpha(t, T_CLOSE, T_AGE); u = t - T_CLOSE
        text_c(d, 330, 'Why it works:', font(82), NAVY + (int(255 * A),))
        text_c(d, 440, 'blocks big enough', font(70), RED + (int(255 * A),))
        text_c(d, 525, 'for little hands', font(70), RED + (int(255 * A),))
        p = ease_back(prog(u, 0.0, 0.5))
        soft_shadow(im, (W / 2 - 320, 990 - 290, W / 2 + 320, 990 + 290), 0.2 * A, 40)
        paste_c(im, MEGA_KID, W / 2, 990, 0.85 + 0.12 * max(p, 0) + 0.03 * prog(u, 0.5, 2.4), A)
        text_c(d, 1360, 'Easy to pull apart', font(66), NAVY + (int(255 * A * ease_out(prog(u, 0.7, 1.1))),))

    # S3 by age: three rows slide in
    if T_AGE < t < T_OCTO:
        A = scene_alpha(t, T_AGE, T_OCTO); u = t - T_AGE
        text_c(d, 270, 'Older kids?', font(92), NAVY + (int(255 * A),))
        for i, (cimg, age, col, name, what, rate) in enumerate(ROWS):
            p = ease_out(prog(u, 0.15 + i * 0.4, 0.65 + i * 0.4))
            if p <= 0: continue
            cy = 560 + i * 365; off = (1 - p) * 500
            soft_shadow(im, (60 + off, cy - 165, 390 + off, cy + 165), 0.18 * A * p)
            paste_c(im, cimg, 225 + off, cy, 1.0, A * p)
            x = 425 + off; a = int(255 * A * p)
            pill(im, x, cy - 105, age, font(44), WHITE, col, A * p, pad=(30, 14), left=True)
            dd = ImageDraw.Draw(im)
            text_at(im, x, cy - 50, name, font(58), NAVY + (a,))
            text_at(im, x, cy + 25, what, font(44), (90, 90, 90, a))
            text_at(im, x, cy + 85, rate, font(46, F_UNI), (40, 40, 40, a))

    # S3b stocking stuffer: reversible octopus
    if T_OCTO < t < T_CHECK:
        A = scene_alpha(t, T_OCTO, T_CHECK); u = t - T_OCTO
        pill(im, W / 2, 320, 'STOCKING STUFFER', font(58), WHITE, PINK, A)
        text_c(d, 395, 'Reversible Octopus', font(84), NAVY + (int(255 * A),))
        z = 0.94 + 0.06 * ease_out(prog(u, 0, 2.0))
        s = 640 * z; soft_shadow(im, (W / 2 - s / 2, 880 - s / 2, W / 2 + s / 2, 880 + s / 2), 0.2 * A)
        paste_c(im, OCTO, W / 2, 880, z, A)
        text_c(d, 1250, 'Flip it: happy or grumpy', font(62), NAVY + (int(255 * A * ease_out(prog(u, 0.4, 0.8))),))
        text_c(d, 1350, '4.8 ★  ·  102,871 ratings', font(56, F_UNI), (40, 40, 40, int(255 * A * ease_out(prog(u, 0.8, 1.2)))))

    # S4 checklist
    if T_CHECK < t < T_CTA:
        A = scene_alpha(t, T_CHECK, T_CTA); u = t - T_CHECK
        text_c(d, 420, 'Before you buy', font(96), NAVY + (int(255 * A),))
        for i, s in enumerate(['✓  Check the age on the box', '✓  Skip blind-bag toys', '✓  Look for 25,000+ ratings']):
            p = ease_back(prog(u, 0.1 + i * 0.25, 0.5 + i * 0.25))
            if p > 0: pill(im, W / 2 + (1 - p) * 300, 760 + i * 230, s, font(56, F_UNI), WHITE, [GREEN, BLUE, RED][i], A * clamp(p))

    # S5 CTA
    if t > T_CTA:
        A = clamp((t - T_CTA) / FADE); u = t - T_CTA
        text_c(d, 360, '10 gifts by age', font(88), NAVY + (int(255 * A),))
        text_c(d, 470, 'all rated 4.7 ★ or better', font(66, F_UNI), (90, 90, 90, int(255 * A)))
        b = 1 + 0.04 * math.sin(u * 6)
        pill(im, W / 2, 760, 'Full guide on toyscout.net', font(70), WHITE, RED, A, pad=(56 * b, 30 * b))
        paste_c(im, logo, W / 2, 1040, ease_back(prog(u, 0.15, 0.65)) + 0.001, alpha=A)
        d5 = ImageDraw.Draw(im)
        text_c(d5, 1260, 'toyscout.net', font(76), NAVY + (int(255 * A),))
    return im.convert('RGB')

def cover():
    im = bg(1.0).convert('RGBA'); d = ImageDraw.Draw(im)
    text_c(d, 430, 'CHRISTMAS', font(128), RED)
    text_c(d, 575, 'GIFTS KIDS', font(116), NAVY)
    text_c(d, 710, 'ACTUALLY ASK FOR', font(86), NAVY)
    for img, dx, rot in [(HOOK[0], -260, 9), (HOOK[2], 260, -9)]:
        paste_c(im, img, W / 2 + dx, 1110, 0.78, 1.0, rot)
    soft_shadow(im, (W / 2 - 230, 1110 - 230, W / 2 + 230, 1110 + 230), 0.25)
    paste_c(im, MEGA, W / 2, 1110, 0.6)
    pill(im, W / 2, 1430, 'One pick per age', font(56), WHITE, GREEN)
    return im.convert('RGB')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':   # render a few check frames only
        for ts in [0.0, 2.9, 5.0, 7.8, 10.8, 12.5, 13.5, 15.2, 17.2]:
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
