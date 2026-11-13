#!/usr/bin/env python3
"""
Pokémon QR Hunt — builder
Run:  python3 build.py
Reads config below, then creates:
  site/        the website (upload this folder to GitHub Pages)
  print/       everything to print: hunt cards, Pokédex sheet, parent cheat sheet

Drop your own pictures in:
  images/<slug>.png|jpg      card + web picture for each Pokémon
  coloring/<slug>.png|jpg    coloring page for each Pokémon (goes in the prize PDF)
If a picture is missing, a labeled placeholder is used so everything still works.
"""
import os, shutil, html, json
from pathlib import Path

# ============================ CONFIG ============================
BASE_URL = "https://cervantesadolfo-droid.github.io/pokemon-hunt/"
PARTY_KID = "Trainer"                 # child's name, shown on the prize page
HIDING_WORD = "BACKYARD"              # 8 letters; where the final Master Ball code is hidden
PRIZE_SLUG = "master-ball-7x4k"       # final page (hard to guess on purpose)
POKEMON = [                           # order = card number = letter position
    ("pikachu",    "Pikachu",    "#F4D03F"),
    ("charmander", "Charmander", "#F39C5A"),
    ("squirtle",   "Squirtle",   "#6DB6E8"),
    ("bulbasaur",  "Bulbasaur",  "#7DCEA0"),
    ("charizard",  "Charizard",  "#E8743B"),
    ("eevee",      "Eevee",      "#C8A27A"),
    ("jigglypuff", "Jigglypuff", "#F5A9CF"),
    ("snorlax",    "Snorlax",    "#6C7A9C"),
]
# ================================================================

ROOT = Path(__file__).parent
SITE, PRINT = ROOT / "site", ROOT / "print"
IMAGES, COLORING = ROOT / "images", ROOT / "coloring"
assert len(HIDING_WORD) == len(POKEMON) == 8, "HIDING_WORD must have one letter per Pokémon"
BASE_URL = BASE_URL.rstrip("/") + "/"

from PIL import Image, ImageDraw, ImageFont
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def find_img(folder, slug):
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = folder / f"{slug}.{ext}"
        if p.exists():
            return p
    return None

def font(size, bold=False):
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def placeholder(name, color, size=(600, 600), text="Add picture"):
    im = Image.new("RGB", size, color)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 20, size[0]-20, size[1]-20], radius=40, outline="white", width=8)
    f1, f2 = font(56, True), font(30)
    w = d.textlength(name, font=f1); d.text(((size[0]-w)/2, size[1]/2-60), name, fill="white", font=f1)
    w = d.textlength(text, font=f2); d.text(((size[0]-w)/2, size[1]/2+20), text, fill="white", font=f2)
    return im

# ---------- reset output ----------
for d in (SITE, PRINT):
    shutil.rmtree(d, ignore_errors=True)
for d in (SITE/"catch", SITE/"prize", SITE/"img", SITE/"assets", PRINT/"qr", IMAGES, COLORING):
    d.mkdir(parents=True, exist_ok=True)

# ---------- images for web ----------
web_imgs = {}
for slug, name, color in POKEMON:
    src = find_img(IMAGES, slug)
    out = SITE/"img"/f"{slug}.png"
    (Image.open(src).convert("RGB") if src else placeholder(name, color)).save(out)
    web_imgs[slug] = out

# ---------- coloring pack PDF ----------
pack = SITE/"coloring-pack.pdf"
c = canvas.Canvas(str(pack), pagesize=letter)
W, H = letter
for slug, name, color in POKEMON:
    src = find_img(COLORING, slug)
    c.setFont("Helvetica-Bold", 22); c.drawCentredString(W/2, H-0.7*inch, f"{name}")
    c.setFont("Helvetica", 11); c.drawCentredString(W/2, H-0.95*inch, "Pokémon Hunt coloring page")
    box = (0.75*inch, 0.75*inch, W-1.5*inch, H-1.9*inch)
    if src:
        c.drawImage(str(src), *box, preserveAspectRatio=True, anchor="c")
    else:
        c.setDash(6, 4); c.rect(*box); c.setDash()
        c.setFont("Helvetica", 14)
        c.drawCentredString(W/2, H/2, f"Put {name} coloring page in coloring/{slug}.png and rerun build.py")
    c.showPage()
c.save()

