"""Activity drawers for the coloring book. Each takes (c, box) where box=(x0,y0,x1,y1) and draws inside it."""
import math, random
from reportlab.lib.units import inch
from reportlab.lib import colors

INK = colors.black
rng = random.Random(42)

def txt(c, x, y, s, size=12, bold=False, center=False):
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    (c.drawCentredString if center else c.drawString)(x, y, s)

def pokeball(c, x, y, r):
    c.circle(x, y, r); c.line(x-r, y, x+r, y); c.circle(x, y, r*0.3); c.circle(x, y, r*0.14)

def star(c, x, y, r):
    p = c.beginPath()
    for k in range(10):
        a = math.pi/2 + k*math.pi/5; rr = r if k % 2 == 0 else r*0.45
        (p.moveTo if k == 0 else p.lineTo)(x+rr*math.cos(a), y+rr*math.sin(a))
    p.close(); c.drawPath(p, stroke=1, fill=0)

# ---------------- 1. MAZE ----------------
def maze(c, box, cols=11, rows=11):
    x0, y0, x1, y1 = box
    cw = min((x1-x0)/cols, (y1-y0)/rows); gw, gh = cw*cols, cw*rows
    ox, oy = x0+(x1-x0-gw)/2, y0+(y1-y0-gh)/2
    # DFS maze
    walls = {}
    for r in range(rows):
        for col in range(cols):
            walls[(r, col)] = {"N": True, "S": True, "E": True, "W": True}
    seen = {(0, 0)}; stack = [(0, 0)]
    while stack:
        r, col = stack[-1]
        nbrs = [(d, (r+dr, col+dc)) for d, dr, dc in (("N", 1, 0), ("S", -1, 0), ("E", 0, 1), ("W", 0, -1))
                if 0 <= r+dr < rows and 0 <= col+dc < cols and (r+dr, col+dc) not in seen]
        if not nbrs: stack.pop(); continue
        d, nxt = rng.choice(nbrs)
        walls[(r, col)][d] = False
        walls[nxt][{"N": "S", "S": "N", "E": "W", "W": "E"}[d]] = False
        seen.add(nxt); stack.append(nxt)
    walls[(0, 0)]["W"] = False; walls[(rows-1, cols-1)]["E"] = False   # entrance / exit
    c.setLineWidth(2.2)
    for (r, col), w in walls.items():
        x, y = ox+col*cw, oy+r*cw
        if w["S"]: c.line(x, y, x+cw, y)
        if w["N"]: c.line(x, y+cw, x+cw, y+cw)
        if w["W"]: c.line(x, y, x, y+cw)
        if w["E"]: c.line(x+cw, y, x+cw, y+cw)
    c.setFont("Helvetica-Bold", 10); c.drawRightString(ox-4, oy+cw*0.35, "START")
    c.setLineWidth(1.5); pokeball(c, ox+gw+22, oy+gh-cw*0.5, 14)
    txt(c, ox+gw+22, oy+gh-cw*0.5-26, "FINISH", 10, True, center=True)

# ---------------- 2. DOT TO DOT (a star) ----------------
def dot_to_dot(c, box):
    x0, y0, x1, y1 = box; cx, cy = (x0+x1)/2, (y0+y1)/2-10; R = min(x1-x0, y1-y0)/2-30
    pts = []
    for k in range(10):
        a = math.pi/2 + k*math.pi/5; rr = R if k % 2 == 0 else R*0.45
        pts.append((cx+rr*math.cos(a), cy+rr*math.sin(a)))
    # add midpoints so there are 20 dots
    allp = []
    for k in range(10):
        a, b = pts[k], pts[(k+1) % 10]; allp += [a, ((a[0]+b[0])/2, (a[1]+b[1])/2)]
    c.setLineWidth(1)
    for n, (x, y) in enumerate(allp, start=1):
        c.circle(x, y, 3, stroke=1, fill=1)
        dx, dy = x-cx, y-cy; L = math.hypot(dx, dy) or 1
        txt(c, x+dx/L*13, y+dy/L*13-4, str(n), 12, True, center=True)
    txt(c, cx, cy-6, "?", 40, True, center=True)

