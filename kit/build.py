#!/usr/bin/env python3
"""
Zeke's Pokémon QR Hunt — builder (v2: registration + timer + leaderboard)
Run:  python3 build.py
Creates:
  site/    the website (GitHub Pages)
  print/   door poster, 8 hunt cards, Pokédex checklist, admin card, parent cheat sheet

Images:  images/<slug>.png      Videos: assets/<slug>.mp4     Activity book: activity-book.pdf
"""
import os, shutil, html, json
from pathlib import Path
from urllib.parse import quote

# ============================ CONFIG ============================
BASE_URL   = "https://cervantesadolfo-droid.github.io/pokemon-hunt/"
KID        = "Zeke"
PRIZE_SLUG = "master-ball-7x4k"      # prize page (not linked publicly; reached after 8 catches)
ADMIN_SLUG = "gym-leader-9q2v"       # Dad's leaderboard page (keep this one to yourself)
PRIZE_SPOT = "BACKYARD"              # where Zeke's Dad hands out the real prize
POKEMON = [
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
SITE, PRINT, IMAGES, ASSETS = ROOT/"site", ROOT/"print", ROOT/"images", ROOT/"assets"
BASE_URL = BASE_URL.rstrip("/") + "/"
N = len(POKEMON)

from PIL import Image, ImageDraw, ImageFont
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def find_img(folder, slug):
    for ext in ("png", "jpg", "jpeg", "webp"):
        if (folder/f"{slug}.{ext}").exists(): return folder/f"{slug}.{ext}"
def font(size, bold=False):
    f = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(f, size) if os.path.exists(f) else ImageFont.load_default()
def placeholder(name, color, size=(600, 600), text="Add picture"):
    im = Image.new("RGB", size, color); d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 20, size[0]-20, size[1]-20], radius=40, outline="white", width=8)
    f1, f2 = font(56, True), font(30)
    w = d.textlength(name, font=f1); d.text(((size[0]-w)/2, size[1]/2-60), name, fill="white", font=f1)
    w = d.textlength(text, font=f2); d.text(((size[0]-w)/2, size[1]/2+20), text, fill="white", font=f2)
    return im

# ---------- reset ----------
for d in (SITE, PRINT): shutil.rmtree(d, ignore_errors=True)
for d in (SITE/"catch", SITE/"prize", SITE/"admin", SITE/"img", SITE/"assets", PRINT/"qr", IMAGES, ASSETS): d.mkdir(parents=True, exist_ok=True)
for f in ASSETS.glob("*"): shutil.copy(f, SITE/"assets"/f.name)
if (ROOT/"activity-book.pdf").exists(): shutil.copy(ROOT/"activity-book.pdf", SITE/"coloring-pack.pdf")
(SITE/".nojekyll").write_text("")

web_imgs = {}
for slug, name, color in POKEMON:
    src = find_img(IMAGES, slug); out = SITE/"img"/f"{slug}.png"
    (Image.open(src).convert("RGB") if src else placeholder(name, color)).save(out); web_imgs[slug] = out

