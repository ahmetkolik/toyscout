"""Motion-graphic Short (9:16, ~17 s) for post4 (best toys for 3-year-old girls), Christmas-gift angle, built from real product photos.
Renders PNG frames with Pillow, then encodes with ffmpeg. No AI generation. Structure and style copied from make_advent.py.
Products and ratings come from js/data.js (catalog check, 2026-10-09). No prices anywhere (owner rule)."""
import math, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SLUG = 'age3girls'
OUT = os.path.expanduser('~/Downloads/toyscout-video')  # frames + mp4 go here, outside the repo
SITE = '/Users/ahmet/Downloads/Toyscout/assets'
W, H, FPS = 1080, 1920, 30
DUR = 17.4
WARP = 1.0
FR = os.path.join(OUT, f'frames_{SLUG}')

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
BLUEY = card(f'{P}/B09PGVGCH5.jpg', 760)                     # Bluey Aqua Art water-reveal pad (No. 1 in post4)
BLUEY_HOW = card(f'{P}/B09PGVGCH5_1.jpg', 720, pad=0.0)      # real photo: color with water, dry, repeat
DOH = card(f'{P}/B07BC44JFC.jpg', 330)                       # Play-Doh Jewel Colors 12-pack
STICK = card(f'{P}/B098PMWSVS.jpg', 330)                     # Cupkin 500+ sticker book
BOARD = card(f'{P}/B0BGN1YDJH.jpg', 330)                     # Kikidex magnetic drawing board
DOH_OPEN = card(f'{P}/B07BC44JFC_2.jpg', 720, pad=0.0)       # real photo of the dough colors
HOOK = [card(f'{P}/B07BC44JFC.jpg', 420), card(f'{P}/B0BGN1YDJH.jpg', 420), card(f'{P}/B09PGVGCH5.jpg', 420)]
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

