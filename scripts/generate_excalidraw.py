"""
Generates docs/architecture.excalidraw
Open at https://excalidraw.com → File → Open → export as PNG
"""
import json, random, time, os

os.makedirs("docs", exist_ok=True)
random.seed(42)

# ── Helpers ────────────────────────────────────────────────────────────────

def uid():
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=16))

NOW = int(time.time() * 1000)

def base(eid, etype, x, y, w, h, extra=None):
    d = {
        "id": eid, "type": etype,
        "x": x, "y": y, "width": w, "height": h,
        "angle": 0, "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
        "roundness": None, "seed": random.randint(1, 9999999),
        "version": 1, "versionNonce": random.randint(1, 9999999),
        "isDeleted": False, "boundElements": [], "updated": NOW,
        "link": None, "locked": False,
    }
    if extra:
        d.update(extra)
    return d

def cluster(x, y, w, h, label, bg="#f1f3f5", stroke="#adb5bd"):
    eid = uid(); tid = uid()
    r = base(eid, "rectangle", x, y, w, h, {
        "strokeColor": stroke, "backgroundColor": bg,
        "strokeWidth": 2, "strokeStyle": "solid",
        "roundness": {"type": 3},
        "boundElements": [{"type": "text", "id": tid}],
    })
    t = base(tid, "text", x + 12, y + 10, w - 24, 28, {
        "strokeColor": stroke, "text": label,
        "fontSize": 14, "fontFamily": 2,
        "textAlign": "left", "verticalAlign": "top",
        "containerId": None, "originalText": label,
        "lineHeight": 1.2,
    })
    return [r, t]

def box(x, y, w, h, label, bg="#ffffff", stroke="#339af0", fs=13):
    eid = uid(); tid = uid()
    lines = label.count("\n") + 1
    lh = fs * 1.35
    ty = y + max(0, (h - lh * lines) / 2)
    r = base(eid, "rectangle", x, y, w, h, {
        "strokeColor": stroke, "backgroundColor": bg,
        "strokeWidth": 2, "roundness": {"type": 3},
        "boundElements": [{"type": "text", "id": tid}],
    })
    t = base(tid, "text", x + 6, ty, w - 12, lh * lines, {
        "strokeColor": "#1e1e1e", "text": label,
        "fontSize": fs, "fontFamily": 2,
        "textAlign": "center", "verticalAlign": "middle",
        "containerId": eid, "originalText": label,
        "lineHeight": 1.35,
    })
    # store center for arrow routing
    r["_cx"] = x + w / 2
    r["_cy"] = y + h / 2
    return [r, t], eid

def arrow(x1, y1, x2, y2, label="", color="#1e1e1e", dashed=False):
    eid = uid()
    a = base(eid, "arrow", x1, y1, x2 - x1, y2 - y1, {
        "strokeColor": color,
        "strokeStyle": "dashed" if dashed else "solid",
        "strokeWidth": 2,
        "roundness": {"type": 2},
        "points": [[0, 0], [x2 - x1, y2 - y1]],
        "lastCommittedPoint": None,
        "startBinding": None, "endBinding": None,
        "startArrowhead": None, "endArrowhead": "arrow",
    })
    els = [a]
    if label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        tw = max(len(label) * 7, 80)
        lt = base(uid(), "text", mid_x - tw/2, mid_y - 14, tw, 22, {
            "strokeColor": "#495057", "text": label,
            "fontSize": 11, "fontFamily": 2,
            "textAlign": "center", "verticalAlign": "middle",
            "containerId": None, "originalText": label,
            "lineHeight": 1.2,
        })
        els.append(lt)
    return els

def label_only(x, y, text, color="#495057", fs=11):
    tw = max(len(text) * 7, 60)
    return [base(uid(), "text", x, y, tw, fs * 1.4, {
        "strokeColor": color, "text": text,
        "fontSize": fs, "fontFamily": 2,
        "textAlign": "center", "verticalAlign": "middle",
        "containerId": None, "originalText": text,
        "lineHeight": 1.2,
    })]

# ── Layout constants ────────────────────────────────────────────────────────

BW, BH = 175, 72    # standard box
GX = 40             # gap x between boxes in a chain
GY = 30             # gap y

# ── Build elements ──────────────────────────────────────────────────────────

els = []

