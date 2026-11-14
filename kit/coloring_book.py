"""Zeke's Birthday Pokémon Coloring Book — 10 pages, US Letter."""
import math, random
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image

ROOT = Path(__file__).parent
OUT = ROOT / "site" / "coloring-pack.pdf"
KID, AGE = "Zeke", 7
POKEMON = ["pikachu","charmander","squirtle","bulbasaur","charizard","eevee","jigglypuff","snorlax"]
NAMES = {p: p.capitalize() for p in POKEMON}
W, H = letter
INK = colors.black
LIGHT = colors.Color(0.55, 0.55, 0.55)   # thin outline for background doodles

random.seed(7)
c = canvas.Canvas(str(OUT), pagesize=letter)
c.setTitle(f"{KID}'s Birthday Pokémon Coloring Book")

# ---------- outline doodles (all colorable) ----------
def pokeball(x, y, r):
    c.circle(x, y, r); c.line(x-r, y, x+r, y); c.circle(x, y, r*0.3); c.circle(x, y, r*0.14)
def balloon(x, y, r):
    c.ellipse(x-r, y-r*1.2, x+r, y+r*1.2)
    c.line(x-r*0.25, y-r*1.2, x+r*0.25, y-r*1.2); c.line(x, y-r*1.2, x, y-r*1.2-4)
    p = c.beginPath(); p.moveTo(x, y-r*1.2-4)
    for k in range(1, 7): p.lineTo(x + (6 if k % 2 else -6), y-r*1.2-4-k*9)
    c.drawPath(p, stroke=1, fill=0)
def star(x, y, r):
    p = c.beginPath()
    for k in range(10):
        a = math.pi/2 + k*math.pi/5; rr = r if k % 2 == 0 else r*0.45
        (p.moveTo if k == 0 else p.lineTo)(x+rr*math.cos(a), y+rr*math.sin(a))
    p.close(); c.drawPath(p, stroke=1, fill=0)
def confetti(x, y, s, rot):
    c.saveState(); c.translate(x, y); c.rotate(rot); c.rect(-s/2, -s/4, s, s/2); c.restoreState()
def hat(x, y, s):
    p = c.beginPath(); p.moveTo(x-s*0.5, y); p.lineTo(x+s*0.5, y); p.lineTo(x, y+s*1.3); p.close()
    c.drawPath(p, stroke=1, fill=0); c.circle(x, y+s*1.3, s*0.12); c.line(x-s*0.3, y+s*0.5, x+s*0.3, y+s*0.5)
def cupcake(x, y, s):
    p = c.beginPath(); p.moveTo(x-s*0.5, y+s*0.5); p.lineTo(x-s*0.35, y); p.lineTo(x+s*0.35, y); p.lineTo(x+s*0.5, y+s*0.5); p.close()
    c.drawPath(p, stroke=1, fill=0)
    c.arc(x-s*0.55, y+s*0.3, x+s*0.55, y+s*0.9, 0, 180)
    c.circle(x, y+s*0.95, s*0.1); c.line(x, y+s*1.05, x, y+s*1.3); c.ellipse(x-3, y+s*1.3, x+3, y+s*1.45)
def gift(x, y, s):
    c.rect(x-s/2, y, s, s*0.8); c.rect(x-s/2-3, y+s*0.8, s+6, s*0.2); c.line(x, y, x, y+s)
    c.ellipse(x-s*0.3, y+s, x, y+s*1.2); c.ellipse(x, y+s, x+s*0.3, y+s*1.2)

DOODLES = [pokeball, balloon, star, hat, cupcake, gift]