# ---------------- 3. COUNT THE BUBBLES ----------------
def count_items(c, box, items=(("bubbles", 7), ("stars", 5), ("Poké Balls", 4))):
    x0, y0, x1, y1 = box
    rowh = (y1-y0)/len(items)
    for k, (name, n) in enumerate(items):
        ry = y1-(k+1)*rowh
        c.setLineWidth(1.3); c.roundRect(x0, ry+6, x1-x0, rowh-12, 12)
        placed = []
        for _ in range(n):
            for _try in range(300):
                x = rng.uniform(x0+30, x1-130); y = rng.uniform(ry+30, ry+rowh-30)
                if all(math.hypot(x-px, y-py) > 42 for px, py in placed): break
            placed.append((x, y))
            if name == "bubbles": c.circle(x, y, 14); c.circle(x-5, y+5, 3)
            elif name == "stars": star(c, x, y, 15)
            else: pokeball(c, x, y, 14)
        c.setLineWidth(2); c.rect(x1-80, ry+rowh/2-24, 48, 48)
        txt(c, x1-56, ry+rowh/2-38, name, 9, center=True)

# ---------------- 4. WORD SEARCH ----------------
def word_search(c, box, words=("ZEKE", "SEED", "LEAF", "VINE", "GRASS", "SUN", "PARTY", "CAKE"), n=10):
    x0, y0, x1, y1 = box
    grid = [[None]*n for _ in range(n)]
    dirs = [(0, 1), (1, 0), (1, 1)]
    for w in sorted(words, key=len, reverse=True):
        for _ in range(500):
            dr, dc = rng.choice(dirs); r, col = rng.randrange(n), rng.randrange(n)
            cells = [(r+dr*k, col+dc*k) for k in range(len(w))]
            if all(0 <= a < n and 0 <= b < n and grid[a][b] in (None, w[k]) for k, (a, b) in enumerate(cells)):
                for k, (a, b) in enumerate(cells): grid[a][b] = w[k]
                break
    for r in range(n):
        for col in range(n):
            if grid[r][col] is None: grid[r][col] = rng.choice("ABCDEFGHIKLMNOPRSTUVWY")
    cell = min((x1-x0-130)/n, (y1-y0)/n); gx, gy = x0, y1-cell*n
    c.setLineWidth(1.2); c.rect(gx, gy, cell*n, cell*n)
    for r in range(n):
        for col in range(n):
            txt(c, gx+col*cell+cell/2, gy+(n-1-r)*cell+cell*0.3, grid[r][col], cell*0.55, True, center=True)
    wx = gx+cell*n+22
    txt(c, wx, y1-14, "Find:", 13, True)
    for k, w in enumerate(words):
        c.setLineWidth(1); c.rect(wx, y1-40-k*24, 10, 10); txt(c, wx+16, y1-40-k*24, w, 13)

# ---------------- 5. TRACE THE WORDS ----------------
def trace_words(c, box, lines=("HAPPY", "BIRTHDAY", "ZEKE")):
    x0, y0, x1, y1 = box
    rowh = (y1-y0)/(len(lines)+1)
    for k, w in enumerate(lines):
        y = y1-(k+1)*rowh+10
        c.setStrokeColor(colors.Color(.6, .6, .6)); c.setLineWidth(0.8); c.setDash(4, 3)
        c.line(x0, y, x1, y); c.line(x0, y+rowh*0.55, x1, y+rowh*0.55); c.setDash()
        c.saveState(); c.setFillColor(colors.white); c.setStrokeColor(colors.Color(.45, .45, .45))
        c.setFont("Helvetica-Bold", rowh*0.75)
        tw = c.stringWidth(w, "Helvetica-Bold", rowh*0.75)
        t = c.beginText((x0+x1)/2-tw/2, y); t.setTextRenderMode(1); t.setFont("Helvetica-Bold", rowh*0.75); t.textOut(w); c.drawText(t)
        c.restoreState(); c.setStrokeColor(INK)
    y = y0+12
    c.setLineWidth(0.8); c.setDash(4, 3); c.line(x0, y, x1, y); c.setDash()
    txt(c, x0, y+rowh*0.6, "Now write your own name:", 12, True)