# ── 1. USER (far left) ─────────────────────────────────────────────────────
(ue, uid_user), eid_user = box(60, 480, BW, BH, "👤  User\n(Browser)", "#fff9db", "#f59f00"), uid()
# fix: re-call properly
user_els, eid_user = box(60, 480, BW, BH, "👤  User\n(Browser)", "#fff9db", "#f59f00")
els += user_els

# ── 2. CI/CD ───────────────────────────────────────────────────────────────
cicd_els, eid_cicd = box(60, 900, BW, BH, "⚙️  GitHub Actions\nCI · Deploy Hooks", "#f8f9fa", "#868e96")
els += cicd_els

# ── 3. FRONTEND CLUSTER ────────────────────────────────────────────────────
FX = 310
els += cluster(FX - 20, 160, BW + 60, 820, "  Frontend  ·  Netlify CDN", "#e7f5ff", "#339af0")

fe_els, eid_fe = box(FX, 220, BW, BH, "⚛️  Next.js 15\nReact 19 · TypeScript", "#dbe4ff", "#4c6ef5")
els += fe_els

na_els, eid_na = box(FX, 330, BW, BH, "🔐  NextAuth v5\nGoogle OAuth", "#d3f9d8", "#2f9e44")
els += na_els

auth_els, eid_auth = box(FX, 490, BW, BH, "🔑  Google OAuth\n+ JWT  HS256", "#fff0f6", "#e64980")
els += auth_els

wa_els, eid_wa = box(FX, 650, BW, BH, "💬  WhatsApp\nWeb API", "#d3f9d8", "#2f9e44")
els += wa_els

ig_els, eid_ig = box(FX, 760, BW, BH, "📸  Instagram\nWeb Share API", "#ffe3e3", "#c92a2a")
els += ig_els

# ── 4. BACKEND CLUSTER ─────────────────────────────────────────────────────
BX = 580
els += cluster(BX - 20, 60, 1540, 1000, "  Backend  ·  Render.com  ·  FastAPI  ·  Python 3.12", "#fff9db", "#f59f00")

api_els, eid_api = box(BX + 10, 130, BW, BH, "⚡  FastAPI\nPython 3.12", "#fff9db", "#f59f00", fs=14)
els += api_els

# ── Text Engine sub-cluster ────────────────────────────────────────────────
TX = BX + 230
TY = 100
els += cluster(TX - 15, TY, BW * 4 + GX * 3 + 50, 140, "  Text Engine  ·  4-provider fallback  (→ dashed = rate-limited, try next)", "#d3f9d8", "#2f9e44")

t1_els, eid_t1 = box(TX, TY + 45, BW, BH, "OpenAI\ngpt-4o-mini", "#d3f9d8", "#2f9e44")
t2_els, eid_t2 = box(TX + BW + GX, TY + 45, BW, BH, "Groq\nllama-3.3-70b", "#d3f9d8", "#2f9e44")
t3_els, eid_t3 = box(TX + (BW + GX)*2, TY + 45, BW, BH, "Gemini\n2.0-flash", "#d3f9d8", "#2f9e44")
t4_els, eid_t4 = box(TX + (BW + GX)*3, TY + 45, BW, BH, "OpenRouter\nfree models", "#d3f9d8", "#2f9e44")
els += t1_els + t2_els + t3_els + t4_els

# fallback arrows inside text engine
cx = lambda ex: ex + BW  # right edge
def mid_y(ey): return ey + BH / 2