def party_background(*avoids):
    """Scatter outline party doodles around the page, skipping the avoid box (x0,y0,x1,y1)."""
    c.saveState(); c.setStrokeColor(LIGHT); c.setLineWidth(1.1)
    placed = []
    tries = 0
    while len(placed) < 26 and tries < 2000:
        tries += 1
        x, y = random.uniform(0.5*inch, W-0.5*inch), random.uniform(0.5*inch, H-0.5*inch)
        s = random.uniform(16, 30)
        if any(a[0]-s < x < a[2]+s and a[1]-s < y < a[3]+s for a in avoids): continue
        if any(math.hypot(x-px, y-py) < s+ps+10 for px, py, ps in placed): continue
        random.choice(DOODLES)(x, y, s); placed.append((x, y, s))
    for _ in range(40):
        x, y = random.uniform(0.4*inch, W-0.4*inch), random.uniform(0.4*inch, H-0.4*inch)
        if any(a[0]-10 < x < a[2]+10 and a[1]-10 < y < a[3]+10 for a in avoids): continue
        confetti(x, y, random.uniform(7, 12), random.uniform(0, 180))
    c.restoreState()

def frame(x0, y0, x1, y1):
    c.saveState(); c.setStrokeColor(INK); c.setLineWidth(3); c.roundRect(x0, y0, x1-x0, y1-y0, 18); c.restoreState()

def bunting(y):
    c.saveState(); c.setStrokeColor(INK); c.setLineWidth(1.5)
    c.bezier(0.4*inch, y, W*0.3, y-28, W*0.7, y-28, W-0.4*inch, y)
    n = 11
    for k in range(n):
        t = (k+0.5)/n
        bx = 0.4*inch + t*(W-0.8*inch)
        by = y - 28*3*t*(1-t)   # approx bezier dip
        p = c.beginPath()
        p.moveTo(bx-13, by); p.lineTo(bx+13, by); p.lineTo(bx, by-26); p.close(); c.drawPath(p, stroke=1, fill=0)
    c.restoreState()

def header(text, size=30, y=H-1.05*inch):
    c.saveState(); c.setFillColor(INK); c.setFont("Helvetica-Bold", size); c.drawCentredString(W/2, y, text); c.restoreState()

# ================= PAGE 1 — COVER =================
box = (1.0*inch, 2.3*inch, W-1.0*inch, H-3.0*inch)
party_background((0.7*inch, 2.2*inch, W-0.7*inch, H-1.0*inch), (1.2*inch, 0.5*inch, W-1.2*inch, 2.2*inch))
bunting(H-0.55*inch)
header(f"{KID.upper()}'S", 44, H-1.75*inch)
header("BIRTHDAY", 44, H-2.35*inch)
header("Pokémon Coloring Book", 22, H-2.8*inch)
frame(*box)
# cover collage: 4 pokemon in a 2x2 grid
cells = [("pikachu", 0, 1), ("charmander", 1, 1), ("squirtle", 0, 0), ("bulbasaur", 1, 0)]
cw, ch = (box[2]-box[0])/2, (box[3]-box[1])/2
for slug, cx, cy in cells:
    c.drawImage(str(ROOT/"lineart"/f"{slug}.png"), box[0]+cx*cw+10, box[1]+cy*ch+10, cw-20, ch-20, preserveAspectRatio=True, anchor="c", mask="auto")
c.setFont("Helvetica-Bold", 26); c.drawCentredString(W/2, 1.75*inch, f"{KID} turns {AGE}!")
c.setFont("Helvetica", 14); c.drawCentredString(W/2, 1.35*inch, "This book belongs to: ______________________________")
c.setFont("Helvetica", 11); c.drawCentredString(W/2, 0.7*inch, "Color every Pokémon you caught at the party!")
c.showPage()