# ---------- CSS ----------
(SITE/"style.css").write_text("""
:root{--red:#E3350D;--dark:#1b1f3b;--bg:#7CC55A;--yellow:#F4D03F}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg) center top/480px auto repeat-y;color:var(--dark);text-align:center;min-height:100vh}
.wrap{max-width:480px;margin:0 auto;padding:24px 16px 48px}
.ball{width:56px;height:56px;border-radius:50%;background:linear-gradient(#E3350D 0 48%,#1b1f3b 48% 52%,#fff 52%);margin:0 auto 12px;position:relative;box-shadow:0 4px 10px rgba(0,0,0,.25)}
.ball:after{content:"";position:absolute;left:50%;top:50%;width:16px;height:16px;border:4px solid #1b1f3b;border-radius:50%;background:#fff;transform:translate(-50%,-50%)}
h1{font-size:28px;margin:8px 0}.sub{font-size:18px;margin:0 0 16px}h1,.sub{text-shadow:0 2px 0 rgba(255,255,255,.9),0 0 14px rgba(255,255,255,.9)}
.card{background:rgba(255,255,255,.94);border-radius:20px;padding:20px;box-shadow:0 8px 24px rgba(0,0,0,.18);margin:16px 0}
.card img{width:100%;max-width:300px;border-radius:16px}
.vid{width:100%;max-width:440px;border-radius:20px;box-shadow:0 8px 24px rgba(0,0,0,.15);background:#000}
.hint{font-size:17px;line-height:1.4}.hint b{color:var(--red)}
.badge{display:inline-block;background:var(--dark);color:#fff;border-radius:999px;padding:6px 14px;font-size:14px;margin-top:12px}
.btn{display:block;width:100%;padding:16px;margin:12px 0;border:0;border-radius:14px;font-size:18px;font-weight:700;text-decoration:none;color:#fff;background:var(--red);cursor:pointer}
.btn.alt{background:var(--dark)}.btn.gold{background:var(--yellow);color:var(--dark)}
.prog{display:flex;gap:6px;justify-content:center;margin-top:14px;flex-wrap:wrap}.prog span{width:34px;height:34px;border-radius:50%;background:#eee;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}.prog span.on{background:var(--yellow)}
.small{font-size:13px;color:var(--dark);background:rgba(255,255,255,.7);display:inline-block;padding:4px 10px;border-radius:999px;margin-top:20px}
.timer{font-variant-numeric:tabular-nums;font-size:40px;font-weight:900;letter-spacing:1px;color:var(--dark);margin:6px 0}
.timer.done{color:#1a8f3c}
input.name{width:100%;font-size:20px;padding:14px;border:2px solid #ccc;border-radius:12px;text-align:center}
.steps{text-align:left;font-size:16px;line-height:1.5;padding-left:22px;margin:8px 0}
.hidden{display:none !important}
table{width:100%;border-collapse:collapse;font-size:16px}td,th{padding:8px 6px;border-bottom:1px solid #eee;text-align:left}th{font-size:13px;color:#666}td.t{font-variant-numeric:tabular-nums;font-weight:700}
.rank{font-weight:900;color:var(--red);width:30px}
""")

# ---------- shared JS ----------
(SITE/"hunt.js").write_text(f"""
var HUNT = (function(){{
  var KEY='pokehunt_v2', N={N};
  function load(){{ try{{ return JSON.parse(localStorage.getItem(KEY)||'{{}}'); }}catch(e){{ return {{}}; }} }}
  function save(s){{ try{{ localStorage.setItem(KEY, JSON.stringify(s)); }}catch(e){{}} }}
  function pad(n){{ return (n<10?'0':'')+n; }}
  function fmt(ms){{ ms=Math.max(0,ms|0); var s=Math.floor(ms/1000); var m=Math.floor(s/60); return pad(m)+':'+pad(s%60); }}
  function caught(s){{ return Object.keys(s.caught||{{}}).length; }}
  function register(name){{ var s={{name:name, start:Date.now(), caught:{{}}}}; save(s); return s; }}
  function catchOne(i){{ var s=load(); if(!s.start) return null; s.caught=s.caught||{{}}; if(!s.caught[i]) s.caught[i]=Date.now();
    if(caught(s)>=N && !s.end) s.end=Math.max.apply(null, Object.keys(s.caught).map(function(k){{return s.caught[k];}}));
    save(s); return s; }}
  function elapsed(s){{ return (s.end||Date.now())-s.start; }}
  function renderProg(s){{ var el=document.getElementById('prog'); if(!el) return; var h='';
    for(var i=1;i<=N;i++) h+='<span class="'+((s.caught||{{}})[i]?'on':'')+'">'+i+'</span>'; el.innerHTML=h;
    var b=document.getElementById('count'); if(b) b.textContent=caught(s)+' of '+N+' caught'; }}
  function tick(s){{ var t=document.getElementById('timer'); if(!t) return; function f(){{ t.textContent=fmt(elapsed(s)); if(s.end) t.className='timer done'; }} f(); if(!s.end) setInterval(f,1000); }}
  function entry(s){{ return btoa(unescape(encodeURIComponent(JSON.stringify({{n:s.name,s:s.start,e:s.end}})))); }}
  return {{load:load,save:save,fmt:fmt,caught:caught,register:register,catchOne:catchOne,elapsed:elapsed,renderProg:renderProg,tick:tick,entry:entry,N:N}};
}})();
""")