# ---------- shared CSS ----------
CSS = """
:root{--red:#E3350D;--dark:#1b1f3b;--bg:#fff8e7}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--dark);text-align:center}
.wrap{max-width:480px;margin:0 auto;padding:24px 16px 48px}
.ball{width:56px;height:56px;border-radius:50%;background:linear-gradient(#E3350D 0 48%,#1b1f3b 48% 52%,#fff 52%);margin:0 auto 12px;position:relative}
.ball:after{content:"";position:absolute;left:50%;top:50%;width:16px;height:16px;border:4px solid #1b1f3b;border-radius:50%;background:#fff;transform:translate(-50%,-50%)}
h1{font-size:28px;margin:8px 0}.sub{font-size:18px;color:#555;margin:0 0 16px}
.card{background:#fff;border-radius:20px;padding:20px;box-shadow:0 8px 24px rgba(0,0,0,.08);margin:16px 0}
.card img{width:100%;max-width:300px;border-radius:16px}
.letter{font-size:96px;font-weight:900;line-height:1;margin:8px 0;color:var(--red)}
.hint{font-size:17px;line-height:1.4}.hint b{color:var(--red)}
.badge{display:inline-block;background:var(--dark);color:#fff;border-radius:999px;padding:6px 14px;font-size:14px;margin-top:12px}
.btn{display:block;width:100%;padding:16px;margin:12px 0;border-radius:14px;font-size:18px;font-weight:700;text-decoration:none;color:#fff;background:var(--red)}
.btn.alt{background:var(--dark)}
.prog{display:flex;gap:6px;justify-content:center;margin-top:14px;flex-wrap:wrap}.prog span{width:34px;height:34px;border-radius:50%;background:#eee;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}.prog span.on{background:#F4D03F}
.small{font-size:13px;color:#777;margin-top:20px}
.vid{width:100%;max-width:440px;border-radius:20px;box-shadow:0 8px 24px rgba(0,0,0,.15);background:#000}
"""
(SITE/"style.css").write_text(CSS)
for f in (ROOT/"assets").glob("*"): shutil.copy(f, SITE/"assets"/f.name)

PROGRESS_JS = """
<script>
(function(){
  var KEY='pokehunt_caught';var n=%d;var me=%s;var caught=[];
  try{caught=JSON.parse(localStorage.getItem(KEY)||'[]');if(me&&caught.indexOf(me)<0){caught.push(me);}localStorage.setItem(KEY,JSON.stringify(caught));}catch(e){}
  var el=document.getElementById('prog');if(!el)return;var h='';
  for(var i=1;i<=n;i++){h+='<span class="'+(caught.indexOf(i)>=0?'on':'')+'">'+i+'</span>';}
  el.innerHTML=h;var b=document.getElementById('count');if(b)b.textContent=caught.length+' of '+n+' caught on this phone';
})();
</script>"""

def page(title, body, me="null", n=len(POKEMON), depth=1):
    rel = "../" * depth
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<link rel="stylesheet" href="{rel}style.css"></head><body><div class="wrap">
<div class="ball"></div>{body}
<p class="small">Pokémon Hunt · scan the next card to keep going!</p></div>
{PROGRESS_JS % (n, me)}</body></html>"""

# ---------- catch pages ----------
for i, (slug, name, color) in enumerate(POKEMON, start=1):
    letter_ = HIDING_WORD[i-1]
    body = f"""