def draw_text(canvas, xy, s, f, fill):
    """Text with real alpha: ImageDraw ignores fill alpha on the RGBA canvas, so draw on a separate RGBA layer and paste."""
    fill = tuple(fill) + ((255,) if len(fill) == 3 else ())
    if fill[3] <= 0: return
    l, tp, r, b = f.getbbox(s); pad = 4
    layer = Image.new('RGBA', (r + 2 * pad, b + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad, pad), s, font=f, fill=fill[:3] + (255,))
    if fill[3] < 255: layer.putalpha(layer.split()[3].point(lambda v: v * fill[3] // 255))
    canvas.paste(layer, (int(xy[0]) - pad, int(xy[1]) - pad), layer)

def text_c(d, y, s, f, fill, cx=W / 2):
    w = d.textlength(s, font=f); draw_text(d._image, (cx - w / 2, y), s, f, fill)

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
    ld = ImageDraw.Draw(layer); ld.rounded_rectangle((0, 0, layer.width - 1, layer.height - 1), layer.height // 2, fill=bgc + (255,))
    ld.text((pad[0], pad[1] - th * 0.12), s, font=f, fill=fg + (255,))
    if alpha < 1: layer.putalpha(layer.split()[3].point(lambda v: int(v * alpha)))
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
T_HOOK, T_PICK, T_HOW, T_MORE, T_DOH, T_CHECK, T_CTA = 0.0, 3.0, 6.6, 9.0, 12.4, 14.4, 15.9

# ---------- scenes ----------
ROWS = [  # (card, label pill, colour, short name, what, rating line) — real catalog numbers (js/data.js)
    (DOH, 'SQUISH PLAY', BLUE, 'Play-Doh 12-Pack', '12 colors to share', '4.8 ★ · 25,679 ratings'),
    (STICK, 'QUIET TIME', GREEN, 'Sticker Book', '500+ stickers inside', '4.8 ★ · 6,866 ratings'),
    (BOARD, 'BIGGER GIFT', PINK, 'Doodle Board', 'Magnetic, erasable', '4.5 ★ · 11,787 ratings'),
]

def frame(t):
    im = bg(t).convert('RGBA'); d = ImageDraw.Draw(im)

    # S1 hook: title + cards visible from frame 0
    if t < T_PICK:
        A = scene_alpha(t, -1, T_PICK)
        y = 300 + 6 * math.sin(t * 3)
        text_c(d, y, 'WHAT TO GET A', font(100), NAVY + (int(255 * A),))
        text_c(d, y + 125, '3-YEAR-OLD GIRL', font(94), PINK + (int(255 * A),))
        text_c(d, y + 262, 'for Christmas', font(84), RED + (int(255 * A),))
        for i, (dx, rot) in enumerate([(-270, 9), (270, -9), (0, 0)]):
            p = ease_back(prog(t, -0.45 + i * 0.12, 0.15 + i * 0.12))
            if p <= 0: continue
            cy = 1150 + (1 - clamp(p)) * 500 + 8 * math.sin(t * 2 + i)
            paste_c(im, HOOK[i], W / 2 + dx, cy, 0.9 * max(p, 0.01), A * clamp(p * 2), rot)
        pill(im, W / 2, 1460, '4 picks, real ratings', font(54), WHITE, GREEN, A * ease_out(prog(t, 0.9, 1.3)))

    # S2 No. 1 pick: Bluey Aqua Art, rating count-up
    if T_PICK < t < T_HOW:
        A = scene_alpha(t, T_PICK, T_HOW); u = t - T_PICK
        pill(im, W / 2, 320, '#1 PICK – MESS-FREE', font(58), WHITE, RED, A)
        text_c(d, 395, 'Bluey Aqua Art', font(98), NAVY + (int(255 * A),))
        text_c(d, 510, 'Water-reveal pages', font(62), (90, 90, 90, int(255 * A)))
        z = 0.86 + 0.06 * ease_out(prog(u, 0, 3.6))
        s = 760 * z; soft_shadow(im, (W / 2 - s / 2, 970 - s / 2, W / 2 + s / 2, 970 + s / 2), 0.2 * A)
        paste_c(im, BLUEY, W / 2, 970, z, A)
        k = ease_out(prog(u, 0.4, 1.6)); n = int(13529 * k); r = 4.7 * k
        text_c(d, 1335, f'{r:.1f} ★  ·  {n:,} ratings', font(70, F_UNI), (40, 40, 40, int(255 * A)))
        sub = ease_out(prog(u, 1.7, 2.2))
        text_c(d, 1425, 'Just a water pen. No paint.', font(52), (90, 90, 90, int(255 * A * sub)))

    # S2b how it works: real product photo
    if T_HOW < t < T_MORE:
        A = scene_alpha(t, T_HOW, T_MORE); u = t - T_HOW
        text_c(d, 300, 'Color with water,', font(82), NAVY + (int(255 * A),))
        text_c(d, 410, 'it dries, color again', font(70), RED + (int(255 * A),))
        p = ease_back(prog(u, 0.0, 0.5))
        z = 0.85 + 0.12 * max(p, 0) + 0.03 * prog(u, 0.5, 2.4)
        s = 720 * z; soft_shadow(im, (W / 2 - s / 2, 900 - s / 2, W / 2 + s / 2, 900 + s / 2), 0.2 * A)
        paste_c(im, BLUEY_HOW, W / 2, 900, z, A)
        text_c(d, 1330, 'Car, plane, waiting room', font(62), NAVY + (int(255 * A * ease_out(prog(u, 0.7, 1.1))),))

    # S3 three more picks slide in
    if T_MORE < t < T_DOH:
        A = scene_alpha(t, T_MORE, T_DOH); u = t - T_MORE
        text_c(d, 270, '3 more she\'ll love', font(92), NAVY + (int(255 * A),))
        for i, (cimg, lab, col, name, what, rate) in enumerate(ROWS):
            p = ease_out(prog(u, 0.15 + i * 0.4, 0.65 + i * 0.4))
            if p <= 0: continue
            cy = 560 + i * 365; off = (1 - p) * 500
            soft_shadow(im, (60 + off, cy - 165, 390 + off, cy + 165), 0.18 * A * p)
            paste_c(im, cimg, 225 + off, cy, 1.0, A * p)
            x = 425 + off; a = int(255 * A * p)
            pill(im, x, cy - 105, lab, font(44), WHITE, col, A * p, pad=(30, 14), left=True)
            draw_text(im, (x, cy - 50), name, font(58), NAVY + (a,))
            draw_text(im, (x, cy + 25), what, font(44), (90, 90, 90, a))
            draw_text(im, (x, cy + 85), rate, font(46, F_UNI), (40, 40, 40, a))

    # S3b Play-Doh close-up: real photo of the dough
    if T_DOH < t < T_CHECK:
        A = scene_alpha(t, T_DOH, T_CHECK); u = t - T_DOH
        pill(im, W / 2, 320, 'AGE 3 = SQUISH STAGE', font(58), WHITE, BLUE, A)
        text_c(d, 395, 'Pinch, poke, squish', font(84), NAVY + (int(255 * A),))
        z = 0.94 + 0.06 * ease_out(prog(u, 0, 2.0))
        s = 720 * z; soft_shadow(im, (W / 2 - s / 2, 900 - s / 2, W / 2 + s / 2, 900 + s / 2), 0.2 * A)
        paste_c(im, DOH_OPEN, W / 2, 900, z, A)
        text_c(d, 1300, '12 cans = no color fights', font(62), NAVY + (int(255 * A * ease_out(prog(u, 0.4, 0.8))),))
        text_c(d, 1395, 'Roll it, shape it, share it', font(54), (90, 90, 90, int(255 * A * ease_out(prog(u, 0.8, 1.2)))))

    # S4 checklist
    if T_CHECK < t < T_CTA:
        A = scene_alpha(t, T_CHECK, T_CTA); u = t - T_CHECK
        text_c(d, 420, 'Before you wrap', font(96), NAVY + (int(255 * A),))
        for i, s in enumerate(['✓  Skip small, loose pieces', '✓  Mess-free travels best', '✓  Open-ended beats flashy']):
            p = ease_back(prog(u, 0.1 + i * 0.25, 0.5 + i * 0.25))
            if p > 0: pill(im, W / 2 + (1 - p) * 300, 760 + i * 230, s, font(56, F_UNI), WHITE, [GREEN, BLUE, RED][i], A * clamp(p))

    # S5 CTA
    if t > T_CTA:
        A = clamp((t - T_CTA) / FADE); u = t - T_CTA
        text_c(d, 360, 'Best toys for', font(88), NAVY + (int(255 * A),))
        text_c(d, 470, '3-year-old girls', font(70), (90, 90, 90, int(255 * A)))
        b = 1 + 0.04 * math.sin(u * 6)
        pill(im, W / 2, 760, 'Full guide on toyscout.net', font(60), WHITE, RED, A, pad=(56 * b, 30 * b))
        paste_c(im, logo, W / 2, 1040, ease_back(prog(u, 0.15, 0.65)) + 0.001, alpha=A)
        text_c(d, 1260, 'toyscout.net', font(76), NAVY + (int(255 * A),))
    return im.convert('RGB')

def cover():
    im = bg(1.0).convert('RGBA'); d = ImageDraw.Draw(im)
    text_c(d, 440, 'WHAT TO GET A', font(108), NAVY)
    text_c(d, 570, '3-YEAR-OLD GIRL', font(96), PINK)
    text_c(d, 708, 'for Christmas', font(86), RED)
    for img, dx, rot in [(HOOK[0], -260, 9), (HOOK[1], 260, -9)]:
        paste_c(im, img, W / 2 + dx, 1110, 0.78, 1.0, rot)
    soft_shadow(im, (W / 2 - 230, 1110 - 230, W / 2 + 230, 1110 + 230), 0.25)
    paste_c(im, BLUEY, W / 2, 1110, 0.6)
    pill(im, W / 2, 1430, '4 picks, real ratings', font(56), WHITE, GREEN)
    return im.convert('RGB')

if __name__ == '__main__':
    import sys
    os.makedirs(OUT, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':   # render a few check frames only
        for ts in sys.argv[2:] and [float(x) for x in sys.argv[2:]] or [0.0, 2.9, 3.1, 5.0, 7.8, 10.8, 12.5, 13.5, 15.2, 17.2]:
            frame(ts).save(os.path.join(OUT, f'preview_{SLUG}_{ts:.2f}.png'))
        cover().save(os.path.join(OUT, f'cover_{SLUG}.jpg'), quality=92); sys.exit()
    os.makedirs(FR, exist_ok=True); n = int(DUR * FPS)
    for i in range(n):
        frame(i / FPS * WARP).save(os.path.join(FR, f'f{i:04d}.png'))
        if i % 60 == 0: print('frame', i, '/', n, flush=True)
    mp4 = os.path.join(OUT, f'toyscout_{SLUG}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(FR, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', mp4], check=True)
    cover().save(os.path.join(OUT, f'cover_{SLUG}.jpg'), quality=92)
    shutil.rmtree(FR)
    print('wrote', mp4)
