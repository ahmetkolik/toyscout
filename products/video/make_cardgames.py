"""Motion-graphic Short (9:16) for post16 (family card games), built from real product photos.
Renders PNG frames with Pillow, then encodes with ffmpeg. No AI generation. Style copied from make_needoh_v2.py.
Data (rating, rating count, players, ages) comes from js/data.js; players/ages from the product titles/bullets."""
import math, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.expanduser('~/Downloads/toyscout-video')
SITE = '/Users/ahmet/Downloads/Toyscout/assets'
W, H, FPS = 1080, 1920, 30
DUR = 12.0
FR = os.path.join(OUT, 'frames_cardgames'); os.makedirs(FR, exist_ok=True)

CREAM = (255, 246, 232); NAVY = (27, 42, 74); RED = (232, 64, 42); BLUE = (40, 120, 220)
PINK = (236, 72, 153); GREEN = (46, 160, 90); TEAL = (20, 150, 160); WHITE = (255, 255, 255); GREY = (90, 90, 90)
F_ROUND = '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf'
F_UNI = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
def font(sz, f=F_ROUND): return ImageFont.truetype(f, sz)

# ---------- products (all from post16, numbers from js/data.js) ----------
PICKS = {
    'skyjo': dict(asin='B06XZ9K244', name='SKYJO', rating=4.8, rc=76155, tags=['2–8 players', 'Ages 8+']),
    'uno':   dict(asin='B07P6MZPK3', name='UNO', rating=4.8, rc=60942, tags=['2–10 players', 'Ages 7+']),
    'taco':  dict(asin='B077Z1R28P', name='Taco Cat Goat', rating=4.8, rc=54925, tags=['2–8 players'], name2='Cheese Pizza'),
    'kit':   dict(asin='B010TQY7A8', name='Exploding Kittens', rating=4.6, rc=59533, tags=['2–5 players', 'Ages 7+']),
}

def rounded(im, r=40):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    o = im.convert('RGBA'); o.putalpha(m); return o

def photo_card(path, size, pad=0.07, r=44):
    """Product photo (white background) centred on a white rounded card with a soft shadow."""
    src = Image.open(path).convert('RGB')
    inner = int(size * (1 - 2 * pad)); s = inner / max(src.size)
    src = src.resize((max(1, int(src.width * s)), max(1, int(src.height * s))), Image.LANCZOS)
    card = Image.new('RGB', (size, size), WHITE); card.paste(src, ((size - src.width) // 2, (size - src.height) // 2))
    card = rounded(card, r)
    m = 40; out = Image.new('RGBA', (size + 2 * m, size + 2 * m), (0, 0, 0, 0))
    sh = Image.new('RGBA', out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((m, m + 14, m + size, m + size + 14), r, fill=(27, 42, 74, 60))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16))); out.alpha_composite(card, (m, m))
    return out

def P(asin, suf=''): return f'{SITE}/products/{asin}{suf}.jpg'

hook_cards = [photo_card(P(PICKS[k]['asin']), 360) for k in ('uno', 'taco', 'kit', 'skyjo')]
sky_big = photo_card(P(PICKS['skyjo']['asin']), 640)
row_cards = {k: photo_card(P(PICKS[k]['asin']), 290, r=36) for k in ('uno', 'taco', 'kit')}
cta_cards = [photo_card(P(PICKS[k]['asin']), 230, r=30) for k in ('skyjo', 'uno', 'taco', 'kit')]

def cutout_white(im, thr=245):
    im = im.convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r > thr and g > thr and b > thr: px[x, y] = (r, g, b, 0)
    return im
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
    for i, (c, r, sp) in enumerate([((255, 214, 224), 520, 0.35), ((214, 232, 255), 600, 0.25), ((255, 236, 190), 420, 0.45)]):
        cx = W * (0.2 + 0.6 * i / 2) + 120 * math.sin(t * sp + i)
        cy = H * (0.25 + 0.3 * i) + 140 * math.cos(t * sp * 1.3 + i)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(90))

def text_c(d, y, s, f, fill, cx=W / 2):
    w = d.textlength(s, font=f); d.text((cx - w / 2, y), s, font=f, fill=fill)

def fit(d, s, size, maxw, f=F_ROUND):
    while size > 20 and d.textlength(s, font=font(size, f)) > maxw: size -= 2
    return font(size, f)