# ---------------- 6. MATCH THE SHADOWS ----------------
def match_shadows(c, box):
    x0, y0, x1, y1 = box
    shapes = ["pokeball", "star", "balloon", "gift", "hat"]
    order = shapes[:]; rng.shuffle(order)
    rowh = (y1-y0)/len(shapes)
    def draw(kind, x, y, s, filled):
        c.saveState(); c.setLineWidth(1.5)
        if filled: c.setFillColor(INK)
        f = 1 if filled else 0
        if kind == "pokeball":
            c.circle(x, y, s, stroke=1, fill=f)
            if not filled: c.line(x-s, y, x+s, y); c.circle(x, y, s*0.3)
        elif kind == "star":
            p = c.beginPath()
            for k in range(10):
                a = math.pi/2+k*math.pi/5; rr = s if k % 2 == 0 else s*0.45
                (p.moveTo if k == 0 else p.lineTo)(x+rr*math.cos(a), y+rr*math.sin(a))
            p.close(); c.drawPath(p, stroke=1, fill=f)
        elif kind == "balloon":
            c.ellipse(x-s*0.8, y-s, x+s*0.8, y+s, stroke=1, fill=f); c.line(x, y-s, x, y-s-14)
        elif kind == "gift":
            c.rect(x-s, y-s*0.8, 2*s, s*1.4, stroke=1, fill=f); c.rect(x-s-3, y+s*0.6, 2*s+6, s*0.35, stroke=1, fill=f)
            if not filled: c.line(x, y-s*0.8, x, y+s*0.95)
        elif kind == "hat":
            p = c.beginPath(); p.moveTo(x-s, y-s); p.lineTo(x+s, y-s); p.lineTo(x, y+s*1.2); p.close(); c.drawPath(p, stroke=1, fill=f)
            c.circle(x, y+s*1.2, s*0.15, stroke=1, fill=f)
        c.restoreState()
    for k, kind in enumerate(shapes):
        y = y1-(k+0.5)*rowh
        draw(kind, x0+60, y, 22, False); c.circle(x0+105, y, 3, fill=1)
        draw(order[k], x1-60, y, 22, True); c.circle(x1-105, y, 3, fill=1)

# ---------------- 7. TIC-TAC-TOE + PATTERNS ----------------
def tictactoe_patterns(c, box):
    x0, y0, x1, y1 = box
    txt(c, x0, y1-16, "Tic-Tac-Toe: play with a friend!", 13, True)
    gw = (x1-x0-40)/3; size = min(gw, (y1-y0)*0.42)
    for k in range(3):
        gx = x0+k*(gw+20); gy = y1-36-size
        c.setLineWidth(2.5)
        for j in (1, 2):
            c.line(gx+size*j/3, gy, gx+size*j/3, gy+size); c.line(gx, gy+size*j/3, gx+size, gy+size*j/3)
    py = y1-36-size-40
    txt(c, x0, py, "What comes next? Draw it in the box.", 13, True)
    pats = [["pokeball", "star", "pokeball", "star"], ["star", "star", "pokeball", "star", "star"], ["pokeball", "pokeball", "star", "pokeball", "pokeball"]]
    rowh = (py-y0-10)/3
    for r, pat in enumerate(pats):
        y = py-20-(r+0.5)*rowh
        for k, kind in enumerate(pat):
            x = x0+30+k*52; c.setLineWidth(1.4)
            pokeball(c, x, y, 16) if kind == "pokeball" else star(c, x, y, 17)
        x = x0+30+len(pat)*52; c.setLineWidth(2); c.rect(x-20, y-20, 40, 40)

# ---------------- 8. HOW MANY Zs + DRAW THE DREAM ----------------
def zs_and_dream(c, box):
    x0, y0, x1, y1 = box
    top = (y1-y0)*0.38
    txt(c, x0, y1-16, "How many Zs is Snorlax snoring? Circle them and count!", 13, True)
    placed = []; n = 9
    for _ in range(n):
        for _t in range(400):
            x = rng.uniform(x0+20, x1-100); y = rng.uniform(y1-top+10, y1-40)
            if all(math.hypot(x-a, y-b) > 34 for a, b in placed): break
        placed.append((x, y)); txt(c, x, y, "Z", rng.choice([16, 22, 28]), True, center=True)
    c.setLineWidth(2); c.rect(x1-70, y1-top+top/2-26, 52, 52); txt(c, x1-44, y1-top+top/2-40, "answer", 9, center=True)
    by = y1-top-30
    txt(c, x0, by, "Draw what Snorlax is dreaming about:", 13, True)
    # thought bubble
    c.setLineWidth(2.5)
    bx0, by0, bx1, by1 = x0+10, y0+10, x1-10, by-20
    c.roundRect(bx0, by0+40, bx1-bx0, by1-by0-40, 40)
    c.circle(bx0+60, by0+28, 12); c.circle(bx0+32, by0+10, 7)

ACTIVITIES = {
    "pikachu":    ("Help Pikachu through the maze to the Poké Ball!", maze),
    "charmander": ("Connect the dots 1 to 20. What shape is it? Then color it!", dot_to_dot),
    "squirtle":   ("Count each kind and write the number in the box.", count_items),
    "bulbasaur":  ("Word search! Find the words going across, down, and diagonal.", word_search),
    "charizard":  ("Trace the letters, then write your own name.", trace_words),
    "eevee":      ("Draw a line from each picture to its matching shadow.", match_shadows),
    "jigglypuff": ("Games! Play tic-tac-toe, then finish the patterns.", tictactoe_patterns),
    "snorlax":    ("Shhh... Snorlax is sleeping.", zs_and_dream),
}
