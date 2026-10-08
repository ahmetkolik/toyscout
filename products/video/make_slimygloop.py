"""Motion-graphic Short (9:16) for post19 "NeeDoh vs Slimygloop", built from real product photos.
Renders PNG frames with Pillow, then encodes with ffmpeg. No AI generation. Style copied from make_needoh_v2.py.
All text stays inside the Shorts safe zone (x 60-1020, y 250-1500). No prices anywhere (owner rule)."""
import math, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.expanduser('~/Downloads/toyscout-video')
SITE = '/Users/ahmet/Downloads/Toyscout/assets'
W, H, FPS = 1080, 1920, 30
DUR = 12.0
FR = os.path.join(OUT, 'frames_slimygloop'); os.makedirs(FR, exist_ok=True)

CREAM = (255, 246, 232); NAVY = (27, 42, 74); RED = (232, 64, 42); BLUE = (40, 120, 220)
PINK = (236, 72, 153); GREEN = (46, 160, 90); PURPLE = (130, 70, 200); WHITE = (255, 255, 255)
F_ROUND = '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf'
F_UNI = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
def font(sz, f=F_ROUND): return ImageFont.truetype(f, sz)
P = f'{SITE}/products'

# ---------- assets ----------
def cutout_white(im, thr=238):
    im = im.convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r > thr and g > thr and b > thr: px[x, y] = (r, g, b, 0)
    return im

def card(im, size, r=48, border=10):
    """Rounded photo card with a white frame."""
    im = im.convert('RGB').resize(size, Image.LANCZOS)
    cw, ch = size[0] + border * 2, size[1] + border * 2
    out = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    m = Image.new('L', (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw, ch), r + border, fill=255)
    out.paste(Image.new('RGBA', (cw, ch), WHITE + (255,)), (0, 0), m)
    m2 = Image.new('L', size, 0); ImageDraw.Draw(m2).rounded_rectangle((0, 0, *size), r, fill=255)
    out.paste(im, (border, border), m2)
    return out

def fit(im, w):
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)

# NeeDoh Gumdrop (B0C6XBP4CW) - same clean cutout as the NeeDoh template
gum = cutout_white(Image.open(f'{P}/B0C6XBP4CW.jpg').convert('RGB').crop((640, 10, 1270, 720)))
nd_sq = Image.open(f'{P}/B0C6XBP4CW_4.jpg').convert('RGB').crop((140, 398, 712, 970))       # real NeeDoh squeeze
# Slimygloop Minecraft Creeper (B0GZ4ZZ4QS)
cr_main = Image.open(f'{P}/B0GZ4ZZ4QS.jpg').convert('RGB')
cr_hand = Image.open(f'{P}/B0GZ4ZZ4QS_2.jpg').convert('RGB').crop((640, 160, 1500, 1020))   # avoids baked-in text
cr_str = Image.open(f'{P}/B0GZ4ZZ4QS_1.jpg').convert('RGB').crop((0, 0, 740, 1500))         # stretched gel, no text
# Slimygloop Kuromi (B0G36TDT1W) and Squishmallows (B0G36Z353F) - main photos (pack + gel)
ku_main = Image.open(f'{P}/B0G36TDT1W.jpg').convert('RGB')
sm_main = Image.open(f'{P}/B0G36Z353F.jpg').convert('RGB')
logo = cutout_white(Image.open(f'{SITE}/logo-blocks.png'), 245)
logo = logo.crop(logo.getbbox()); logo = fit(logo, 200)

C_CR_MAIN = card(cr_main, (430, 417), 40)
C_CR_HAND = card(cr_hand, (720, 720), 56)
C_ND_SQ = card(nd_sq, (420, 420), 44)
C_CR_STR = card(cr_str, (300, 608), 44)
C_KU = card(ku_main, (430, 400), 40)
C_SM = card(sm_main, (430, 421), 40)

# ---------- easing ----------
def clamp(x): return max(0.0, min(1.0, x))
def ease_out(t): return 1 - (1 - t) ** 3
def ease_back(t, s=1.7):
    t -= 1; return t * t * ((s + 1) * t + s) + 1
def prog(t, a, b): return clamp((t - a) / (b - a))

# ---------- drawing helpers ----------
def bg(t):
    im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im)
    for i, (c, r, sp) in enumerate([((214, 245, 214), 520, 0.35), ((232, 220, 255), 600, 0.25), ((255, 236, 190), 420, 0.45)]):
        cx = W * (0.2 + 0.6 * i / 2) + 120 * math.sin(t * sp + i)
        cy = H * (0.25 + 0.3 * i) + 140 * math.cos(t * sp * 1.3 + i)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(90))