<h1>You caught {html.escape(name)}!</h1><p class="sub">Card #{i} of {len(POKEMON)}</p>
<div class="card"><img src="../img/{slug}.png" alt="{html.escape(name)}">
<p class="hint">Your secret letter is</p><div class="letter">{letter_}</div>
<p class="hint">Write <b>{letter_}</b> in blank <b>#{i}</b> on your Pokédex sheet.</p>
<div class="badge" id="count"></div><div class="prog" id="prog"></div></div>
<p class="hint">Catch all {len(POKEMON)} and the letters spell where the <b>Master Ball</b> is hiding!</p>"""
    (SITE/"catch"/f"{slug}.html").write_text(page(f"You caught {name}!", body, me=str(i)))

# ---------- prize page ----------
pack_url = BASE_URL + "coloring-pack.pdf"
subject = "Pokémon Hunt coloring pages"
mail_body = (f"Congratulations, Master Trainer!\n\nHere are the Pokémon coloring pages you earned at the party. "
             f"Open this link and print them:\n{pack_url}\n\nThanks for coming!")
from urllib.parse import quote
mailto = f"mailto:?subject={quote(subject)}&body={quote(mail_body)}"
body = f"""
<h1>MASTER TRAINER!</h1>
<video class="vid" autoplay muted loop playsinline poster="../assets/master-ball-poster.jpg" onclick="this.muted=!this.muted">
<source src="../assets/master-ball.mp4" type="video/mp4"></video>
<p class="small" style="margin:4px 0 12px">Tap the video for sound</p>
<div class="card"><p class="hint">You caught all {len(POKEMON)} Pokémon. Your prize: a coloring book of every Pokémon you found.</p>
<a class="btn" href="../coloring-pack.pdf" download="pokemon-coloring-pages.pdf">⬇ Download coloring pages</a>
<a class="btn alt" href="{html.escape(mailto)}">✉ Email them to me</a>
<p class="small">"Email them to me" opens your mail app with the link already written. Send it to yourself and print at home.</p></div>
<div class="card"><div class="badge" id="count"></div><div class="prog" id="prog"></div></div>"""
(SITE/"prize"/f"{PRIZE_SLUG}.html").write_text(page("Master Trainer!", body))

# ---------- landing page ----------
body = f"""<h1>Pokémon Hunt</h1><p class="sub">Scan any hidden card with your camera to start.</p>
<div class="card"><p class="hint">Find all {len(POKEMON)} Pokémon hidden around the house. Each one gives you a secret letter. The letters spell where the Master Ball is hiding!</p>
<div class="badge" id="count"></div><div class="prog" id="prog"></div></div>"""
(SITE/"index.html").write_text(page("Pokémon Hunt", body, depth=0))
(SITE/".nojekyll").write_text("")

# ---------- QR codes ----------
def qr(url, path):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=4)
    q.add_data(url); q.make(fit=True)
    q.make_image(fill_color="black", back_color="white").save(path)

links = []
for i, (slug, name, color) in enumerate(POKEMON, start=1):
    url = f"{BASE_URL}catch/{slug}.html"; p = PRINT/"qr"/f"{i:02d}-{slug}.png"; qr(url, p); links.append((i, name, url, p))
prize_url = f"{BASE_URL}prize/{PRIZE_SLUG}.html"; prize_qr = PRINT/"qr"/"09-master-ball.png"; qr(prize_url, prize_qr)

# ---------- hunt cards PDF (2 per page, 4 x 6.5 in each) ----------
c = canvas.Canvas(str(PRINT/"hunt-cards.pdf"), pagesize=letter)
CW, CH = 3.9*inch, 6.6*inch
slots = [((W-2*CW-0.4*inch)/2, H-CH-0.9*inch), ((W-2*CW-0.4*inch)/2+CW+0.4*inch, H-CH-0.9*inch)]
def draw_card(x, y, num, name, color, img, qrp):
    c.setStrokeColor(colors.HexColor("#1b1f3b")); c.setLineWidth(2)
    c.roundRect(x, y, CW, CH, 18, stroke=1, fill=0)
    c.setFillColor(colors.HexColor("#E3350D")); c.roundRect(x, y+CH-0.55*inch, CW, 0.55*inch, 18, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 16); c.drawCentredString(x+CW/2, y+CH-0.37*inch, (f"#{num}  {name}" if isinstance(num,int) else f"{num}  {name}"))
    c.setFillColor(colors.black)
    c.drawImage(str(img), x+0.3*inch, y+CH-0.55*inch-3.1*inch, CW-0.6*inch, 2.9*inch, preserveAspectRatio=True, anchor="c")
    c.setFont("Helvetica-Bold", 13); c.drawCentredString(x+CW/2, y+2.65*inch, "SCAN ME to catch!")
    c.drawImage(str(qrp), x+(CW-2.3*inch)/2, y+0.3*inch, 2.3*inch, 2.3*inch)
for i, (slug, name, color) in enumerate(POKEMON, start=1):
    x, y = slots[(i-1) % 2]
    draw_card(x, y, i, name, color, web_imgs[slug], links[i-1][3])
    if i % 2 == 0: c.showPage()
# master ball card
x, y = slots[0]
mb = placeholder("MASTER BALL", "#5b3fa0", text="Final prize!"); mb_path = PRINT/"qr"/"masterball-art.png"; mb.save(mb_path)
draw_card(x, y, "FINAL", "Master Ball", "#5b3fa0", mb_path, prize_qr)
c.setFont("Helvetica", 11); c.drawString(slots[1][0], slots[1][1]+CH-0.4*inch, "Hide the Master Ball card at:")
c.setFont("Helvetica-Bold", 28); c.drawString(slots[1][0], slots[1][1]+CH-0.9*inch, HIDING_WORD)
c.setFont("Helvetica", 11)
for j, line in enumerate(["Cut out all 9 cards. Tape cards #1–#8 at kid eye level",
                          "in different rooms. Tape the Master Ball card at the",
                          "place the word spells. Scan one with your phone to",
                          "test before guests arrive."]):
    c.drawString(slots[1][0], slots[1][1]+CH-1.3*inch-j*0.22*inch, line)
c.showPage(); c.save()

# ---------- Pokédex sheet (one per kid) ----------
c = canvas.Canvas(str(PRINT/"pokedex-sheet.pdf"), pagesize=letter)
c.setFillColor(colors.HexColor("#E3350D")); c.rect(0, H-1.2*inch, W, 1.2*inch, stroke=0, fill=1)
c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 30); c.drawCentredString(W/2, H-0.75*inch, "MY POKÉDEX")
c.setFillColor(colors.black); c.setFont("Helvetica", 14); c.drawString(0.8*inch, H-1.7*inch, "Trainer name: ________________________________")
c.setFont("Helvetica", 12); c.drawString(0.8*inch, H-2.1*inch, "Find each Pokémon, scan its card, and write the secret letter in its box.")
top = H-2.7*inch
for i, (slug, name, color) in enumerate(POKEMON, start=1):
    y = top - (i-1)*0.78*inch
    c.setStrokeColor(colors.HexColor("#1b1f3b")); c.setLineWidth(1.5)
    c.rect(0.8*inch, y-0.5*inch, 0.5*inch, 0.5*inch)      # checkbox
    c.setFont("Helvetica-Bold", 16); c.drawString(1.5*inch, y-0.35*inch, f"#{i}  {name}")
    c.setLineWidth(2); c.rect(W-2.2*inch, y-0.6*inch, 0.7*inch, 0.7*inch)   # letter box
    if i == 1: c.setFont("Helvetica", 9); c.drawString(W-2.2*inch, y+0.15*inch, "secret letter")
y = top - 8*0.78*inch - 0.3*inch
c.setFont("Helvetica-Bold", 14); c.drawString(0.8*inch, y, "The letters spell a hiding place:")
c.setLineWidth(2)
for i in range(8):
    c.rect(0.8*inch + i*0.8*inch, y-1.0*inch, 0.65*inch, 0.65*inch)
c.setFont("Helvetica", 12); c.drawString(0.8*inch, y-1.4*inch, "Go there to find the MASTER BALL and scan it for your prize!")
c.save()

# ---------- parent cheat sheet ----------
c = canvas.Canvas(str(PRINT/"parent-cheat-sheet.pdf"), pagesize=letter)
c.setFont("Helvetica-Bold", 20); c.drawString(0.8*inch, H-0.9*inch, "Parent cheat sheet (don't let the kids see!)")
c.setFont("Helvetica", 11); y = H-1.4*inch
lines = [f"Hiding word: {HIDING_WORD}   →  hide the Master Ball card there.", f"Website: {BASE_URL}", ""]
for i, name, url, p in links:
    lines.append(f"#{i}  {name:<12} letter {HIDING_WORD[i-1]}   {url}")
lines += ["", f"Master Ball (prize):  {prize_url}", f"Coloring pack:  {pack_url}", "",
          "If a phone won't scan: tell the kid the letter from this list.",
          "The prize page has a Download button and an 'Email them to me' button",
          "(opens the parent's mail app with the link already written).",
          "Any phone camera scans these; no app needed. Hold 1–2 ft away, avoid glare."]
for line in lines:
    c.drawString(0.8*inch, y, line); y -= 0.26*inch
c.save()

manifest = {"base_url": BASE_URL, "hiding_word": HIDING_WORD, "prize_url": prize_url, "pack_url": pack_url,
            "catch_urls": {name: url for i, name, url, p in links}}
(ROOT/"manifest.json").write_text(json.dumps(manifest, indent=2))
print("Built. Site →", SITE, " Printables →", PRINT)
print(json.dumps(manifest, indent=2))