# ================= PAGES 2–9 — ONE POKÉMON + ONE ACTIVITY EACH =================
from activities import ACTIVITIES
for i, slug in enumerate(POKEMON, start=1):
    instr, draw = ACTIVITIES[slug]
    badge = (0.7*inch, H-3.1*inch, 3.3*inch, H-0.9*inch)          # small Pokémon, top-left
    act = (0.8*inch, 1.2*inch, W-0.8*inch, H-3.35*inch)           # activity area
    party_background(act, badge, (3.3*inch, H-3.1*inch, W-0.6*inch, H-0.9*inch), (1.2*inch, 0.5*inch, W-1.2*inch, 1.2*inch))
    bunting(H-0.5*inch)
    # badge
    c.saveState(); c.setLineWidth(2); c.roundRect(badge[0], badge[1], badge[2]-badge[0], badge[3]-badge[1], 14); c.restoreState()
    c.drawImage(str(ROOT/"lineart"/f"{slug}.png"), badge[0]+8, badge[1]+8, badge[2]-badge[0]-16, badge[3]-badge[1]-16, preserveAspectRatio=True, anchor="c", mask="auto")
    # title + instruction to the right of the badge
    c.setFont("Helvetica-Bold", 28); c.drawString(3.5*inch, H-1.55*inch, f"#{i}  {NAMES[slug]}")
    c.setFont("Helvetica-Bold", 13); c.drawString(3.5*inch, H-2.0*inch, "ACTIVITY:")
    c.setFont("Helvetica", 12.5)
    # wrap instruction
    words, line, y = instr.split(), "", H-2.3*inch
    for w in words:
        if c.stringWidth(line+" "+w, "Helvetica", 12.5) > W-3.5*inch-0.7*inch: c.drawString(3.5*inch, y, line); line, y = w, y-17
        else: line = (line+" "+w).strip()
    c.drawString(3.5*inch, y, line)
    frame(*act)
    c.saveState(); c.setStrokeColor(INK); c.setFillColor(INK)
    draw(c, (act[0]+22, act[1]+22, act[2]-22, act[3]-22))
    c.restoreState()
    c.setFont("Helvetica-Bold", 14); c.drawCentredString(W/2, 0.9*inch, f"Happy {AGE}th Birthday, {KID}!")
    c.setFont("Helvetica", 10); c.drawCentredString(W/2, 0.62*inch, f"Caught at {KID}'s Pokémon Hunt  ·  Page {i+1} of 10")
    c.showPage()

# ================= PAGE 10 — MASTER TRAINER CERTIFICATE =================
party_background((0.9*inch, 1.2*inch, W-0.9*inch, H-1.0*inch))
c.saveState(); c.setLineWidth(4); c.roundRect(0.7*inch, 0.9*inch, W-1.4*inch, H-1.8*inch, 24)
c.setLineWidth(1.5); c.roundRect(0.85*inch, 1.05*inch, W-1.7*inch, H-2.1*inch, 18); c.restoreState()
c.saveState(); c.setLineWidth(2.5); pokeball(W/2, H-1.75*inch, 0.45*inch); c.restoreState()
header("OFFICIAL", 16, H-2.55*inch)
header("MASTER TRAINER", 34, H-3.05*inch)
header("CERTIFICATE", 34, H-3.55*inch)
c.setFont("Helvetica", 14); c.drawCentredString(W/2, H-4.3*inch, "This certifies that")
c.setLineWidth(1.5); c.line(1.6*inch, H-5.05*inch, W-1.6*inch, H-5.05*inch)
c.setFont("Helvetica", 10); c.drawCentredString(W/2, H-5.25*inch, "trainer name")
c.setFont("Helvetica", 14)
c.drawCentredString(W/2, H-5.8*inch, f"caught all 8 Pokémon at {KID}'s {AGE}th Birthday Hunt")
c.drawCentredString(W/2, H-6.1*inch, "and found the Master Ball!")
# mini lineup of all 8
y0, size = 2.5*inch, 0.85*inch
for k, slug in enumerate(POKEMON):
    x = 1.0*inch + k*((W-2.0*inch)/8)
    c.drawImage(str(ROOT/"lineart"/f"{slug}.png"), x, y0, (W-2.0*inch)/8-6, size, preserveAspectRatio=True, anchor="c", mask="auto")
c.setFont("Helvetica", 11)
c.line(1.3*inch, 1.7*inch, 3.6*inch, 1.7*inch); c.drawCentredString(2.45*inch, 1.5*inch, "Date")
c.line(W-3.6*inch, 1.7*inch, W-1.3*inch, 1.7*inch); c.drawCentredString(W-2.45*inch, 1.5*inch, f"Signed, {KID}'s Dad (Gym Leader)")
c.save()
print("wrote", OUT)
