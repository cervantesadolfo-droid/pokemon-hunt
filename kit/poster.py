"""Door poster: game-world background, wooden signs, Pokémon cutouts. Imported by build.py."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image

W, H = letter
WOOD, WOOD_DK, PLANK = colors.HexColor("#B9803F"), colors.HexColor("#7A4E22"), colors.HexColor("#E8C98F")
RED, NAVY, YEL = colors.HexColor("#E3350D"), colors.HexColor("#1b1f3b"), colors.HexColor("#F7D23E")

def outlined(c, x, y, text, size, fill, stroke=NAVY, width=2.2, font="Helvetica-Bold"):
    c.saveState(); c.setFont(font, size); c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(width)
    t = c.beginText(); t.setTextRenderMode(2); t.setFont(font, size)
    t.setTextOrigin(x - c.stringWidth(text, font, size)/2, y); t.textOut(text); c.drawText(t); c.restoreState()

def sign(c, x, y, w, h, posts=True):
    """Wooden sign board with two posts."""
    c.saveState()
    if posts:
        c.setFillColor(WOOD_DK); c.rect(x+0.35*inch, y-0.5*inch, 0.22*inch, 0.6*inch, stroke=0, fill=1); c.rect(x+w-0.57*inch, y-0.5*inch, 0.22*inch, 0.6*inch, stroke=0, fill=1)
    c.setFillColor(WOOD_DK); c.roundRect(x-4, y-4, w+8, h+8, 14, stroke=0, fill=1)
    c.setFillColor(WOOD); c.roundRect(x, y, w, h, 12, stroke=0, fill=1)
    c.setFillColor(PLANK); c.roundRect(x+8, y+8, w-16, h-16, 9, stroke=0, fill=1)
    c.setStrokeColor(WOOD); c.setLineWidth(1)
    for k in range(1, 4): c.line(x+14, y+8+(h-16)*k/4, x+w-14, y+8+(h-16)*k/4)   # plank lines
    c.setFillColor(WOOD_DK)
    for px, py in ((x+14, y+h-14), (x+w-14, y+h-14), (x+14, y+14), (x+w-14, y+14)): c.circle(px, py, 3, stroke=0, fill=1)
    c.restoreState()

def banner(c, cx, cy, w, h, text, size=19):
    c.saveState(); c.setFillColor(RED); c.setStrokeColor(NAVY); c.setLineWidth(2)
    c.roundRect(cx-w/2, cy-h/2, w, h, 8, stroke=1, fill=1)
    p = c.beginPath()   # ribbon tails
    for s in (-1, 1):
        x0 = cx + s*w/2
        p.moveTo(x0, cy+h/2-4); p.lineTo(x0+s*0.35*inch, cy+h/2-4); p.lineTo(x0+s*0.18*inch, cy); p.lineTo(x0+s*0.35*inch, cy-h/2+4); p.lineTo(x0, cy-h/2+4); p.close()
    c.setFillColor(colors.HexColor("#B22A0A")); c.drawPath(p, stroke=1, fill=1)
    c.setFillColor(RED); c.roundRect(cx-w/2, cy-h/2, w, h, 8, stroke=1, fill=1)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", size); c.drawCentredString(cx, cy-size*0.36, text)
    c.restoreState()

def pokeball(c, x, y, r):
    c.saveState(); c.setLineWidth(2); c.setStrokeColor(NAVY)
    c.setFillColor(RED); c.wedge(x-r, y-r, x+r, y+r, 0, 180, stroke=0, fill=1)
    c.setFillColor(colors.white); c.wedge(x-r, y-r, x+r, y+r, 180, 180, stroke=0, fill=1)
    c.circle(x, y, r, stroke=1, fill=0); c.line(x-r, y, x+r, y)
    c.setFillColor(colors.white); c.circle(x, y, r*0.32, stroke=1, fill=1); c.setFillColor(NAVY); c.circle(x, y, r*0.13, stroke=0, fill=1)
    c.restoreState()

def draw_poster(path, *, kid, n, bg_png, qr_png, cutouts, prize_spot):
    c = canvas.Canvas(str(path), pagesize=letter)
    # background: fill the page, crop from the top of the scene
    bw, bh = Image.open(bg_png).size; scale = W/bw
    c.drawImage(str(bg_png), 0, H-bh*scale, W, bh*scale)
    # soft sky band so the title pops
    c.saveState(); c.setFillColor(colors.Color(1, 1, 1, alpha=0.35)); c.rect(0, H-2.45*inch, W, 2.45*inch, stroke=0, fill=1); c.restoreState()
    # title
    outlined(c, W/2, H-1.05*inch, f"{kid.upper()}'S", 46, YEL, width=2.6)
    outlined(c, W/2, H-1.75*inch, "POKÉMON HUNT", 46, YEL, width=2.6)
    pokeball(c, 0.9*inch, H-1.3*inch, 0.42*inch); pokeball(c, W-0.9*inch, H-1.3*inch, 0.42*inch)
    banner(c, W/2, H-2.35*inch, 5.6*inch, 0.55*inch, "REGISTER HERE TO START YOUR CLOCK")
    # QR sign
    sx, sy, sw, sh = W/2-2.35*inch, H-6.75*inch, 4.7*inch, 4.1*inch
    sign(c, sx, sy, sw, sh)
    c.setFillColor(colors.white); c.roundRect(W/2-1.55*inch, sy+sh-0.35*inch-3.1*inch, 3.1*inch, 3.1*inch, 10, stroke=0, fill=1)
    c.drawImage(str(qr_png), W/2-1.45*inch, sy+sh-0.4*inch-3.0*inch, 2.9*inch, 2.9*inch)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 15); c.drawCentredString(W/2, sy+0.42*inch, "Parents: scan with your phone camera,")
    c.setFont("Helvetica", 13); c.drawCentredString(W/2, sy+0.2*inch, "type your trainer's name, tap  Start the clock!")
    # rules sign
    rx, ry, rw, rh = 0.55*inch, 0.55*inch, W-1.1*inch, 2.75*inch
    sign(c, rx, ry, rw, rh, posts=False)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 16); c.drawString(rx+0.3*inch, ry+rh-0.42*inch, "HOW TO PLAY")
    c.setFont("Helvetica-Bold", 11.5)
    rules = [f"{n} Pokémon cards are hidden around the house.",
             "Find one and scan its QR code with the SAME phone you registered on.",
             "Every scan catches that Pokémon and shows your running time.",
             f"Catch all {n} and your clock stops. The prize screen appears!",
             f"Show it to {kid}'s Dad in the {prize_spot.lower()}. Fastest trainers win a prize!"]
    y = ry+rh-0.78*inch
    for i, r in enumerate(rules, 1):
        c.setFillColor(RED); c.circle(rx+0.42*inch, y+4, 8, stroke=0, fill=1)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 10); c.drawCentredString(rx+0.42*inch, y+0.5, str(i))
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 11.5); c.drawString(rx+0.65*inch, y, r); y -= 0.36*inch
    c.setFont("Helvetica-Oblique", 9.5); c.drawCentredString(W/2, ry+0.17*inch, "No app needed. Any phone camera reads the codes. One registration per phone (teams welcome).")
    # Pokémon cutouts around the signs
    def put(slug, x, y, w, flip=False):
        im = Image.open(cutouts/f"{slug}.png"); h = w*im.height/im.width
        c.saveState()
        if flip: c.translate(x+w, 0); c.scale(-1, 1); x = 0
        c.drawImage(str(cutouts/f"{slug}.png"), x, y, w, h, mask="auto"); c.restoreState()
    put("pikachu",    -0.05*inch, 3.2*inch, 1.75*inch)
    put("squirtle",   W-1.85*inch, 3.25*inch, 1.75*inch, flip=True)
    put("charmander", W-1.85*inch, 5.6*inch, 1.5*inch)
    put("bulbasaur",  0.05*inch, 5.55*inch, 1.65*inch)
    put("eevee",      0.2*inch, 7.55*inch, 1.1*inch)
    put("jigglypuff", W-1.25*inch, 7.45*inch, 1.05*inch)
    c.save()