def paste_c(canvas, im, cx, cy, scale=1.0, alpha=1.0, rot=0):
    w = max(1, int(im.width * scale)); h = max(1, int(im.height * scale))
    p = im.resize((w, h), Image.LANCZOS) if scale != 1.0 else im.copy()
    if rot: p = p.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = p.split()[3].point(lambda v: int(v * alpha)); p.putalpha(a)
    canvas.alpha_composite(p, (int(cx - p.width / 2), int(cy - p.height / 2)))

def pill(canvas, cx, cy, s, f, fg, bgc, alpha=1.0, pad=(44, 22), left=None):
    d0 = ImageDraw.Draw(canvas); tw = d0.textlength(s, font=f); th = f.size
    layer = Image.new('RGBA', (int(tw + pad[0] * 2), int(th + pad[1] * 2)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer); ld.rounded_rectangle((0, 0, layer.width - 1, layer.height - 1), layer.height // 2, fill=bgc + (int(255 * alpha),))
    ld.text((pad[0], pad[1] - th * 0.12), s, font=f, fill=fg + (int(255 * alpha),))
    x = left if left is not None else int(cx - layer.width / 2)
    canvas.alpha_composite(layer, (int(x), int(cy - layer.height / 2)))
    return layer.width

def scene_alpha(t, a, b, fade=0.25):
    return clamp((t - a) / fade) * clamp((b - t) / fade)

# ---------- scenes ----------
def frame(t):
    im = bg(t).convert('RGBA'); d = ImageDraw.Draw(im)

    # S1 hook 0–2.7: title visible from frame 0, four real boxes fan in
    if t < 2.8:
        A = scene_alpha(t, -1, 2.8)
        y = 270 + 6 * math.sin(t * 3)
        text_c(d, y, 'CARD GAMES', font(118), NAVY + (int(255 * A),))
        text_c(d, y + 140, 'YOUR FAMILY WILL', font(84), NAVY + (int(255 * A),))
        text_c(d, y + 250, 'ACTUALLY PLAY', font(108), RED + (int(255 * A),))
        fan = [(-270, 1080, -12), (-90, 1020, -4), (90, 1020, 4), (270, 1080, 12)]
        for i, (dx, cy, rot) in enumerate(fan):
            p = ease_back(prog(t, 0.05 + i * 0.12, 0.5 + i * 0.12))
            if p <= 0: continue
            wob = 3 * math.sin(t * 2.2 + i)
            paste_c(im, hook_cards[i], W / 2 + dx, cy + (1 - p) * 500, 0.92, A * clamp(p), rot + wob)
        pill(im, W / 2, 1400, 'All rated 4.6★ or higher', font(54, F_UNI), WHITE, NAVY, A * ease_out(prog(t, 0.9, 1.3)))

    # S2 #1 pick 2.7–5.7: SKYJO + rating count-up + players/age
    if 2.65 < t < 5.85:
        A = scene_alpha(t, 2.65, 5.85)
        pill(im, W / 2, 330, '#1 PICK', font(62), WHITE, RED, A)
        text_c(d, 410, 'SKYJO', font(120), NAVY + (int(255 * A),))
        z = 0.94 + 0.06 * ease_out(prog(t, 2.7, 5.7))
        paste_c(im, sky_big, W / 2, 900, z, A)
        n = int(PICKS['skyjo']['rc'] * ease_out(prog(t, 3.0, 4.3)))
        d2 = ImageDraw.Draw(im)
        text_c(d2, 1250, f'4.8 ★  ·  {n:,} ratings', font(68, F_UNI), (40, 40, 40, int(255 * A)))
        s = ease_out(prog(t, 4.2, 4.6))
        pill(im, W / 2 - 190, 1405, '2–8 players', font(54, F_UNI), WHITE, TEAL, A * s)
        pill(im, W / 2 + 210, 1405, 'Ages 8+', font(54, F_UNI), WHITE, BLUE, A * s)

    # S3 three more picks 5.7–9.1: rows slide in
    if 5.65 < t < 9.25:
        A = scene_alpha(t, 5.65, 9.25)
        text_c(d, 280, 'Also on the table', font(84), NAVY + (int(255 * A),))
        for i, k in enumerate(('uno', 'taco', 'kit')):
            pk = PICKS[k]; p = ease_out(prog(t, 5.8 + i * 0.45, 6.3 + i * 0.45))
            if p <= 0: continue
            a = A * p; off = (1 - p) * 700; cy = 590 + i * 330
            paste_c(im, row_cards[k], 225 - off, cy, 1.0, a)
            dd = ImageDraw.Draw(im); x0 = 400 + off * 0.3
            nm = pk['name']; f = fit(dd, nm, 66, 610)
            ty = cy - 120 if pk.get('name2') else cy - 95
            dd.text((x0, ty), nm, font=f, fill=NAVY + (int(255 * a),))
            if pk.get('name2'):
                dd.text((x0, ty + 70), pk['name2'], font=f, fill=NAVY + (int(255 * a),)); ry = ty + 160
            else:
                ry = ty + 85
            dd.text((x0, ry), f"{pk['rating']} ★  ·  {pk['rc']:,} ratings", font=font(42, F_UNI), fill=(40, 40, 40, int(255 * a)))
            xx = x0
            for j, tg in enumerate(pk['tags']):
                xx += pill(im, 0, ry + 95, tg, font(38, F_UNI), WHITE, [TEAL, BLUE][j], a, pad=(26, 14), left=xx) + 14

    # S4 checklist 9.1–10.7 (from post16 "What to skip")
    if 9.05 < t < 10.75:
        A = scene_alpha(t, 9.05, 10.75)
        text_c(d, 420, 'Before you buy', font(96), NAVY + (int(255 * A),))
        for i, s in enumerate(['✓  Rules you can teach fast', '✓  Check the age on the box', '✓  Pick the original, not a clone']):
            p = ease_back(prog(t, 9.25 + i * 0.25, 9.65 + i * 0.25))
            if p > 0: pill(im, W / 2 + (1 - p) * 300, 740 + i * 220, s, font(54, F_UNI), WHITE, [GREEN, BLUE, RED][i], A * clamp(p))

    # S5 CTA 10.7–12
    if t > 10.65:
        A = clamp((t - 10.65) / 0.25)
        text_c(d, 330, '10 family games', font(92), NAVY + (int(255 * A),))
        text_c(d, 445, 'compared side by side', font(64), GREY + (int(255 * A),))
        for i, c in enumerate(cta_cards):
            p = ease_back(prog(t, 10.75 + i * 0.08, 11.15 + i * 0.08))
            if p > 0: paste_c(im, c, 165 + i * 250, 690, 0.95 * max(p, 0.01), A, [-5, 3, -3, 5][i])
        b = 1 + 0.04 * math.sin((t - 10.7) * 6)
        pill(im, W / 2, 920, 'Full guide on toyscout.net', font(70), WHITE, RED, A, pad=(56 * b, 30 * b))
        paste_c(im, logo, W / 2, 1140, 0.55 * (ease_back(prog(t, 10.9, 11.4)) + 0.001), A)
        d5 = ImageDraw.Draw(im)
        text_c(d5, 1290, 'toyscout.net', font(76), NAVY + (int(255 * A),))
    return im.convert('RGB')

def cover():
    im = bg(1.0).convert('RGBA'); d = ImageDraw.Draw(im)
    text_c(d, 440, 'CARD GAMES', font(124), NAVY)
    text_c(d, 590, 'YOUR FAMILY WILL', font(86), NAVY)
    text_c(d, 700, 'ACTUALLY PLAY', font(112), RED)
    for i, (dx, cy, rot) in enumerate([(-270, 1110, -12), (-90, 1050, -4), (90, 1050, 4), (270, 1110, 12)]):
        paste_c(im, hook_cards[i], W / 2 + dx, cy, 0.92, 1.0, rot)
    pill(im, W / 2, 1420, 'toyscout.net', font(62), WHITE, RED)
    return im.convert('RGB')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':   # render a few check frames only
        for ts in sys.argv[2:]:
            frame(float(ts)).save(os.path.join(OUT, f'preview_cardgames_{ts}.png'))
        cover().save(os.path.join(OUT, 'preview_cardgames_cover.png')); sys.exit()
    cover().save(os.path.join(OUT, 'cover_cardgames.jpg'), quality=92)
    n = int(DUR * FPS)
    for i in range(n):
        frame(i / FPS).save(os.path.join(FR, f'f{i:04d}.png'))
        if i % 60 == 0: print('frame', i, '/', n, flush=True)
    mp4 = os.path.join(OUT, 'toyscout_cardgames.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(FR, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', mp4], check=True)
    shutil.rmtree(FR)
    print('wrote', mp4)