def text_c(d, y, s, f, fill, cx=W / 2):
    w = d.textlength(s, font=f); d.text((cx - w / 2, y), s, font=f, fill=fill)

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

# ---------- scenes ----------
def frame(t):
    im = bg(t).convert('RGBA'); d = ImageDraw.Draw(im)

    # S1 hook 0-2.4: title visible from frame 0, NeeDoh vs Slimygloop pop in
    if t < 2.4:
        A = scene_alpha(t, -1, 2.4)
        y = 290 + 6 * math.sin(t * 3)
        text_c(d, y, 'SLIMYGLOOP', font(118), GREEN + (int(255 * A),))
        text_c(d, y + 145, 'OR NEEDOH?', font(118), NAVY + (int(255 * A),))
        pl = 0.7 + 0.3 * ease_back(prog(t, 0.0, 0.45)); pr = 0.7 + 0.3 * ease_back(prog(t, 0.1, 0.55))
        sq_amt = 0.14 * math.sin(clamp((t - 1.0) / 1.0) * math.pi * 2) * (1 - clamp((t - 1.0) / 1.0))
        shadow(im, 290, 1330, 380, 0.2 * A)
        paste_c(im, gum, 290, 1030, 0.62 * max(pl, 0.01), 1 + sq_amt, 1 - sq_amt, A)
        paste_c(im, C_CR_MAIN, 800, 1010, 0.92 * pr, alpha=A, rot=5)
        vs = 0.6 + 0.4 * ease_back(prog(t, 0.0, 0.4))
        if vs > 0: pill(im, 540, 1020, 'VS', font(72), WHITE, RED, A * clamp(vs), pad=(34, 26))
        d1 = ImageDraw.Draw(im)
        text_c(d1, 1380, 'NeeDoh', font(58), NAVY + (int(255 * A),), cx=290)
        text_c(d1, 1380, 'Slimygloop', font(58), GREEN + (int(255 * A),), cx=790)

    # S2 pick 2.35-5.0: Creeper Gelli Gel + rating count-up
    if 2.35 < t < 5.0:
        A = scene_alpha(t, 2.35, 5.0)
        pill(im, W / 2, 320, 'OUR SLIMYGLOOP PICK', font(56), WHITE, GREEN, A)
        text_c(d, 400, 'Gelli Gels Creeper', font(92), NAVY + (int(255 * A),))
        z = 0.9 + 0.08 * ease_out(prog(t, 2.4, 5.0))
        paste_c(im, C_CR_HAND, W / 2, 900, z, alpha=A, rot=-2)
        n = int(1008 * ease_out(prog(t, 2.8, 4.0)))
        d2 = ImageDraw.Draw(im)
        text_c(d2, 1300, f'4.3 ★  ·  {n:,} ratings', font(70, F_UNI), (40, 40, 40, int(255 * A)))
        sub = ease_out(prog(t, 3.8, 4.3))
        text_c(d2, 1400, 'Gel + glitter, ages 4+', font(58), (90, 90, 90, int(255 * A * sub)))

    # S3 how they differ 4.95-7.4: NeeDoh squeeze vs Slimygloop stretch (real photos)
    if 4.95 < t < 7.4:
        A = scene_alpha(t, 4.95, 7.4)
        text_c(d, 290, "What's the difference?", font(78), NAVY + (int(255 * A),))
        pl = ease_out(prog(t, 5.0, 5.6)); pr = ease_out(prog(t, 5.6, 6.2))
        paste_c(im, C_ND_SQ, -260 + pl * 545, 760, 1.0, alpha=A, rot=-3)
        paste_c(im, C_CR_STR, W + 200 - pr * 420, 820, 1.0, alpha=A, rot=3)
        d3 = ImageDraw.Draw(im)
        a1 = ease_out(prog(t, 5.4, 5.8)); a2 = ease_out(prog(t, 6.0, 6.4))
        text_c(d3, 1190, 'NeeDoh', font(64), NAVY + (int(255 * A * a1),), cx=285)
        text_c(d3, 1270, 'heavy dough', font(50), BLUE + (int(255 * A * a1),), cx=285)
        text_c(d3, 1330, 'inside', font(50), BLUE + (int(255 * A * a1),), cx=285)
        text_c(d3, 1190, 'Slimygloop', font(64), GREEN + (int(255 * A * a2),), cx=800)
        text_c(d3, 1270, 'light gel +', font(50), PINK + (int(255 * A * a2),), cx=800)
        text_c(d3, 1330, 'slow glitter', font(50), PINK + (int(255 * A * a2),), cx=800)

    # S4 more characters 7.35-9.3: Kuromi + Squishmallows
    if 7.35 < t < 9.3:
        A = scene_alpha(t, 7.35, 9.3)
        text_c(d, 290, 'Pick a character', font(88), NAVY + (int(255 * A),))
        p1 = ease_back(prog(t, 7.4, 7.85)); p2 = ease_back(prog(t, 7.7, 8.15))
        if p1 > 0:
            paste_c(im, C_KU, 300, 700, max(p1, 0.01) * 0.98, alpha=A, rot=-4)
        if p2 > 0:
            paste_c(im, C_SM, 780, 1090, max(p2, 0.01) * 0.98, alpha=A, rot=4)
        d4 = ImageDraw.Draw(im)
        b1 = ease_out(prog(t, 7.9, 8.3)); b2 = ease_out(prog(t, 8.2, 8.6))
        text_c(d4, 600, 'Kuromi', font(64), PURPLE + (int(255 * A * b1),), cx=790)
        text_c(d4, 685, '4.3 ★ · 1,009', font(52, F_UNI), (60, 60, 60, int(255 * A * b1)), cx=790)
        text_c(d4, 990, 'Squishmallows', font(60), BLUE + (int(255 * A * b2),), cx=300)
        text_c(d4, 1072, '4.3 ★ · 1,094', font(52, F_UNI), (60, 60, 60, int(255 * A * b2)), cx=300)

    # S5 checklist 9.25-10.7
    if 9.25 < t < 10.7:
        A = scene_alpha(t, 9.25, 10.7)
        text_c(d, 400, 'Pick Slimygloop if', font(88), NAVY + (int(255 * A),))
        for i, s in enumerate(['✓  They love Minecraft or Sanrio', '✓  They like watching glitter', '✓  They are 4 or older']):
            p = ease_back(prog(t, 9.4 + i * 0.25, 9.8 + i * 0.25))
            if p > 0: pill(im, W / 2 + (1 - p) * 300, 700 + i * 220, s, font(52, F_UNI), WHITE, [GREEN, PURPLE, BLUE][i], A * clamp(p))

    # S6 CTA 10.65-12.0
    if t > 10.65:
        A = clamp((t - 10.65) / 0.25)
        text_c(d, 360, 'NeeDoh vs Slimygloop', font(84), NAVY + (int(255 * A),))
        text_c(d, 470, 'vs slow-rise squishies', font(64), (90, 90, 90, int(255 * A)))
        b = 1 + 0.04 * math.sin((t - 10.7) * 6)
        pill(im, W / 2, 760, 'Full guide on toyscout.net', font(70), WHITE, RED, A, pad=(56 * b, 30 * b))
        paste_c(im, logo, W / 2, 1040, ease_back(prog(t, 10.8, 11.3)) + 0.001, alpha=A)
        d5 = ImageDraw.Draw(im)
        text_c(d5, 1260, 'toyscout.net', font(76), NAVY + (int(255 * A),))
    return im.convert('RGB')

