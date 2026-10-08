"""Motion-graphic TikTok test video (9:16) for the NeeDoh Gumdrop, built from real product photos.
Renders PNG frames with Pillow, then encodes with ffmpeg. No AI generation."""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.expanduser('~/Downloads/toyscout-video')  # frames + mp4 go here, outside the repo
SITE = '/Users/ahmet/Downloads/Toyscout/assets'
W, H, FPS = 1080, 1920, 30
DUR = 12.5
FR = os.path.join(OUT, 'frames'); os.makedirs(FR, exist_ok=True)

CREAM = (255, 246, 232); NAVY = (27, 42, 74); RED = (232, 64, 42); BLUE = (40, 120, 220)
PINK = (236, 72, 153); GREEN = (46, 160, 90); WHITE = (255, 255, 255)
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

main = Image.open(f'{SITE}/products/B0C6XBP4CW.jpg').convert('RGB')
gum = cutout_white(main.crop((640, 10, 1270, 720)))           # blue gumdrop
sq = Image.open(f'{SITE}/products/B0C6XBP4CW_4.jpg').convert('RGB')
sq_l = sq.crop((140, 398, 712, 970)); sq_r = sq.crop((790, 398, 1362, 970))   # two real hand-squeeze photos
logo = cutout_white(Image.open(f'{SITE}/logo-blocks.png'), 245)
logo = logo.crop(logo.getbbox()); logo = logo.resize((300, int(logo.height * 300 / logo.width)), Image.LANCZOS)

def rounded(im, r=48):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *im.size), r, fill=255)
    o = im.convert('RGBA'); o.putalpha(m); return o

sq_l = rounded(sq_l.resize((470, 470), Image.LANCZOS)); sq_r = rounded(sq_r.resize((470, 470), Image.LANCZOS))

# ---------- easing ----------
def clamp(x): return max(0.0, min(1.0, x))
def ease_out(t): return 1 - (1 - t) ** 3
def ease_back(t, s=1.7):
    t -= 1; return t * t * ((s + 1) * t + s) + 1
def prog(t, a, b): return clamp((t - a) / (b - a))

# ---------- drawing helpers ----------
def bg(t):
    im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im)
    # soft moving blobs for depth
    for i, (c, r, sp) in enumerate([((255, 214, 224), 520, 0.35), ((214, 232, 255), 600, 0.25), ((255, 236, 190), 420, 0.45)]):
        cx = W * (0.2 + 0.6 * i / 2) + 120 * math.sin(t * sp + i)
        cy = H * (0.25 + 0.3 * i) + 140 * math.cos(t * sp * 1.3 + i)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(90))

def text_c(d, y, s, f, fill, stroke=0, sf=None):
    w = d.textlength(s, font=f); d.text(((W - w) / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sf)

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
    canvas.paste(sh.filter(ImageFilter.GaussianBlur(22)), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)))

# ---------- scenes ----------
def scene_alpha(t, a, b, fade=0.25):
    return clamp((t - a) / fade) * clamp((b - t) / fade)