def page(title, body, depth=1, extra_js="", head=""):
    rel = "../"*depth
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<link rel="stylesheet" href="{rel}style.css"><style>body{{background-image:url({rel}assets/bg.svg)}}</style>{head}</head>
<body><div class="wrap"><div class="ball"></div>{body}
<p class="small">{KID}'s Pokémon Hunt</p></div>
<script src="{rel}hunt.js"></script><script>{extra_js}</script></body></html>"""

prize_url = f"{BASE_URL}prize/{PRIZE_SLUG}.html"
admin_url = f"{BASE_URL}admin/{ADMIN_SLUG}.html"
reg_url   = f"{BASE_URL}register.html"
pack_url  = f"{BASE_URL}coloring-pack.pdf"

# ---------- landing ----------
(SITE/"index.html").write_text(page(f"{KID}'s Pokémon Hunt", f"""
<h1>{KID}'s Pokémon Hunt</h1><p class="sub">Gotta catch 'em all... fast!</p>
<div class="card" id="unreg"><p class="hint">Scan the <b>REGISTER</b> poster at the door to start your clock.</p>
<a class="btn" href="register.html">Register now</a></div>
<div class="card hidden" id="reg"><p class="hint">Trainer <b id="who"></b></p><div class="timer" id="timer">00:00</div>
<div class="badge" id="count"></div><div class="prog" id="prog"></div>
<p class="hint" style="margin-top:14px">Find the hidden cards and scan each one!</p></div>
""", depth=0, extra_js="""
var s=HUNT.load(); if(s.start){document.getElementById('unreg').classList.add('hidden');document.getElementById('reg').classList.remove('hidden');
document.getElementById('who').textContent=s.name;HUNT.renderProg(s);HUNT.tick(s);}"""))

# ---------- register ----------
(SITE/"register.html").write_text(page("Register", f"""
<h1>Welcome, Trainer!</h1><p class="sub">Register to start the hunt</p>
<div class="card" id="form">
<ol class="steps"><li><b>{N} Pokémon cards</b> are hidden around the house.</li>
<li>Scan each card's QR code with <b>this phone</b> to catch it.</li>
<li>Your clock starts <b>now</b> and stops when you catch the last one.</li>
<li>Fastest trainers win a prize from {KID}'s Dad!</li></ol>
<input class="name" id="name" placeholder="Trainer name (or team name)" maxlength="30" autocomplete="off">
<button class="btn" onclick="go()">Start the clock!</button>
<p class="hint" style="font-size:14px">One registration per phone. Siblings sharing a phone can register as a team.</p></div>
<div class="card hidden" id="done"><p class="hint">You're in, <b id="who"></b>!</p><div class="timer" id="timer">00:00</div>
<p class="hint">Your clock is running. Go find card <b>#1</b>!</p>
<div class="badge" id="count"></div><div class="prog" id="prog"></div>
<a class="btn alt" href="index.html">My Pokédex</a>
<button class="btn" style="background:#999;font-size:14px;padding:10px" onclick="reset()">Start over with a new name</button></div>
""", depth=0, extra_js="""
function show(s){document.getElementById('form').classList.add('hidden');document.getElementById('done').classList.remove('hidden');
document.getElementById('who').textContent=s.name;HUNT.renderProg(s);HUNT.tick(s);}
function go(){var n=document.getElementById('name').value.trim();if(!n){alert('Type your trainer name first!');return;}show(HUNT.register(n));}
function reset(){if(confirm('This erases this phone\\'s progress and restarts the clock. Continue?')){localStorage.removeItem('pokehunt_v2');location.reload();}}
var s=HUNT.load(); if(s.start) show(s);"""))

# ---------- catch pages ----------
for i, (slug, name, color) in enumerate(POKEMON, start=1):
    vid = ASSETS/f"{slug}.mp4"
    media = (f'<video class="vid" autoplay muted loop playsinline poster="../img/{slug}.png" onclick="this.muted=!this.muted"><source src="../assets/{slug}.mp4" type="video/mp4"></video>'
             f'<p class="small" style="margin:4px 0 8px">Tap the video for sound</p>') if vid.exists() else f'<img src="../img/{slug}.png" alt="{html.escape(name)}">'
    body = f"""
<div id="unreg" class="hidden"><h1>Not so fast!</h1><p class="sub">You found {html.escape(name)}, but your clock isn't running.</p>
<div class="card"><p class="hint">Scan the <b>REGISTER</b> poster at the door first, then come back and scan this card again.</p>
<a class="btn" href="../register.html">Register now</a></div></div>
<div id="ok" class="hidden"><h1>You caught {html.escape(name)}!</h1><p class="sub">Card #{i} of {N}</p>
<div class="card">{media}<div class="timer" id="timer">00:00</div>
<div class="badge" id="count"></div><div class="prog" id="prog"></div>
<p class="hint" id="next" style="margin-top:14px">Keep going, <b id="who"></b>! Find the next card.</p>
<a class="btn gold hidden" id="prize" href="../prize/{PRIZE_SLUG}.html">⭐ ALL {N} CAUGHT! Tap for your prize</a></div></div>"""
    js = f"""var s=HUNT.catchOne({i});
if(!s){{document.getElementById('unreg').classList.remove('hidden');}}
else{{document.getElementById('ok').classList.remove('hidden');document.getElementById('who').textContent=s.name;HUNT.renderProg(s);HUNT.tick(s);
 if(s.end){{document.getElementById('next').classList.add('hidden');document.getElementById('prize').classList.remove('hidden');
   setTimeout(function(){{location.href='../prize/{PRIZE_SLUG}.html';}},4000);}}}}"""
    (SITE/"catch"/f"{slug}.html").write_text(page(f"You caught {name}!", body, extra_js=js))

# ---------- prize page ----------
subject = f"{KID}'s Pokémon Hunt activity book"
mail_body = f"Congratulations, Master Trainer!\n\nHere is the Pokémon activity book you earned at {KID}'s party. Open this link and print it:\n{pack_url}\n\nThanks for coming!"
mailto = f"mailto:?subject={quote(subject)}&body={quote(mail_body)}"
QRJS = '<script src="../assets/qrcode.min.js"></script>'
body = f"""
<div id="notyet" class="hidden"><h1>Keep hunting!</h1><div class="card"><div class="badge" id="count"></div><div class="prog" id="prog"></div>
<p class="hint">Catch all {N} Pokémon to unlock the prize.</p><a class="btn alt" href="../index.html">Back to my Pokédex</a></div></div>
<div id="won" class="hidden"><h1>MASTER TRAINER!</h1>
<video class="vid" autoplay muted loop playsinline poster="../assets/master-ball-poster.jpg" onclick="this.muted=!this.muted"><source src="../assets/master-ball.mp4" type="video/mp4"></video>
<p class="small" style="margin:4px 0 12px">Tap the video for sound</p>
<div class="card"><p class="hint"><b id="who"></b> caught all {N} Pokémon in</p><div class="timer done" id="final">00:00</div>
<p class="hint" style="font-size:22px;font-weight:800">Find <b>{KID}'s Dad</b> in the <b>{PRIZE_SPOT}</b> for your prize!</p>
<p class="hint">Show him this screen so he can scan your time:</p>
<div id="qr" style="display:flex;justify-content:center;margin:10px 0"></div></div>
<div class="card"><p class="hint">Bonus: an activity book of every Pokémon you found.</p>
<a class="btn" href="../coloring-pack.pdf" download="pokemon-activity-book.pdf">⬇ Download activity book</a>
<a class="btn alt" href="{html.escape(mailto)}">✉ Email it to me</a>
<p class="small">"Email it to me" opens your mail app with the link already written. Send it to yourself and print at home.</p></div></div>"""
js = f"""var s=HUNT.load();
if(!s.end){{document.getElementById('notyet').classList.remove('hidden');HUNT.renderProg(s);}}
else{{document.getElementById('won').classList.remove('hidden');document.getElementById('who').textContent=s.name;
 document.getElementById('final').textContent=HUNT.fmt(s.end-s.start);
 try{{new QRCode(document.getElementById('qr'),{{text:'{admin_url}#e='+HUNT.entry(s),width:200,height:200,correctLevel:QRCode.CorrectLevel.M}});}}catch(e){{}}}}"""
(SITE/"prize"/f"{PRIZE_SLUG}.html").write_text(page("Master Trainer!", body, extra_js=js, head=QRJS))

# ---------- admin leaderboard ----------
body = f"""
<h1>Gym Leader Board</h1><p class="sub">Fastest trainers first</p>
<div class="card" id="added" class="hidden" style="display:none"><p class="hint">Added <b id="aname"></b> — <span id="atime"></span></p></div>
<div class="card"><table><thead><tr><th>#</th><th>Trainer</th><th>Time</th><th>Finished</th><th></th></tr></thead><tbody id="rows"></tbody></table>
<p class="hint" id="empty" style="font-size:15px">No finishers yet. Scan a trainer's prize screen, or add one below.</p></div>
<div class="card"><p class="hint"><b>Add by hand</b> (if a QR won't scan)</p>
<input class="name" id="mname" placeholder="Trainer name" style="margin-bottom:8px">
<input class="name" id="mtime" placeholder="Time, like 12:34" inputmode="numeric">
<button class="btn alt" onclick="manual()">Add to board</button></div>
<div class="card"><button class="btn" style="background:#999" onclick="clearAll()">Clear the board</button>
<p class="small">This board lives on this phone only. Keep this page's link to yourself.</p></div>"""
js = """var KEY='pokehunt_admin';
function load(){try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch(e){return []}}
function save(l){try{localStorage.setItem(KEY,JSON.stringify(l))}catch(e){}}
function fmt(ms){var s=Math.floor(ms/1000),m=Math.floor(s/60);return (m<10?'0':'')+m+':'+((s%60)<10?'0':'')+(s%60);}
function render(){var l=load().sort(function(a,b){return a.ms-b.ms});var h='';
 l.forEach(function(e,i){h+='<tr><td class="rank">'+(i+1)+'</td><td>'+e.n.replace(/</g,'&lt;')+'</td><td class="t">'+fmt(e.ms)+'</td><td style="font-size:12px;color:#666">'+new Date(e.at).toLocaleTimeString([], {hour:'numeric',minute:'2-digit'})+'</td><td><a href="#" onclick="del('+e.id+');return false" style="color:#999">✕</a></td></tr>';});
 document.getElementById('rows').innerHTML=h;document.getElementById('empty').style.display=l.length?'none':'block';}
function add(n,ms,at){var l=load();if(l.some(function(e){return e.n===n&&e.ms===ms}))return;l.push({id:Date.now()+Math.random(),n:n,ms:ms,at:at||Date.now()});save(l);render();
 var a=document.getElementById('added');a.style.display='block';document.getElementById('aname').textContent=n;document.getElementById('atime').textContent=fmt(ms);}
function del(id){var l=load().filter(function(e){return e.id!==id});save(l);render();}
function clearAll(){if(confirm('Clear all finishers?')){save([]);render();}}
function manual(){var n=document.getElementById('mname').value.trim(),t=document.getElementById('mtime').value.trim().split(':');
 if(!n||t.length!=2){alert('Enter a name and a time like 12:34');return;} add(n,(parseInt(t[0])*60+parseInt(t[1]))*1000);
 document.getElementById('mname').value='';document.getElementById('mtime').value='';}
var m=location.hash.match(/e=([^&]+)/); if(m){try{var e=JSON.parse(decodeURIComponent(escape(atob(m[1]))));if(e.n&&e.s&&e.e)add(e.n,e.e-e.s,e.e);}catch(x){}history.replaceState(null,'',location.pathname);}
render();"""
(SITE/"admin"/f"{ADMIN_SLUG}.html").write_text(page("Gym Leader Board", body, extra_js=js))

# ================= PRINTABLES =================
def qr(url, path):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=4)
    q.add_data(url); q.make(fit=True); q.make_image(fill_color="black", back_color="white").save(path)
links = []
for i, (slug, name, color) in enumerate(POKEMON, start=1):
    url = f"{BASE_URL}catch/{slug}.html"; p = PRINT/"qr"/f"{i:02d}-{slug}.png"; qr(url, p); links.append((i, name, url, p))
qr(reg_url, PRINT/"qr"/"register.png"); qr(admin_url, PRINT/"qr"/"admin.png")
W, H = letter

# --- door poster ---
c = canvas.Canvas(str(PRINT/"door-poster.pdf"), pagesize=letter)
c.setFillColor(colors.HexColor("#E3350D")); c.rect(0, H-1.6*inch, W, 1.6*inch, stroke=0, fill=1)
c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 34); c.drawCentredString(W/2, H-0.8*inch, f"{KID.upper()}'S POKÉMON HUNT")
c.setFont("Helvetica-Bold", 18); c.drawCentredString(W/2, H-1.25*inch, "REGISTER HERE TO START YOUR CLOCK")
c.setFillColor(colors.black)
c.drawImage(str(PRINT/"qr"/"register.png"), W/2-1.9*inch, H-5.7*inch, 3.8*inch, 3.8*inch)
c.setFont("Helvetica-Bold", 20); c.drawCentredString(W/2, H-6.1*inch, "Parents: scan with your phone camera")
c.setFont("Helvetica", 13); c.drawCentredString(W/2, H-6.4*inch, "Type your trainer's name and tap  Start the clock!")
c.setFont("Helvetica-Bold", 16); c.drawString(1.0*inch, H-7.1*inch, "HOW TO PLAY")
c.setFont("Helvetica", 13.5); y = H-7.45*inch
for line in [f"1.  {N} Pokémon cards are hidden around the house.",
             "2.  Find a card and scan its QR code with the SAME phone you registered on.",
             "3.  Each scan catches that Pokémon and shows your running time.",
             f"4.  Catch all {N} and your clock stops. The prize screen appears!",
             f"5.  Show the prize screen to {KID}'s Dad in the {PRIZE_SPOT.lower()}. Fastest trainers win!"]:
    c.drawString(1.0*inch, y, line); y -= 0.32*inch
c.setFont("Helvetica-Oblique", 11); c.drawCentredString(W/2, 0.7*inch, "No app needed. Any phone camera reads the codes. One registration per phone (teams welcome).")
c.save()

# --- hunt cards (2 per page) ---
c = canvas.Canvas(str(PRINT/"hunt-cards.pdf"), pagesize=letter)
CW, CH = 3.9*inch, 6.6*inch
slots = [((W-2*CW-0.4*inch)/2, H-CH-0.9*inch), ((W-2*CW-0.4*inch)/2+CW+0.4*inch, H-CH-0.9*inch)]
def draw_card(x, y, num, name, img, qrp):
    c.setStrokeColor(colors.HexColor("#1b1f3b")); c.setLineWidth(2); c.roundRect(x, y, CW, CH, 18)
    c.setFillColor(colors.HexColor("#E3350D")); c.roundRect(x, y+CH-0.55*inch, CW, 0.55*inch, 18, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 16); c.drawCentredString(x+CW/2, y+CH-0.37*inch, f"#{num}  {name}")
    c.setFillColor(colors.black)
    c.drawImage(str(img), x+0.3*inch, y+CH-0.55*inch-3.1*inch, CW-0.6*inch, 2.9*inch, preserveAspectRatio=True, anchor="c")
    c.setFont("Helvetica-Bold", 13); c.drawCentredString(x+CW/2, y+2.65*inch, "SCAN ME to catch!")
    c.drawImage(str(qrp), x+(CW-2.3*inch)/2, y+0.3*inch, 2.3*inch, 2.3*inch)
for i, (slug, name, color) in enumerate(POKEMON, start=1):
    x, y = slots[(i-1) % 2]; draw_card(x, y, i, name, web_imgs[slug], links[i-1][3])
    if i % 2 == 0: c.showPage()
c.save()

# --- Pokédex checklist (one per kid) ---
c = canvas.Canvas(str(PRINT/"pokedex-sheet.pdf"), pagesize=letter)
c.setFillColor(colors.HexColor("#E3350D")); c.rect(0, H-1.2*inch, W, 1.2*inch, stroke=0, fill=1)
c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 30); c.drawCentredString(W/2, H-0.75*inch, "MY POKÉDEX")
c.setFillColor(colors.black); c.setFont("Helvetica", 14); c.drawString(0.8*inch, H-1.7*inch, "Trainer name: ________________________________")
c.setFont("Helvetica", 12); c.drawString(0.8*inch, H-2.1*inch, "Check off each Pokémon as you catch it. Your phone keeps the time!")
top = H-2.7*inch
for i, (slug, name, color) in enumerate(POKEMON, start=1):
    y = top-(i-1)*0.72*inch
    c.setStrokeColor(colors.HexColor("#1b1f3b")); c.setLineWidth(1.5); c.rect(0.8*inch, y-0.5*inch, 0.5*inch, 0.5*inch)
    c.drawImage(str(web_imgs[slug]), 1.5*inch, y-0.55*inch, 0.6*inch, 0.6*inch, preserveAspectRatio=True, anchor="c")
    c.setFont("Helvetica-Bold", 16); c.drawString(2.3*inch, y-0.35*inch, f"#{i}  {name}")
    c.setFont("Helvetica", 11); c.drawString(W-2.6*inch, y-0.35*inch, "Where I found it: ________")
y = top-N*0.72*inch-0.4*inch
c.setFont("Helvetica-Bold", 14); c.drawString(0.8*inch, y, "My finish time:  ____ : ____")
c.setFont("Helvetica", 12); c.drawString(0.8*inch, y-0.4*inch, f"Show your prize screen to {KID}'s Dad in the {PRIZE_SPOT.lower()}!")
c.save()

# --- admin card + cheat sheet (Dad only) ---
c = canvas.Canvas(str(PRINT/"DAD-ONLY-admin-and-cheat-sheet.pdf"), pagesize=letter)
c.setFont("Helvetica-Bold", 22); c.drawString(0.8*inch, H-0.9*inch, "Gym Leader (admin) card — keep private")
c.drawImage(str(PRINT/"qr"/"admin.png"), 0.8*inch, H-4.2*inch, 3*inch, 3*inch)
c.setFont("Helvetica", 12); y = H-1.6*inch
for line in ["Scan this once with YOUR phone and bookmark it.", "This is your leaderboard.", "",
             "When a kid shows you their prize screen,", "scan the QR code on it with your phone:", "their name and time are added, fastest first.", "",
             "If a QR won't scan, read the time off their", "screen and type it in the 'Add by hand' box."]:
    c.drawString(4.1*inch, y, line); y -= 0.26*inch
c.setFont("Helvetica-Bold", 16); c.drawString(0.8*inch, H-4.8*inch, "Links"); c.setFont("Helvetica", 10.5); y = H-5.1*inch
for line in [f"Register (door poster): {reg_url}", f"Admin board (private):   {admin_url}", f"Prize page (auto after {N}):  {prize_url}", f"Activity book:  {pack_url}", ""] + \
            [f"#{i}  {n:<12} {u}" for i, n, u, p in links] + ["",
             "Setup: tape the 8 cards at kid eye level in different rooms. Put the door poster where parents walk in.",
             "Test: register on your own phone, scan one card, confirm the clock runs. Then 'Start over' on the register page.",
             "Phones must be on wifi or cell data. If a phone won't scan, type the catch link above into its browser."]:
    c.drawString(0.8*inch, y, line); y -= 0.24*inch
c.save()

json.dump({"base_url": BASE_URL, "register": reg_url, "admin": admin_url, "prize": prize_url, "pack": pack_url,
           "catch": {n: u for i, n, u, p in links}}, open(ROOT/"manifest.json", "w"), indent=2)
print("Built →", SITE, PRINT)