def cover():
    im = bg(1.0).convert('RGBA'); d = ImageDraw.Draw(im)
    text_c(d, 440, 'SLIMYGLOOP', font(124), GREEN + (255,))
    text_c(d, 590, 'OR NEEDOH?', font(124), NAVY + (255,))
    shadow(im, 290, 1250, 360, 0.2)
    paste_c(im, gum, 290, 1010, 0.6)
    paste_c(im, C_CR_MAIN, 800, 1000, 0.92, rot=5)
    pill(im, 540, 1010, 'VS', font(72), WHITE, RED, 1.0, pad=(34, 26))
    pill(im, W / 2, 1400, 'Which one should you buy?', font(60), WHITE, RED, 1.0)
    im.convert('RGB').save(os.path.join(OUT, 'cover_slimygloop.jpg'), quality=92)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':   # render a few check frames only
        for tt in map(float, sys.argv[2:]):
            frame(tt).save(os.path.join(OUT, f'preview_slimygloop_{tt:.1f}.png'))
        cover(); sys.exit()
    cover()
    n = int(DUR * FPS)
    for i in range(n):
        frame(i / FPS).save(os.path.join(FR, f'f{i:04d}.png'))
        if i % 60 == 0: print('frame', i, '/', n, flush=True)
    mp4 = os.path.join(OUT, 'toyscout_slimygloop.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(FR, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', mp4], check=True)
    shutil.rmtree(FR)
    print('wrote', mp4)