def frame(t):
    im = bg(t).convert('RGBA'); d = ImageDraw.Draw(im)

    # S1 hook 0–2.6: title drops in, gumdrop pops and squishes
    if t < 2.8:
        A = scene_alpha(t, -1, 2.8)
        p = ease_out(prog(t, 0.0, 0.5))
        y = -200 + p * 360
        text_c(d, y, 'WHICH NEEDOH', font(108), NAVY + (int(255 * A),))
        text_c(d, y + 140, 'SHOULD YOU BUY?', font(96), RED + (int(255 * A),))
        s = ease_back(prog(t, 0.35, 0.95))
        sq_amt = 0.16 * math.sin(clamp((t - 1.3) / 1.1) * math.pi * 2) * (1 - clamp((t - 1.3) / 1.1))
        shadow(im, W / 2, 1450, 560 * max(s, 0.01), 0.22 * A)
        paste_c(im, gum, W / 2, 1050 + 40 * sq_amt * 3, 0.95 * max(s, 0.01), 1 + sq_amt, 1 - sq_amt, A)

    # S2 pick 2.6–5.6: label + rating counter + slow zoom
    if 2.55 < t < 5.75:
        A = scene_alpha(t, 2.55, 5.75)
        pill(im, W / 2, 330, '#1 PICK', font(62), WHITE, RED, A)
        text_c(d, 430, 'NeeDoh Gumdrop', font(104), NAVY + (int(255 * A),))
        z = 0.92 + 0.08 * ease_out(prog(t, 2.6, 5.6))
        shadow(im, W / 2, 1300, 520, 0.2 * A)
        paste_c(im, gum, W / 2, 960, z, alpha=A)
        n = int(4453 * ease_out(prog(t, 3.0, 4.4)))
        d2 = ImageDraw.Draw(im)
        text_c(d2, 1420, f'4.4 ★  ·  {n:,} ratings', font(70, F_UNI), (40, 40, 40, int(255 * A)))
        sub = ease_out(prog(t, 4.2, 4.7))
        text_c(d2, 1530, 'Best-rated NeeDoh we track', font(58), (90, 90, 90, int(255 * A * sub)))

    # S3 feel 5.6–8.8: two real squeeze photos slide in
    if 5.55 < t < 8.95:
        A = scene_alpha(t, 5.55, 8.95)
        pl = ease_out(prog(t, 5.6, 6.2)); pr = ease_out(prog(t, 6.6, 7.2))
        paste_c(im, sq_l, -300 + pl * 600, 760, 1.0, alpha=A, rot=-4)
        paste_c(im, sq_r, W + 300 - pr * 590, 1180, 1.0, alpha=A, rot=4)
        d3 = ImageDraw.Draw(im)
        a1 = ease_out(prog(t, 5.9, 6.3)); a2 = ease_out(prog(t, 6.9, 7.3))
        text_c(d3, 300, 'Soft when you', font(80), NAVY + (int(255 * A * a1),))
        text_c(d3, 395, 'squeeze slow.', font(80), BLUE + (int(255 * A * a1),))
        text_c(d3, 1500, 'Firm when you', font(80), NAVY + (int(255 * A * a2),))
        text_c(d3, 1595, 'squeeze fast.', font(80), PINK + (int(255 * A * a2),))

    # S4 checklist 8.8–10.6
    if 8.75 < t < 10.75:
        A = scene_alpha(t, 8.75, 10.75)
        text_c(d, 420, 'Why kids love it', font(96), NAVY + (int(255 * A),))
        for i, s in enumerate(['✓  Quiet in class', '✓  Bounces back every time', '✓  Ages 3 and up']):
            p = ease_back(prog(t, 9.0 + i * 0.3, 9.4 + i * 0.3))
            if p > 0: pill(im, W / 2 + (1 - p) * 300, 760 + i * 230, s, font(62, F_UNI), WHITE, [GREEN, BLUE, RED][i], A * clamp(p))

    # S5 CTA 10.6–12.5
    if t > 10.55:
        A = clamp((t - 10.55) / 0.25)
        text_c(d, 360, 'NeeDoh vs Slimygloop', font(84), NAVY + (int(255 * A),))
        text_c(d, 470, 'vs slow-rise squishies', font(64), (90, 90, 90, int(255 * A)))
        b = 1 + 0.04 * math.sin((t - 10.6) * 6)
        pill(im, W / 2, 760, 'Full guide: link in bio', font(70), WHITE, RED, A, pad=(56 * b, 30 * b))
        paste_c(im, logo, W / 2, 1190, ease_back(prog(t, 10.8, 11.3)) + 0.001, alpha=A)
        d5 = ImageDraw.Draw(im)
        text_c(d5, 1480, 'toyscout.net', font(76), NAVY + (int(255 * A),))
    return im.convert('RGB')

n = int(DUR * FPS)
for i in range(n):
    frame(i / FPS).save(os.path.join(FR, f'f{i:04d}.png'))
    if i % 60 == 0: print('frame', i, '/', n, flush=True)
mp4 = os.path.join(OUT, 'toyscout_needoh_gumdrop_test.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(FR, 'f%04d.png'),
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', mp4], check=True)
print('wrote', mp4)