els += arrow(TX + BW, TY + 45 + BH//2, TX + BW + GX, TY + 45 + BH//2, "429→", "#e03131", dashed=True)
els += arrow(TX + (BW+GX) + BW, TY + 45 + BH//2, TX + (BW+GX)*2, TY + 45 + BH//2, "429→", "#e03131", dashed=True)
els += arrow(TX + (BW+GX)*2 + BW, TY + 45 + BH//2, TX + (BW+GX)*3, TY + 45 + BH//2, "429→", "#e03131", dashed=True)

# ── Image Engine sub-cluster ───────────────────────────────────────────────
IX = BX + 230
IY = 280
IW = BW - 10
els += cluster(IX - 15, IY, IW * 5 + GX * 4 + 60, 145, "  Image Engine  ·  5-provider fallback  (Pillow always runs first — zero cost, never fails)", "#f3d9fa", "#7048e8")

i1_els, eid_i1 = box(IX, IY + 48, IW, BH, "🖼️  Pillow\nTextCard  ★", "#f3d9fa", "#7048e8")
i2_els, eid_i2 = box(IX + (IW+GX), IY + 48, IW, BH, "Pollinations\n.ai", "#f3d9fa", "#7048e8")
i3_els, eid_i3 = box(IX + (IW+GX)*2, IY + 48, IW, BH, "Stable Horde\nasync poll", "#f3d9fa", "#7048e8")
i4_els, eid_i4 = box(IX + (IW+GX)*3, IY + 48, IW, BH, "HuggingFace\nSD 1.5", "#f3d9fa", "#7048e8")
i5_els, eid_i5 = box(IX + (IW+GX)*4, IY + 48, IW, BH, "Gemini\nImage Gen", "#f3d9fa", "#7048e8")
els += i1_els + i2_els + i3_els + i4_els + i5_els

for n in range(4):
    sx = IX + (IW+GX)*n + IW
    ex = IX + (IW+GX)*(n+1)
    my = IY + 48 + BH//2
    els += arrow(sx, my, ex, my, "→", "#e03131", dashed=True)

# ── Services sub-cluster ───────────────────────────────────────────────────
SVX = BX + 230
SVY = 465
SW = 215
els += cluster(SVX - 15, SVY, SW * 3 + 60 + 50, 135, "  Services", "#ffe3e3", "#e03131")

sv1_els, _ = box(SVX, SVY + 42, SW, BH, "⏰  APScheduler\nDaily auto-posts", "#ffe3e3", "#e03131")
sv2_els, _ = box(SVX + SW + 30, SVY + 42, SW, BH, "📈  Trend Engine\nReddit · Hacker News", "#ffe3e3", "#e03131")
sv3_els, _ = box(SVX + (SW+30)*2, SVY + 42, SW, BH, "🔥  Incident\nAnalyzer", "#ffe3e3", "#e03131")
els += sv1_els + sv2_els + sv3_els

# ── Observability sub-cluster ──────────────────────────────────────────────
OBX = BX + 230
OBY = 640
OW = 215
els += cluster(OBX - 15, OBY, OW * 3 + 60 + 50, 140, "  Observability  ·  structlog JSON", "#e3fafc", "#0c8599")

ob1_els, eid_ob1 = box(OBX, OBY + 45, OW, BH, "📝  structlog\nJSON renderer", "#e3fafc", "#0c8599")
ob2_els, eid_ob2 = box(OBX + OW + 30, OBY + 45, OW, BH, "_LokiHandler\nHTTP push", "#e3fafc", "#0c8599")
ob3_els, eid_ob3 = box(OBX + (OW+30)*2, OBY + 45, OW, BH, "OTLP Exporter\nTraces", "#e3fafc", "#0c8599")
els += ob1_els + ob2_els + ob3_els

# internal flow arrows
ob1_cx = OBX + OW;  ob_my = OBY + 45 + BH//2
ob2_cx = OBX + OW + 30
ob2_rx = OBX + (OW+30) + OW
ob3_lx = OBX + (OW+30)*2
els += arrow(ob1_cx, ob_my, ob2_cx, ob_my)
els += arrow(ob2_rx, ob_my, ob3_lx, ob_my)

# ── 5. DATA LAYER ─────────────────────────────────────────────────────────
DX = 2160
els += cluster(DX - 20, 160, BW + 60, 700, "  Data Layer", "#fff4e6", "#e8590c")

db1_els, eid_db1 = box(DX, 230, BW, BH, "🍃  MongoDB Atlas\n512 MB free", "#fff4e6", "#e8590c")
db2_els, eid_db2 = box(DX, 340, BW, BH, "⚡  Upstash Redis\n10K cmd/day", "#ffe3e3", "#c92a2a")
db3_els, eid_db3 = box(DX, 450, BW, BH, "☁️  Cloudinary\n25 GB CDN", "#e7f5ff", "#1971c2")
els += db1_els + db2_els + db3_els

# ── 6. GRAFANA CLOUD ───────────────────────────────────────────────────────
GFX = 2400
els += cluster(GFX - 20, 160, BW + 60, 700, "  Grafana Cloud", "#fff0f6", "#a61e4d")

gf1_els, eid_gf1 = box(GFX, 230, BW, BH, "📋  Loki\nLog Storage", "#fff0f6", "#a61e4d")
gf2_els, eid_gf2 = box(GFX, 340, BW, BH, "🔍  Tempo\nTrace Storage", "#fff0f6", "#a61e4d")
gf3_els, eid_gf3 = box(GFX, 450, BW, BH, "📊  Dashboards\nLogQL Panels", "#fff0f6", "#a61e4d")
els += gf1_els + gf2_els + gf3_els

# Loki + Tempo → Dashboard
gf1_cx = GFX + BW//2; gf3_ty = 450
els += arrow(gf1_cx, 230 + BH, gf1_cx, gf3_ty)
gf2_cx = GFX + BW//2
els += arrow(gf2_cx, 340 + BH, gf2_cx, gf3_ty)

# ── CROSS-CLUSTER ARROWS ───────────────────────────────────────────────────

# user → frontend
user_rx = 60 + BW;  fe_lx = FX;  user_my = 480 + BH//2;  fe_my = 220 + BH//2
els += arrow(user_rx, user_my, fe_lx, fe_my, "HTTPS")

# user → auth (indirect, via nextauth)
els += arrow(FX + BW, 330 + BH//2, FX, 490 + BH//2, "verify token")

# frontend → backend
fe_rx = FX + BW;  api_lx = BX + 10;  fe_cy = 220 + BH//2
els += arrow(fe_rx, 220 + BH//2, api_lx, 130 + BH//2, "REST · Bearer JWT")

# api → text engine
api_rx = BX + 10 + BW;  t1_my = TY + 45 + BH//2
els += arrow(api_rx, 130 + BH//2, TX, t1_my, "text prompt")

# api → image engine
els += arrow(api_rx, 130 + BH//2, IX, IY + 48 + BH//2, "image prompt")

# api → services
els += arrow(api_rx, 130 + BH//2, SVX, SVY + 42 + BH//2)

# api → observability
els += arrow(BX + 10 + BW//2, 130 + BH, BX + 10 + BW//2, OBY + 45 + BH//2)

# api → mongodb
api_top_x = BX + 10 + BW//2
els += arrow(BX + 10 + BW, 130 + BH//2, DX, 230 + BH//2, "read/write")

# api → redis
els += arrow(BX + 10 + BW, 130 + BH//2, DX, 340 + BH//2, "rate limit · cache")

# api → cloudinary (upload)
els += arrow(BX + 10 + BW, 130 + BH//2, DX, 450 + BH//2, "upload PNG")

# cloudinary → api (CDN URL return)
els += arrow(DX, 450 + BH//2, BX + 10 + BW, 130 + BH//2, "CDN URL", "#1971c2")

# loki handler → Grafana Loki
ob2_cx_r = OBX + OW + 30 + OW;  ob2_my = OBY + 45 + BH//2
els += arrow(ob2_cx_r, ob2_my, GFX, 230 + BH//2, "JSON log streams", "#0c8599")

# OTLP → Grafana Tempo
ob3_cx = OBX + (OW+30)*2 + OW//2;  ob3_my = OBY + 45 + BH//2
els += arrow(OBX + (OW+30)*2 + OW, ob3_my, GFX, 340 + BH//2, "OTLP spans", "#0c8599")

# frontend → whatsapp
els += arrow(FX + BW//2, 760 + BH//2, wa_els[0]["x"] + BW//2, wa_els[0]["y"], "caption + image URL", "#2f9e44")

# frontend → instagram (web share)
els += arrow(FX + BW//2, 760 + BH//2, ig_els[0]["x"] + BW//2, ig_els[0]["y"] + BH, "Blob · nav.share()", "#c92a2a")

# CI/CD → frontend
els += arrow(60 + BW//2, 900, FX + BW//2, 220 + BH, "auto-deploy", "#868e96")
# CI/CD → backend
els += arrow(60 + BW, 900 + BH//2, BX + 10, 130 + BH//2, "render deploy hook", "#868e96")

# ── Assemble ────────────────────────────────────────────────────────────────

# remove helper _cx/_cy keys before serializing
clean = []
for e in els:
    ec = {k: v for k, v in e.items() if not k.startswith("_")}
    clean.append(ec)

doc = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://excalidraw.com",
    "elements": clean,
    "appState": {
        "viewBackgroundColor": "#ffffff",
        "gridSize": None,
    },
    "files": {},
}

out = "docs/architecture.excalidraw"
with open(out, "w") as f:
    json.dump(doc, f, indent=2)

print(f"✅  Saved {out}  ({len(clean)} elements)")
print("👉  Open https://excalidraw.com → File → Open → select the file → Export → PNG")
