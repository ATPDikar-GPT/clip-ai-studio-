import re, subprocess, tempfile, json, shutil, uuid, os, html, csv, io, socket, ssl, threading, time as time_module, random, statistics, gzip, urllib.request, urllib.parse, urllib.error
from pathlib import Path
from datetime import datetime, date, time, timezone
import streamlit as st
import imageio_ffmpeg
from faster_whisper import WhisperModel

ROOT = Path(__file__).parent
UPLOADS = ROOT / "uploads"
OUT = ROOT / "outputs"
DATA = ROOT / "data"
PROJECTS = DATA / "projects"
CALENDAR_FILE = DATA / "calendar.json"
ADS_FILE = DATA / "ad_drafts.json"
TEMPLATES_FILE = DATA / "creation_templates.json"
TWITCH_DIR = DATA / "twitch_clipper"
TWITCH_LOGS_DIR = TWITCH_DIR / "live_logs"
TWITCH_SESSIONS_DIR = TWITCH_DIR / "sessions"

# OpenAI API model catalog (verified against the current official model catalog).
OPENAI_MODEL_LABELS = {
    "gpt-6-astra": "GPT-6 Astra — МАКСИМАЛЬНОЕ КАЧЕСТВО · Pro + Max",
    "gpt-6.1-sol": "GPT-6.1 Sol — почти Astra, дешевле",
    "gpt-6.1-terra": "GPT-6.1 Terra — быстрый и сбалансированный",
    "gpt-6-luna": "GPT-6 Luna — экономная",
    "gpt-4o-mini": "GPT-4o mini — старая модель (совместимость)",
}
DEFAULT_OPENAI_MODEL = "gpt-6-astra"

for folder in (UPLOADS, OUT, DATA, PROJECTS, TWITCH_DIR, TWITCH_LOGS_DIR, TWITCH_SESSIONS_DIR):
    folder.mkdir(exist_ok=True, parents=True)

st.set_page_config(page_title="CLIP AI Studio", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"] { font-family:'Manrope','Segoe UI',sans-serif !important; }
.stApp {
  background:
    radial-gradient(ellipse at 7% 0%, rgba(130,83,255,.16), transparent 34%),
    radial-gradient(ellipse at 95% 12%, rgba(99,64,180,.10), transparent 30%),
    linear-gradient(145deg,#0D0E15 0%,#11121C 52%,#0B0C13 100%);
  color:#F4F2FA;
}
[data-testid="stHeader"] { background:rgba(13,14,21,.94); }
[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#11121B 0%,#151522 100%);
  border-right:1px solid #302943;
}
[data-testid="stSidebar"] * { color:#EAE7F4 !important; }
.block-container { padding-top:1.35rem; padding-bottom:3.5rem; max-width:1500px; }
h1,h2,h3,h4 { color:#FBFAFF !important; font-weight:800 !important; letter-spacing:-.035em; }
h1 { font-size:2.15rem !important; }
h2 { font-size:1.55rem !important; }
h3 { font-size:1.16rem !important; }
p,label,[data-testid="stMarkdownContainer"] { color:#D7D3E3; }
strong,b { color:#FFF; font-weight:800 !important; }
small,.stCaption,[data-testid="stCaptionContainer"] { color:#A9A3B9 !important; }
hr { border-color:#302A40; }

/* Navigation */
section[data-testid="stSidebar"] { min-width:265px !important; }
.nav-brand { display:flex; align-items:center; gap:10px; font-size:25px; font-weight:900; letter-spacing:-1.1px; margin:4px 0 2px; color:#FFF; }
.nav-brand .brand-icon { display:inline-flex; width:39px; height:39px; align-items:center; justify-content:center; border-radius:13px; background:linear-gradient(145deg,#A56BFF,#6841C8); box-shadow:0 7px 22px rgba(137,85,255,.28); font-size:22px; }
.nav-sub { color:#9E97B0; font-size:11px; margin:0 0 22px 49px; letter-spacing:.02em; }
[data-testid="stSidebar"] [data-testid="stRadio"] > label { color:#817A92 !important; font-size:10px !important; font-weight:800 !important; letter-spacing:.12em; }
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] { gap:5px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  padding:8px 10px; border-radius:10px; border:1px solid transparent;
  transition:background .18s ease,border .18s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#211B31; border-color:#382B50; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) { background:linear-gradient(100deg,rgba(137,85,255,.24),rgba(91,58,145,.13)); border:1px solid #6545A0; }
[data-testid="stSidebar"] [data-testid="stRadio"] label p { color:#EDE9F7 !important; font-weight:700 !important; }

/* Main surfaces */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background:linear-gradient(145deg,rgba(31,30,45,.96),rgba(24,24,36,.96));
  border:1px solid #39324D !important; border-radius:17px !important;
  padding:15px 17px !important; box-shadow:0 12px 30px rgba(0,0,0,.17);
}
div[data-testid="stExpander"] { background:#191925; border:1px solid #39324D; border-radius:13px; }
div[data-testid="stTabs"] { background:#171722; border:1px solid #39324D; border-radius:15px; padding:8px 12px 0; }
div[data-testid="stTabs"] button { color:#C8C2D7 !important; font-weight:700 !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#FFF !important; border-bottom:3px solid #A477FF; }

/* Inputs and dropdown contrast */
div[data-testid="stSelectbox"] label,div[data-testid="stSlider"] label,
div[data-testid="stFileUploader"] label,div[data-testid="stToggle"] label {
  color:#F0EDF7 !important; font-weight:700 !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,div[data-testid="stDateInput"] input,
div[data-testid="stTimeInput"] input {
  background:#222131 !important; border:1px solid #4A405F !important;
  border-radius:10px !important; color:#FFF !important; min-height:42px;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] * { color:#FFF !important; font-weight:600 !important; }
div[data-baseweb="popover"],div[data-baseweb="popover"] *,ul[role="listbox"],ul[role="listbox"] *,
div[role="listbox"],div[role="listbox"] *,li[role="option"],li[role="option"] * {
  color:#F7F5FC !important; opacity:1 !important; text-shadow:none !important;
}
div[data-baseweb="popover"] ul,div[data-baseweb="popover"] li,ul[role="listbox"] li,li[role="option"] {
  background-color:#262337 !important;
}
div[data-baseweb="popover"] li:hover,ul[role="listbox"] li:hover,li[role="option"]:hover,
li[aria-selected="true"] { background-color:#5C438A !important; color:#FFF !important; }
div[data-testid="stFileUploader"] section { background:#1D1B2A; border:1px dashed #7654B5; border-radius:14px; }
div[data-testid="stFileUploader"] section * { color:#F2EFF9 !important; }

/* Buttons */
div[data-testid="stButton"] > button,div[data-testid="stDownloadButton"] > button,
div[data-testid="stFormSubmitButton"] > button {
  border-radius:10px; border:1px solid #A17AFF;
  background:linear-gradient(115deg,#9662F0,#7046C2);
  color:#FFF !important; font-weight:800 !important; min-height:2.65rem;
  box-shadow:0 5px 17px rgba(112,70,194,.20); transition:all .18s ease;
}
div[data-testid="stButton"] > button:hover,div[data-testid="stDownloadButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
  border-color:#C6A9FF; background:linear-gradient(115deg,#A879FF,#8058D4);
  transform:translateY(-1px); box-shadow:0 8px 22px rgba(137,85,255,.28);
}
div[data-testid="stButton"] > button p,div[data-testid="stDownloadButton"] > button p,
div[data-testid="stFormSubmitButton"] > button p { color:#FFF !important; font-weight:800 !important; }
div[data-testid="stCheckbox"] label,div[data-testid="stRadio"] label { color:#EAE6F4 !important; font-weight:650 !important; }
div[data-testid="stAlert"] {
  border-radius:13px !important; border:1px solid #49405D !important;
  background:#1B1A27 !important; color:#EDE9F6 !important;
  box-shadow:0 6px 18px rgba(0,0,0,.12);
}
div[data-testid="stAlert"] p { color:#E6E1EF !important; line-height:1.5 !important; }
div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] { color:#E6E1EF !important; }

/* Unified progress and status cards: labels stay above the track, never inside it. */
.clip-progress-card {
  width:100%; box-sizing:border-box; margin:9px 0 15px; padding:15px 17px 13px;
  border:1px solid #39334B; border-radius:15px;
  background:linear-gradient(145deg,rgba(31,30,45,.97),rgba(22,22,33,.97));
  box-shadow:0 9px 24px rgba(0,0,0,.16),inset 0 1px 0 rgba(255,255,255,.025);
}
.clip-progress-head { display:flex; align-items:flex-start; justify-content:space-between; gap:14px; }
.clip-progress-stage { color:#B99BFA; font-size:9px; line-height:1.3; font-weight:900; letter-spacing:.14em; text-transform:uppercase; margin:0 0 5px; }
.clip-progress-title { color:#F7F4FC; font-size:14px; line-height:1.35; font-weight:850; letter-spacing:-.015em; }
.clip-progress-detail { color:#AFA8BF; font-size:11px; line-height:1.45; margin-top:4px; }
.clip-progress-value { flex:0 0 auto; color:#E6D9FF; font-size:18px; line-height:1; font-weight:900; font-variant-numeric:tabular-nums; padding-top:3px; }
.clip-progress-track { height:7px; margin-top:13px; width:100%; overflow:hidden; border-radius:99px; background:#2B2838; box-shadow:inset 0 1px 2px rgba(0,0,0,.35); }
.clip-progress-fill { height:100%; border-radius:99px; background:linear-gradient(90deg,#8E61E8 0%,#B58CFF 54%,#8E61E8 100%); box-shadow:0 0 11px rgba(151,105,238,.23); transition:width .28s ease; }
.clip-progress-foot { color:#797389; font-size:10px; line-height:1.35; margin-top:8px; display:flex; justify-content:space-between; gap:12px; }
.clip-status-card { display:flex; align-items:flex-start; gap:11px; box-sizing:border-box; width:100%; margin:8px 0 14px; padding:12px 15px; border-radius:13px; background:#191923; border:1px solid #373247; }
.clip-status-icon { flex:0 0 25px; height:25px; width:25px; display:flex; align-items:center; justify-content:center; border-radius:8px; background:#2B2639; color:#C7A6FF; font-size:14px; font-weight:900; }
.clip-status-card.success { border-color:#315044; background:linear-gradient(110deg,rgba(37,72,57,.28),rgba(25,25,35,.96)); }
.clip-status-card.success .clip-status-icon { color:#A9E2C1; background:#20382F; }
.clip-status-card.error { border-color:#684044; background:linear-gradient(110deg,rgba(91,43,48,.24),rgba(25,25,35,.96)); }
.clip-status-card.error .clip-status-icon { color:#FFB3B8; background:#41262D; }
.clip-status-title { color:#F3F0F9; font-size:12px; font-weight:850; line-height:1.4; }
.clip-status-detail { color:#AAA4B7; font-size:10px; line-height:1.45; margin-top:3px; }
@media (max-width:640px) { .clip-progress-card {padding:13px 13px 11px;} .clip-progress-title {font-size:13px;} .clip-progress-value {font-size:16px;} }
video { max-width:100%; border-radius:13px; border:1px solid #443957; background:#090910; }
div[data-testid="stVideo"] { max-width:300px !important; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,#211F30,#191925); border:1px solid #3C3451; border-radius:15px; padding:13px 15px; }
div[data-testid="stMetricLabel"] p { color:#AFA8C1 !important; font-weight:700; }
div[data-testid="stMetricValue"] { color:#FFF !important; font-weight:850; }
div[data-testid="stForm"] { background:#191925; border:1px solid #3B3450; border-radius:15px; padding:16px; }



/* V16 multi-platform creation studio */
.create-hero {padding:22px 24px;border:1px solid #5B477A;border-radius:20px;background:radial-gradient(ellipse at 90% 15%,rgba(160,112,255,.23),transparent 35%),linear-gradient(115deg,#241B35,#1B2030);box-shadow:0 16px 36px rgba(0,0,0,.2);margin-bottom:16px;}
.create-kicker {font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:#C7A9FF;font-weight:900;}
.create-title {font-size:27px;line-height:1.16;font-weight:900;color:#FFF;margin:8px 0;letter-spacing:-.04em;}
.create-copy {font-size:13px;color:#C8C1D8;line-height:1.6;max-width:760px;}
.create-step {font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:#BDA4EF;font-weight:850;margin:4px 0 8px;}
.create-chip {display:inline-block;border:1px solid #594674;background:#28213A;color:#EDE5FF;border-radius:999px;padding:5px 10px;font-size:11px;margin:2px 4px 2px 0;}
.template-card {border:1px solid #443858;border-radius:13px;background:linear-gradient(140deg,#252236,#1B1B29);padding:12px;min-height:86px;}
.create-note {border:1px solid #554274;border-radius:12px;background:rgba(110,75,160,.13);padding:11px 13px;color:#DCD2F0;font-size:12px;line-height:1.5;}

/* Context score card */
.context-score-card {
  display:flex; align-items:center; gap:15px; padding:14px 16px; margin:10px 0 13px;
  border:1px solid rgba(164,119,255,.34); border-radius:15px;
  background:linear-gradient(115deg,rgba(112,70,194,.17),rgba(32,29,48,.88));
  box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 8px 24px rgba(0,0,0,.13);
}
.context-score-ring {
  width:62px; height:62px; flex:0 0 62px; border-radius:50%;
  display:flex; align-items:center; justify-content:center; flex-direction:column;
  border:3px solid #9A70EF; background:radial-gradient(circle,#302347,#1B1828);
  color:#FFF; font-size:20px; line-height:1; font-weight:900;
}
.context-score-ring small {font-size:8px; color:#C5B4E8; font-weight:700; margin-top:4px; letter-spacing:.08em;}
.context-score-title {color:#FFF;font-weight:850;font-size:13px;margin-bottom:4px;}
.context-score-copy {color:#BEB6CE;font-size:11px;line-height:1.45;}
.ad-preview-shell {background:linear-gradient(145deg,#211C30,#11121B);border:1px solid #554274;border-radius:16px;padding:12px;}
.ad-preview-stage {position:relative;overflow:hidden;border-radius:12px;background:#08080D;min-height:330px;display:flex;align-items:center;justify-content:center;}
.ad-preview-banner {position:absolute;left:7%;right:7%;padding:13px 15px;border:1px solid rgba(255,255,255,.55);border-radius:12px;background:rgba(24,17,38,.94);color:white;text-align:center;box-shadow:0 8px 30px rgba(0,0,0,.4);}
.ad-preview-banner strong {display:block;font-size:17px;line-height:1.2;margin-bottom:4px;}
.ad-preview-banner span {font-size:11px;color:#E8DFFF;}

/* Premium home dashboard */
.v12-hero {
  position:relative; overflow:hidden; padding:29px 31px; border:1px solid #574178;
  border-radius:22px; min-height:188px;
  background:
    radial-gradient(ellipse at 88% 35%,rgba(150,87,255,.27),transparent 33%),
    linear-gradient(112deg,#21182F 0%,#211D34 52%,#171B2B 100%);
  box-shadow:0 18px 45px rgba(0,0,0,.23);
}
.v12-hero:after {
  content:"✦"; position:absolute; right:7%; top:12%; font-size:105px; line-height:1;
  color:rgba(190,151,255,.12); transform:rotate(-12deg); pointer-events:none;
}
.v12-kicker { color:#C5A7FF; text-transform:uppercase; letter-spacing:1.8px; font-size:10px; font-weight:850; }
.v12-hero-title { color:#FFF; font-size:32px; line-height:1.14; font-weight:850; letter-spacing:-1.1px; margin:10px 0 8px; }
.v12-hero-copy { color:#C9C1D9; font-size:13px; max-width:720px; line-height:1.65; }
.v12-section-title { color:#F8F6FC; font-size:19px; font-weight:850; letter-spacing:-.45px; margin:22px 0 12px; }
.v12-stat {
  min-height:91px; padding:15px 16px; border-radius:15px; border:1px solid #39324D;
  background:linear-gradient(145deg,#211F30,#191925);
}
.v12-stat-label { color:#AAA3BA; font-size:11px; font-weight:700; }
.v12-stat-value { color:#FFF; font-size:27px; font-weight:850; letter-spacing:-.8px; margin-top:5px; }
.v12-stat-note { color:#B99BFF; font-size:10px; margin-top:1px; }
.v12-module {
  min-height:148px; padding:16px; border-radius:16px; border:1px solid #3E3553;
  background:linear-gradient(145deg,#242136,#1B1B29); transition:all .18s ease;
}
.v12-module:hover { border-color:#8962C7; background:linear-gradient(145deg,#2C2440,#1D1B2B); }
.v12-module-icon { display:inline-flex; width:38px; height:38px; align-items:center; justify-content:center; border-radius:12px; background:rgba(151,103,239,.17); color:#C6A7FF; font-size:20px; }
.v12-module-title { color:#FFF; font-size:14px; font-weight:850; margin:11px 0 5px; }
.v12-module-copy { color:#B7B0C6; font-size:11px; line-height:1.5; min-height:34px; }
.v12-project-title { color:#F7F4FC; font-weight:800; font-size:14px; }
.v12-project-meta { color:#A9A2B8; font-size:11px; margin-top:4px; }
.by-senya { position:fixed; right:22px; bottom:12px; z-index:999999; color:#B9B1C9; font-size:10px; letter-spacing:.08em; opacity:.92; pointer-events:none; background:rgba(28,25,40,.94); border:1px solid #4B3D65; border-radius:999px; padding:6px 12px; box-shadow:0 5px 18px rgba(0,0,0,.22); }
.by-senya span { color:#C6A7FF; font-weight:850; }
</style>
""", unsafe_allow_html=True)



def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except Exception:
        return default

def write_json(path, value):
    path.parent.mkdir(exist_ok=True, parents=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)

def project_dir(pid):
    return PROJECTS / pid

def load_projects():
    items = []
    for meta in PROJECTS.glob("*/project.json"):
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
            items.append(data)
        except Exception:
            pass
    return sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)

def save_project(project):
    folder = project_dir(project["id"])
    folder.mkdir(exist_ok=True, parents=True)
    write_json(folder / "project.json", project)

def load_project(pid):
    path = project_dir(pid) / "project.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

def update_project(pid, **updates):
    p = load_project(pid)
    if p:
        p.update(updates)
        p["updated_at"] = datetime.now().isoformat(timespec="seconds")
        save_project(p)
    return p

def run_ffmpeg(args, progress_callback=None, total_seconds=None):
    """Run FFmpeg while reporting encoded time to the UI when possible."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-progress", "pipe:1", "-nostats", *args]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, encoding="utf-8", errors="replace", bufsize=1
    )
    last_percent = -1
    try:
        for line in proc.stdout:
            line = line.strip()
            if line.startswith("out_time_ms=") and progress_callback and total_seconds:
                try:
                    # FFmpeg's out_time_ms is microseconds despite the key name.
                    elapsed = int(line.split("=", 1)[1]) / 1_000_000
                    percent = max(0, min(99, int(elapsed / max(total_seconds, 0.1) * 100)))
                    if percent != last_percent:
                        progress_callback(percent)
                        last_percent = percent
                except (ValueError, ZeroDivisionError):
                    pass
        return_code = proc.wait()
    finally:
        if proc.stdout:
            proc.stdout.close()
    if return_code == 0 and progress_callback:
        progress_callback(100)
    return subprocess.CompletedProcess(cmd, return_code, "", "")

def get_media_duration(path):
    """Read duration through PyAV without loading the video into memory."""
    try:
        import av
        with av.open(str(path)) as container:
            if container.duration:
                return float(container.duration / av.time_base)
            if container.streams.video and container.streams.video[0].duration:
                stream = container.streams.video[0]
                return float(stream.duration * stream.time_base)
    except Exception:
        pass
    return None

def ass_time(t):
    t = max(0, float(t))
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def ass_escape(s):
    return s.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}").replace("\n", r"\N")

def make_ass(words, clip_start, clip_end, style, out_path):
    """Create readable ASS subtitles; supports both phrase and one-word captions."""
    styles = {
        "Классические белые": ("&H00FFFFFF", "&H00000000", 54, 3, 1),
        "Жёлтое выделение": ("&H0000D7FF", "&H00000000", 58, 4, 1),
        "Минималистичные": ("&H00FFFFFF", "&H80000000", 46, 2, 0),
        "Кинетические (одно слово)": ("&H00FFFFFF", "&H00130B22", 62, 5, 2),
        "Неоновые": ("&H00F4D5FF", "&H003B145D", 58, 4, 2),
        "Контрастные": ("&H0000FFFF", "&H00101010", 60, 5, 2),
        "Подкаст": ("&H00FFFFFF", "&H001B1B1B", 50, 3, 1),
        "Компактные": ("&H00FFFFFF", "&H00000000", 40, 2, 0),
        "Розовый акцент": ("&H00D9A5FF", "&H00190D25", 56, 4, 2),
        "Зелёный акцент": ("&H0077FFB5", "&H00101C18", 56, 4, 2),
    }
    primary, outline, size, outline_width, shadow = styles.get(
        style, styles["Классические белые"]
    )
    one_word = style == "Кинетические (одно слово)"
    alignment = 2
    margin_v = 175 if one_word else 145
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{size},{primary},&H000000FF,{outline},&H80000000,1,0,0,0,100,100,0,0,1,{outline_width},{shadow},{alignment},48,48,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    current = []
    group_start = None
    group_end = None
    for w in words:
        ws, we, txt = w
        if ws >= clip_end or we <= clip_start:
            continue
        rs = max(ws, clip_start) - clip_start
        re_ = min(we, clip_end) - clip_start
        if one_word:
            safe = ass_escape(txt.strip())
            if safe:
                events.append(
                    f"Dialogue: 0,{ass_time(rs)},{ass_time(max(re_, rs + 0.08))},Default,,0,0,0,,{{\\an2\\fad(45,45)}}{safe.upper()}"
                )
            continue
        if group_start is None:
            group_start = rs
        current.append(txt)
        group_end = re_
        if len(current) >= 4 or txt.endswith((".", "!", "?", ",")):
            events.append(f"Dialogue: 0,{ass_time(group_start)},{ass_time(group_end)},Default,,0,0,0,,{ass_escape(' '.join(current))}")
            current = []
            group_start = None
            group_end = None
    if current and group_start is not None:
        events.append(f"Dialogue: 0,{ass_time(group_start)},{ass_time(group_end)},Default,,0,0,0,,{ass_escape(' '.join(current))}")
    Path(out_path).write_text(header + "\n".join(events), encoding="utf-8-sig")

def export_clip(source, clip, settings, output_path, progress_callback=None):
    start, end = clip["start"], clip["end"]
    duration = max(0.5, end-start)
    # Fill a 9:16 canvas. Zoom presets crop further into the center.
    zoom = settings.get("zoom", "Без приближения")
    factor = {"Без приближения": 1.0, "Лёгкое приближение": 1.12, "Сильное приближение": 1.28}.get(zoom, 1.0)
    # Scale to fill 720x1280 then optionally enlarge and center-crop.
    vf = f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,scale=iw*{factor}:ih*{factor},crop=720:1280"
    args = ["-ss", str(start), "-i", str(source), "-t", str(duration)]
    if settings.get("subtitles") and clip.get("words"):
        ass_file = Path(output_path).with_suffix(".ass")
        make_ass(clip["words"], start, end, settings.get("subtitle_style","Классические белые"), ass_file)
        # Use forward slashes and escape drive colon for the FFmpeg filter parser.
        ass_arg = ass_file.resolve().as_posix().replace(":", r"\:")
        vf += f",ass='{ass_arg}'"
    args += ["-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
             "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(output_path)]
    result = run_ffmpeg(args, progress_callback=progress_callback, total_seconds=duration)
    if result.returncode != 0:
        # If this ffmpeg build lacks libass, retry without subtitles and surface a clear note.
        if settings.get("subtitles"):
            args_no_sub = ["-ss", str(start), "-i", str(source), "-t", str(duration),
                           "-vf", f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,scale=iw*{factor}:ih*{factor},crop=720:1280",
                           "-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","128k","-movflags","+faststart",str(output_path)]
            retry = run_ffmpeg(args_no_sub, progress_callback=progress_callback, total_seconds=duration)
            if retry.returncode == 0:
                return "Видео создано, но в этой сборке FFmpeg нет поддержки ASS-субтитров. Зум применён."
        raise RuntimeError(result.stderr[-1800:])
    return None


def make_quick_text_overlay(text, width, height, font_size, position, color_name, output_path):
    """Create a transparent title-card overlay with Pillow for the quick editor."""
    from PIL import Image, ImageDraw, ImageFont
    import textwrap
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    font_candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
    ]
    font = None
    for candidate in font_candidates:
        try:
            if candidate.exists():
                font = ImageFont.truetype(str(candidate), int(font_size))
                break
        except Exception:
            pass
    if font is None:
        font = ImageFont.load_default()

    max_text_width = int(width * 0.84)
    words = str(text).split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        box = draw.textbbox((0, 0), trial, font=font, stroke_width=1)
        if box[2] - box[0] <= max_text_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    lines = lines[:5]
    if not lines:
        return None
    rendered = "\n".join(lines)
    spacing = max(8, int(font_size * 0.22))
    bbox = draw.multiline_textbbox((0, 0), rendered, font=font, spacing=spacing, align="center", stroke_width=2)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = max(22, int(width * 0.035)), max(15, int(font_size * 0.35))
    box_w, box_h = min(width - 30, text_w + pad_x * 2), text_h + pad_y * 2
    x = (width - box_w) // 2
    if position == "Сверху":
        y = int(height * 0.10)
    elif position == "По центру":
        y = (height - box_h) // 2
    else:
        y = int(height * 0.78) - box_h
    y = max(18, min(height - box_h - 18, y))
    draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=22, fill=(8, 7, 15, 155), outline=(190, 155, 255, 190), width=2)
    colors = {"Белый": (255, 255, 255, 255), "Жёлтый": (255, 224, 75, 255), "Розовый": (255, 170, 225, 255)}
    color = colors.get(color_name, colors["Белый"])
    draw.multiline_text((width // 2, y + pad_y - bbox[1]), rendered, font=font, fill=color,
                        anchor="ma", align="center", spacing=spacing,
                        stroke_width=3, stroke_fill=(0, 0, 0, 230))
    image.save(output_path)
    return Path(output_path)


def export_quick_edit(input_path, output_path, trim_start, trim_end, aspect_label,
                      speed, original_volume, music_path=None, music_volume=25,
                      overlay_text="", overlay_size=54, overlay_position="Снизу",
                      overlay_color="Белый", fade_edges=True):
    """Render lightweight Shorts edits without modifying the source clip."""
    input_path, output_path = Path(input_path), Path(output_path)
    duration = float(trim_end) - float(trim_start)
    if duration < 0.5:
        raise ValueError("Выбранный фрагмент слишком короткий. Оставь не менее 0,5 секунды.")
    speed = float(speed)
    if not 0.5 <= speed <= 2.0:
        raise ValueError("Скорость должна быть в диапазоне 0,5×–2×.")
    aspect = {
        "Вертикальный 9:16 (Shorts/Reels/TikTok)": (720, 1280),
        "Горизонтальный 16:9 (YouTube)": (1280, 720),
        "Квадратный 1:1": (1080, 1080),
    }
    width, height = aspect.get(aspect_label, (720, 1280))
    out_duration = duration / speed
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    args = [ff, "-y", "-ss", str(max(0.0, float(trim_start))), "-i", str(input_path)]
    overlay_path = None
    if str(overlay_text).strip():
        overlay_path = output_path.with_name(output_path.stem + "_text.png")
        make_quick_text_overlay(overlay_text, width, height, overlay_size, overlay_position,
                                overlay_color, overlay_path)
        args += ["-loop", "1", "-framerate", "30", "-i", str(overlay_path)]
    music_index = None
    if music_path:
        music_index = 2 if overlay_path else 1
        args += ["-stream_loop", "-1", "-i", str(music_path)]

    scale = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
    video_chain = f"{scale},trim=duration={duration:.4f},setpts=PTS/{speed:.4f},fps=30"
    fade = min(0.35, max(0.0, out_duration / 5)) if fade_edges else 0.0
    if fade > 0.02:
        fade_out_start = max(0.0, out_duration - fade)
        video_chain += f",fade=t=in:st=0:d={fade:.3f},fade=t=out:st={fade_out_start:.3f}:d={fade:.3f}"
    video_chain += ",format=yuv420p"

    if music_index is not None:
        original_gain = max(0.0, min(2.0, float(original_volume) / 100.0))
        music_gain = max(0.0, min(2.0, float(music_volume) / 100.0))
        video_graph = f"[0:v]{video_chain}[base];[1:v]format=rgba[txt];[base][txt]overlay=0:0:shortest=1[vout];" if overlay_path else f"[0:v]{video_chain}[vout];"
        audio_filter = (
            f"[0:a]atempo={speed:.4f},volume={original_gain:.3f}[orig];"
            f"[{music_index}:a]atrim=duration={out_duration:.4f},asetpts=PTS-STARTPTS,volume={music_gain:.3f}[music];"
            "[orig][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        args += ["-filter_complex", video_graph + audio_filter,
                 "-map", "[vout]", "-map", "[aout]"]
    else:
        if overlay_path:
            args += ["-filter_complex", f"[0:v]{video_chain}[base];[1:v]format=rgba[txt];[base][txt]overlay=0:0:shortest=1[vout]",
                     "-map", "[vout]"]
        else:
            args += ["-vf", video_chain, "-map", "0:v:0"]
        args += ["-map", "0:a?", "-af", f"atempo={speed:.4f},volume={max(0.0, min(2.0, float(original_volume)/100.0)):.3f}"]

    args += ["-t", f"{out_duration:.4f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(output_path)]
    try:
        result = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                text=True, encoding="utf-8", errors="replace", timeout=max(180, int(out_duration * 12)))
        if result.returncode != 0 or not output_path.exists() or output_path.stat().st_size == 0:
            detail = (result.stderr or "FFmpeg не создал файл.")[-1800:]
            raise RuntimeError(detail)
    finally:
        if overlay_path and overlay_path.exists():
            try: overlay_path.unlink()
            except Exception: pass
    return output_path


def contextual_clip_score(text, segments, start, end, speech_ratio):
    """
    Offline contextual heuristic. It evaluates hook strength, completion,
    contrast, specificity, question/answer cues and local context continuity.
    It is deliberately labelled a potential score, not a guaranteed viral score.
    """
    clean = re.sub(r"\s+", " ", text).strip()
    tokens = re.findall(r"\w+", clean.lower())
    if not tokens:
        return 0, "Недостаточно распознанной речи"
    hook_patterns = [
        r"\bпочему\b", r"\bкак\b", r"\bсекрет\b", r"\bошибк[аиу]\b",
        r"\bникогда\b", r"\bвсегда\b", r"\bоказал[оа]сь\b",
        r"\bна самом деле\b", r"\bпредставьте\b", r"\bне поверите\b",
        r"\bвот почему\b", r"\bчто произошло\b", r"\bсамое главное\b",
    ]
    contrast_patterns = [r"\bно\b", r"\bоднако\b", r"\bзато\b", r"\bвместо\b",
                         r"\bхотя\b", r"\bпри этом\b", r"\bс другой стороны\b"]
    specificity_patterns = [r"\d+(?:[.,]\d+)?", r"\bрубл", r"\bдоллар", r"\bпроцент",
                            r"\bкилограмм", r"\bметр", r"\bраза?\b", r"\bлет\b"]
    hook_hits = sum(len(re.findall(p, clean, re.I)) for p in hook_patterns)
    contrast_hits = sum(len(re.findall(p, clean, re.I)) for p in contrast_patterns)
    specifics = sum(len(re.findall(p, clean, re.I)) for p in specificity_patterns)
    question = 1 if "?" in clean or re.search(r"\b(почему|зачем|как|что если)\b", clean, re.I) else 0
    payoff = 1 if re.search(r"\b(поэтому|в итоге|оказалось|вот почему|значит|вывод)\b", clean, re.I) else 0
    sentence_end = 1 if re.search(r"[.!?…][\"»)]?$", clean) else 0
    length_quality = min(1.0, len(tokens) / 42)
    density = min(1.0, len(tokens) / max(1.0, (end-start) * 2.4))
    # Look one segment either side to avoid rewarding a cut that starts/ends mid-thought.
    prev_context = any(s["end"] <= start and start - s["end"] < 3.0 for s in segments)
    next_context = any(s["start"] >= end and s["start"] - end < 3.0 for s in segments)
    continuity = 1 if (prev_context or next_context) else 0
    raw = (
        22 * min(hook_hits, 2) / 2
        + 15 * min(contrast_hits, 2) / 2
        + 12 * min(specifics, 2) / 2
        + 10 * question
        + 12 * payoff
        + 9 * sentence_end
        + 10 * length_quality
        + 7 * min(1.0, speech_ratio)
        + 3 * continuity
    )
    score = int(max(0, min(100, round(raw))))
    reasons = []
    if hook_hits: reasons.append("сильный заход")
    if contrast_hits: reasons.append("контраст/поворот мысли")
    if specifics: reasons.append("конкретика")
    if question: reasons.append("вопрос")
    if payoff: reasons.append("развязка мысли")
    if not reasons: reasons.append("ровный речевой фрагмент")
    return score, " · ".join(reasons[:3])


MOMENT_CUES = {
    "Горячие мнения": r"\b(считаю|думаю|мнение|не согласен|не согласна|бред|чушь|спор|ошибаетесь|неправ|неправы|никогда|категорически|возмущ|скандал|позор|ужас)\b",
    "Забавные моменты": r"\b(смешно|смешной|смешная|шутка|прикол|ржу|ха-ха|угар|забавно|смешит|комедия|анекдот)\b",
    "Ключевые выводы": r"\b(итог|вывод|главное|поэтому|в результате|значит|получается|суть|запомните|важно понять)\b",
    "Лучшие истории": r"\b(история|случилось|однажды|помню|когда-то|случай|представь|расскажу|произошло|в тот день)\b",
    "Удивительные факты": r"\b(оказалось|неожиданно|удивительно|факт|представьте|никто не знает|секрет|на самом деле|впервые|рекорд)\b",
    "Лучшее": r"\b(почему|как|секрет|ошибка|никогда|всегда|оказалось|на самом деле|представьте|не поверите|вот почему)\b",
}

def apply_moment_intent(candidates, moment_types=None, custom_prompt=""):
    """Lightweight offline preference ranking; semantic interpretation is done by optional API reranking."""
    chosen_types = moment_types or ["Лучшее"]
    patterns = [re.compile(MOMENT_CUES[t], re.I) for t in chosen_types if t in MOMENT_CUES]
    prompt_terms = [w.lower() for w in re.findall(r"[а-яёa-z0-9]{4,}", custom_prompt) if w.lower() not in {"найди", "момент", "где", "когда", "чтобы", "который", "которая", "которые", "видео"}]
    for c in candidates:
        body = (c.get("text", "") + " " + c.get("context_before", "") + " " + c.get("context_after", "")).lower()
        cue_hits = sum(len(p.findall(body)) for p in patterns)
        prompt_hits = sum(1 for term in prompt_terms if term in body)
        c["intent_score"] = min(20, cue_hits * 3 + prompt_hits * 2)
        c["context_score"] = min(100, int(c.get("context_score", 0)) + c["intent_score"])
        c["score"] = c["context_score"] / 25.0
    return sorted(candidates, key=lambda x: x.get("context_score", 0), reverse=True)


def choose_clips(segments, duration, clip_len, count):
    step = max(8, clip_len // 4)
    starts = list(range(0, max(1, int(duration - clip_len) + 1), step)) or [0]
    candidates = []
    for start in starts:
        end = min(duration, start + clip_len)
        inside = [s for s in segments if s["end"] > start and s["start"] < end]
        text = " ".join(s["text"] for s in inside).strip()
        tokens = re.findall(r"\w+", text)
        if len(tokens) < 10:
            continue
        speech = sum(max(0, min(s["end"], end) - max(s["start"], start)) for s in inside)
        speech_ratio = speech / max(1, end-start)
        score, reason = contextual_clip_score(text, segments, start, end, speech_ratio)
        before = " ".join(s["text"] for s in segments if s["end"] <= start and start - s["end"] <= 18)
        after = " ".join(s["text"] for s in segments if s["start"] >= end and s["start"] - end <= 18)
        candidates.append({
            "start": start, "end": end, "text": text,
            "context_before": before[-900:], "context_after": after[:900],
            "score": score / 25.0, "context_score": score, "score_reason": reason
        })
    candidates.sort(key=lambda x: x["context_score"], reverse=True)
    chosen = []
    for candidate in candidates:
        if all(abs(candidate["start"] - item["start"]) >= clip_len * 0.65 for item in chosen):
            chosen.append(candidate)
        if len(chosen) >= count:
            break
    return sorted(chosen, key=lambda x: x["start"])




def ai_rerank_candidates(candidates, api_key, model_name=DEFAULT_OPENAI_MODEL, moment_types=None, custom_prompt=""):
    """Rank candidate Shorts moments with OpenAI. GPT-6 uses Responses API."""
    if not api_key or not candidates:
        return candidates
    import urllib.request
    import urllib.error

    payload_candidates = []
    ai_input = sorted(candidates, key=lambda c: c.get("context_score", 0), reverse=True)[:24]
    for c in ai_input:
        i = candidates.index(c)
        payload_candidates.append({
            "id": i,
            "start_sec": round(float(c["start"]), 2),
            "end_sec": round(float(c["end"]), 2),
            "context_before": str(c.get("context_before", ""))[:900],
            "clip_transcript": str(c.get("text", ""))[:1800],
            "context_after": str(c.get("context_after", ""))[:900],
            "offline_score": int(c.get("context_score", 0))
        })
    system_prompt = (
        "Ты — профессиональный редактор коротких вертикальных видео. Оценивай не ключевые слова сами по себе, "
        "а законченный смысловой момент. Ищи самостоятельную мысль, сильный хук, конфликт, неожиданность, "
        "эмоцию, конкретику, понятность без длинного контекста и хорошую развязку. "
        "Не выдумывай содержание и не обещай просмотры. Возвращай только JSON."
    )
    user_prompt = (
        "Верни объект JSON с массивом ranked. Каждый элемент содержит id, score (0-100), title, hook, reason, weakness. "
        "Учитывай context_before и context_after, чтобы не вырывать мысль из разговора. "
        "Оцени каждый id, отсортируй от лучшего к худшему, не меняй id и таймкоды. "
        "Приоритетные типы моментов: " + ", ".join(moment_types or ["Лучшее"]) + ". "
        "Пожелание пользователя: " + (custom_prompt.strip() or "нет дополнительных пожеланий") + ". "
        "Не ставь высокий балл только за совпадение слов. Кандидаты:\n" + json.dumps(payload_candidates, ensure_ascii=False)
    )

    # Strict JSON schema prevents free-form output from breaking clip ranking.
    output_schema = {
        "type": "object",
        "properties": {
            "ranked": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "score": {"type": "integer"},
                        "title": {"type": "string"},
                        "hook": {"type": "string"},
                        "reason": {"type": "string"},
                        "weakness": {"type": "string"}
                    },
                    "required": ["id", "score", "title", "hook", "reason", "weakness"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["ranked"],
        "additionalProperties": False
    }

    is_gpt6 = model_name.startswith("gpt-6-") or model_name.startswith("gpt-6.")
    if is_gpt6:
        # Responses API is recommended for GPT-6 reasoning. Astra uses the highest
        # documented settings: Pro mode + Max effort. Other models use standard mode.
        reasoning = {"effort": "max" if model_name == "gpt-6-astra" else "medium"}
        if model_name == "gpt-6-astra":
            reasoning["mode"] = "pro"
        body_data = {
            "model": model_name,
            "store": False,
            "reasoning": reasoning,
            "max_output_tokens": 6000,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "text": {"format": {
                "type": "json_schema",
                "name": "clip_moment_ranking",
                "strict": True,
                "schema": output_schema
            }}
        }
        endpoint = "https://api.openai.com/v1/responses"
    else:
        # Compatibility path for legacy GPT-4o mini.
        body_data = {
            "model": model_name,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        endpoint = "https://api.openai.com/v1/chat/completions"

    body = json.dumps(body_data, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=300 if model_name == "gpt-6-astra" else 180) as response:
            result = json.loads(response.read().decode("utf-8"))

        if is_gpt6:
            if result.get("status") == "incomplete":
                raise RuntimeError(f"OpenAI вернул неполный ответ: {result.get('incomplete_details') or 'лимит ответа'}")
            text_parts = []
            for output_item in result.get("output", []):
                if output_item.get("type") == "message":
                    for part in output_item.get("content", []):
                        if part.get("type") == "output_text":
                            text_parts.append(part.get("text", ""))
            content = "".join(text_parts)
        else:
            content = result["choices"][0]["message"]["content"]
            if isinstance(content, list):
                content = "".join(part.get("text", "") for part in content if isinstance(part, dict))

        if not content:
            raise RuntimeError("OpenAI вернул пустой текстовый ответ. Проверь статус запроса и лимиты API.")
        parsed = json.loads(content)
        ranked = parsed.get("ranked", [])
        enriched = []
        for item in ranked:
            try:
                cid = int(item["id"])
                if cid < 0 or cid >= len(candidates):
                    continue
                candidate = dict(candidates[cid])
                candidate["ai_score"] = max(0, min(100, int(item.get("score", 0))))
                candidate["ai_title"] = str(item.get("title", ""))[:120]
                candidate["ai_hook"] = str(item.get("hook", ""))[:220]
                candidate["ai_reason"] = str(item.get("reason", ""))[:500]
                candidate["ai_weakness"] = str(item.get("weakness", ""))[:300]
                candidate["score"] = candidate["ai_score"] / 25.0
                candidate["context_score"] = candidate["ai_score"]
                candidate["score_reason"] = candidate["ai_reason"] or candidate.get("score_reason", "")
                enriched.append(candidate)
            except (KeyError, TypeError, ValueError):
                continue
        if not enriched:
            raise RuntimeError("AI вернул ответ без корректного списка кандидатов.")
        return enriched
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:900]
        try:
            api_message = json.loads(detail).get("error", {}).get("message", detail)
        except Exception:
            api_message = detail
        if e.code == 401:
            hint = " Проверь API-ключ: подписка ChatGPT и API-биллинг — разные вещи."
        elif e.code == 403:
            hint = " У API-проекта может не быть доступа к выбранному режиму или модели."
        elif e.code == 404:
            hint = " Модель или endpoint не найдены для этого API-проекта."
        elif e.code == 429:
            hint = " Проверь API-баланс, лимиты и квоты проекта."
        else:
            hint = ""
        raise RuntimeError(f"OpenAI API ({e.code}): {api_message}{hint}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Не удалось подключиться к OpenAI API: {e}")
    except (KeyError, json.JSONDecodeError, IndexError, TypeError) as e:
        raise RuntimeError(f"Не удалось разобрать ответ OpenAI: {e}")


def check_openai_model_access(api_key, model_name):
    """Check whether the supplied API project can retrieve the selected model."""
    import urllib.request
    import urllib.error
    request = urllib.request.Request(
        f"https://api.openai.com/v1/models/{model_name}",
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET"
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            result = json.loads(response.read().decode("utf-8"))
        return True, result.get("id", model_name)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        try:
            detail = json.loads(detail).get("error", {}).get("message", detail)
        except Exception:
            pass
        if e.code == 401:
            detail = "API-ключ неверный или отозван. " + detail
        elif e.code == 404:
            detail = "Модель не найдена или недоступна этому API-проекту. " + detail
        return False, detail
    except urllib.error.URLError as e:
        return False, f"Нет соединения с OpenAI API: {e}"


def select_final_candidates(candidates, count):
    """Prefer AI ranking when present, while avoiding near-duplicate time ranges."""
    ordered = sorted(
        candidates,
        key=lambda c: (c.get("ai_score", c.get("context_score", 0)), c.get("context_score", 0)),
        reverse=True
    )
    chosen = []
    for candidate in ordered:
        if all(abs(candidate["start"] - existing["start"]) >= (candidate["end"]-candidate["start"]) * 0.65
               for existing in chosen):
            chosen.append(candidate)
        if len(chosen) >= count:
            break
    return sorted(chosen, key=lambda c: c["start"])


def render_ad_preview_frame(video_path, at_seconds, banner_bytes=None, ad_copy="", position="Ниже", scale=78):
    """Render one local preview frame with the selected banner position."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            frame_path = Path(tmp.name)
        cmd = [ff, "-y", "-ss", str(max(0, float(at_seconds))), "-i", str(video_path),
               "-frames:v", "1", "-vf", "scale=540:-2", str(frame_path)]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45)
        if result.returncode != 0 or not frame_path.exists() or frame_path.stat().st_size == 0:
            return None
        frame = Image.open(frame_path).convert("RGBA")
        frame_path.unlink(missing_ok=True)
        overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        margin = max(12, int(frame.width * .06))
        banner_img = None
        if banner_bytes:
            try:
                import io
                banner_img = Image.open(io.BytesIO(banner_bytes)).convert("RGBA")
                max_w = int((frame.width - 2 * margin) * max(.35, min(1.0, scale / 100)))
                max_h = int(frame.height * .30)
                banner_img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            except Exception:
                banner_img = None
        text = (ad_copy or "").strip()
        if banner_img:
            bw, bh = banner_img.size
        else:
            bw, bh = int(frame.width * .82), max(66, int(frame.height * .13))
        y = margin if position == "Выше" else (frame.height - bh) // 2 if position == "По центру" else frame.height - bh - margin
        x = (frame.width - bw) // 2
        draw.rounded_rectangle((x-8, y-8, x+bw+8, y+bh+8), radius=14, fill=(18, 13, 29, 225), outline=(190, 157, 255, 230), width=2)
        if banner_img:
            overlay.alpha_composite(banner_img, (x, y))
        elif text:
            try:
                font = ImageFont.truetype("arial.ttf", max(18, int(frame.width * .045)))
            except Exception:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text((x+(bw-tw)//2, y+(bh-th)//2), text, font=font, fill=(255,255,255,255))
        return Image.alpha_composite(frame, overlay).convert("RGB")
    except Exception:
        return None


# ---------- Twitch Clipper: chat ingestion, ranking and local export ----------
def normalize_twitch_channel(raw_value):
    """Accept a Twitch channel login or a channel URL and return its login."""
    from urllib.parse import urlparse
    raw = (raw_value or "").strip()
    if not raw:
        return ""
    if "twitch.tv" in raw.lower():
        parsed = urlparse(raw if "://" in raw else "https://" + raw)
        host = (parsed.hostname or "").lower()
        if not (host == "twitch.tv" or host.endswith(".twitch.tv")):
            return ""
        parts = [p for p in parsed.path.split("/") if p]
        if not parts or parts[0].lower() in {"videos", "directory", "downloads", "settings", "p", "search", "clip"}:
            return ""
        raw = parts[0]
    raw = raw.lstrip("@#").lower()
    return raw if re.fullmatch(r"[a-z0-9_]{1,25}", raw) else ""


def parse_chat_offset(value):
    """Parse seconds or relative HH:MM:SS / MM:SS values. Absolute dates are not offsets."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return max(0.0, float(value))
    text = str(value).strip()
    if not text:
        return None
    try:
        return max(0.0, float(text.replace(",", ".")))
    except ValueError:
        pass
    m = re.fullmatch(r"(?:(\d{1,2}):)?(\d{1,2}):(\d{1,2})(?:[.,](\d{1,3}))?", text)
    if not m:
        return None
    hh = int(m.group(1) or 0)
    mm = int(m.group(2))
    ss = int(m.group(3))
    frac = float("0." + (m.group(4) or "0"))
    return float(hh * 3600 + mm * 60 + ss) + frac


def _chat_item_to_record(item):
    if not isinstance(item, dict):
        return None
    msg = item.get("message")
    if isinstance(msg, dict):
        text = msg.get("body") or msg.get("text") or msg.get("content") or ""
    else:
        text = msg if isinstance(msg, str) else (item.get("text") or item.get("body") or item.get("content") or "")
    text = str(text).strip()
    if not text:
        return None
    offset = None
    for key in ("content_offset_seconds", "offset_seconds", "video_offset_seconds", "offset", "time_seconds", "time"):
        if key in item:
            offset = parse_chat_offset(item.get(key))
            if offset is not None:
                break
    if offset is None and item.get("timestamp") is not None:
        offset = parse_chat_offset(item.get("timestamp"))
    if offset is None:
        return None
    commenter = item.get("commenter") or item.get("user") or {}
    if isinstance(commenter, dict):
        username = commenter.get("display_name") or commenter.get("name") or commenter.get("login") or commenter.get("username") or "viewer"
    else:
        username = str(commenter or "viewer")
    if item.get("display_name"):
        username = item.get("display_name")
    if item.get("username"):
        username = item.get("username")
    return {"offset_seconds": float(offset), "username": str(username)[:80], "text": text[:1000], "manual_marker": bool(item.get("manual_marker", False))}


def parse_twitch_chat_upload(uploaded_file):
    """Read TwitchDownloader JSON/JSONL, CSV, SRT, or timestamped plain-text chat."""
    if uploaded_file is None:
        return []
    if isinstance(uploaded_file, (str, Path)):
        local_path = Path(uploaded_file)
        name = local_path.name
        raw = local_path.read_bytes()
    else:
        name = getattr(uploaded_file, "name", "chat.txt")
        raw = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    suffix = Path(name).suffix.lower()
    if str(name).lower().endswith(".json.gz") or suffix == ".gz":
        try:
            raw = gzip.decompress(raw)
            suffix = ".json"
        except Exception as exc:
            raise ValueError("Не удалось распаковать GZIP-лог. Проверь файл JSON.GZ.") from exc
    decoded = raw.decode("utf-8-sig", errors="replace")
    records = []
    if suffix == ".jsonl":
        for line in decoded.splitlines():
            try:
                rec = _chat_item_to_record(json.loads(line))
                if rec:
                    records.append(rec)
            except Exception:
                continue
    elif suffix == ".json" or decoded.lstrip().startswith("{") or decoded.lstrip().startswith("[{"):
        try:
            root = json.loads(decoded)
            candidates = []
            if isinstance(root, list):
                candidates = root
            elif isinstance(root, dict):
                for key in ("comments", "messages", "chat", "data", "events"):
                    if isinstance(root.get(key), list):
                        candidates = root[key]
                        break
            for item in candidates:
                rec = _chat_item_to_record(item)
                if rec:
                    records.append(rec)
        except Exception:
            records = []
    elif suffix == ".csv":
        reader = csv.DictReader(io.StringIO(decoded))
        for row in reader:
            normalized = {str(k).strip().lower(): v for k, v in row.items() if k}
            item = {
                "offset_seconds": next((normalized[k] for k in ("content_offset_seconds", "offset_seconds", "offset", "time", "timestamp") if k in normalized), None),
                "text": next((normalized[k] for k in ("message", "text", "body", "content") if k in normalized), ""),
                "display_name": next((normalized[k] for k in ("display_name", "username", "user", "author") if k in normalized), "viewer"),
            }
            rec = _chat_item_to_record(item)
            if rec:
                records.append(rec)
    elif suffix == ".srt":
        blocks = re.split(r"\n\s*\n", decoded.strip())
        for block in blocks:
            lines = [x.strip() for x in block.splitlines() if x.strip()]
            time_line = next((x for x in lines if "-->" in x), None)
            if not time_line:
                continue
            start_text = time_line.split("-->", 1)[0].strip().replace(",", ".")
            offset = parse_chat_offset(start_text)
            if offset is None:
                continue
            body_lines = [x for x in lines if x != time_line and not x.isdigit()]
            body = " ".join(body_lines)
            rec = _chat_item_to_record({"offset_seconds": offset, "text": body, "username": "viewer"})
            if rec:
                records.append(rec)
    else:
        pattern = re.compile(r"^\s*\[?(\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d{1,3})?)\]?\s*(?:<([^>]+)>|([^:]{1,50}):)\s*(.*)$")
        for line in decoded.splitlines():
            m = pattern.match(line)
            if not m:
                continue
            rec = _chat_item_to_record({"offset_seconds": m.group(1), "username": m.group(2) or m.group(3) or "viewer", "text": m.group(4)})
            if rec:
                records.append(rec)
    records.sort(key=lambda x: x["offset_seconds"])
    return records


HYPE_RE = re.compile(r"(?i)(pog|poggers|kekw|lol|lmao|rofl|omegalul|haha|ахах|ору|лол|жесть|имба|кек|wtf|insane|let'?s go|no way|ez|gg|💀|😂|🤣|😭|🔥|😱|🤯|❤️|👏|pogchamp)")


def rank_twitch_chat_moments(messages, duration, clip_length=45, max_clips=10):
    """Score message bursts and explicit live markers with 5-second buckets."""
    duration = max(float(duration or 0), 0.1)
    clip_length = max(10, min(180, int(clip_length)))
    max_clips = max(1, min(30, int(max_clips)))
    valid = [m for m in messages if 0 <= float(m.get("offset_seconds", -1)) < duration]
    if not valid:
        return []
    step = 5.0
    bucket_count = max(1, int(duration // step) + 1)
    buckets = [{"count": 0, "hype": 0, "users": set(), "markers": 0} for _ in range(bucket_count)]
    for msg in valid:
        idx = min(bucket_count - 1, max(0, int(float(msg["offset_seconds"]) // step)))
        bucket = buckets[idx]
        bucket["count"] += 1
        text_value = str(msg.get("text", ""))
        if HYPE_RE.search(text_value) or (len(text_value) > 3 and text_value.isupper()):
            bucket["hype"] += 1
        bucket["users"].add(str(msg.get("username", "viewer")))
        if msg.get("manual_marker"):
            bucket["markers"] += 1
    scored = []
    radius = 3  # +/- 15 seconds around each 5-second center.
    for idx in range(bucket_count):
        lo, hi = max(0, idx - radius), min(bucket_count, idx + radius + 1)
        window = buckets[lo:hi]
        count = sum(x["count"] for x in window)
        if count == 0:
            continue
        hype = sum(x["hype"] for x in window)
        users = set().union(*(x["users"] for x in window))
        markers = sum(x["markers"] for x in window)
        peak = idx * step
        score = count + 1.35 * hype + 0.85 * len(users) + 40 * markers
        scored.append({"peak": peak, "score": score, "messages": count, "hype": hype, "viewers": len(users), "markers": markers})
    if not scored:
        return []
    local_peaks = []
    for item in scored:
        neighbors = [x["score"] for x in scored if abs(x["peak"] - item["peak"]) <= 10]
        if item["score"] >= max(neighbors, default=item["score"]):
            local_peaks.append(item)
    local_peaks.sort(key=lambda x: x["score"], reverse=True)
    chosen = []
    min_gap = max(clip_length * 0.72, 20)
    for item in local_peaks:
        if any(abs(item["peak"] - prior["peak"]) < min_gap for prior in chosen):
            continue
        start = max(0.0, min(duration - 1, item["peak"] - clip_length * 0.38))
        end = min(duration, start + clip_length)
        start = max(0.0, end - clip_length)
        chosen.append({**item, "start": start, "end": end})
        if len(chosen) >= max_clips:
            break
    chosen.sort(key=lambda x: x["start"])
    return chosen


class TwitchIRCRecorder:
    """Read-only Twitch IRC capture over TLS. The OAuth token, if provided, stays in memory."""
    def __init__(self, channel, log_path, base_offset=0.0, username="", oauth_token=""):
        self.channel = channel
        self.log_path = Path(log_path)
        self.base_offset = float(base_offset or 0)
        self.username = username.strip().lower()
        self.oauth_token = (oauth_token or "").strip()
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.messages = []
        self.status = "Ожидаем подключение"
        self.error = ""
        self.started_monotonic = None
        self.started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.thread = None
        self.total_messages = 0

    def start(self):
        self.thread = threading.Thread(target=self._run, name=f"twitch-chat-{self.channel}", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.status = "Останавливаем подключение…"
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.5)
        if self.thread and not self.thread.is_alive() and self.status != "Ошибка подключения":
            self.status = "Остановлено · лог сохранён"

    def snapshot(self):
        with self.lock:
            return {"messages": list(self.messages[-3000:]), "total": self.total_messages, "status": self.status, "error": self.error}

    def mark_now(self, label="Ручная отметка"):
        elapsed = max(0.0, time_module.monotonic() - (self.started_monotonic or time_module.monotonic()))
        record = {"offset_seconds": self.base_offset + elapsed, "username": "CLIP AI", "text": label, "manual_marker": True, "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        self._record(record)

    def _record(self, record):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock:
            self.messages.append(record)
            if len(self.messages) > 3000:
                self.messages = self.messages[-3000:]
            self.total_messages += 1
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _run(self):
        context = ssl.create_default_context()
        attempt = 0
        self.started_monotonic = time_module.monotonic()
        while not self.stop_event.is_set() and attempt < 5:
            attempt += 1
            try:
                self.status = "Подключаемся к Twitch IRC по TLS…"
                with socket.create_connection(("irc.chat.twitch.tv", 6697), timeout=15) as raw_sock:
                    with context.wrap_socket(raw_sock, server_hostname="irc.chat.twitch.tv") as sock:
                        sock.settimeout(2.0)
                        if self.oauth_token:
                            token = self.oauth_token.removeprefix("oauth:").strip()
                            nick = self.username
                            if not nick:
                                raise ValueError("Для OAuth-режима укажи Twitch-логин.")
                            sock.sendall(f"PASS oauth:{token}\r\nNICK {nick}\r\n".encode("utf-8"))
                        else:
                            nick = f"justinfan{random.randint(10000, 99999999)}"
                            sock.sendall(f"PASS SCHMOOPIIE\r\nNICK {nick}\r\n".encode("utf-8"))
                        sock.sendall(b"CAP REQ :twitch.tv/tags twitch.tv/commands\r\n")
                        sock.sendall(f"JOIN #{self.channel}\r\n".encode("utf-8"))
                        self.status = "Подключено · ждём сообщения чата"
                        receive_buffer = ""
                        while not self.stop_event.is_set():
                            try:
                                data = sock.recv(8192)
                            except socket.timeout:
                                continue
                            if not data:
                                raise ConnectionError("Twitch закрыл соединение")
                            receive_buffer += data.decode("utf-8", errors="replace")
                            raw_lines = receive_buffer.split("\r\n")
                            receive_buffer = raw_lines.pop()  # Preserve a partial IRC line until the next socket read.
                            for raw_line in raw_lines:
                                if not raw_line:
                                    continue
                                if raw_line.startswith("PING "):
                                    sock.sendall(("PONG " + raw_line[5:] + "\r\n").encode("utf-8"))
                                    continue
                                if " PRIVMSG #" not in raw_line or " :" not in raw_line:
                                    if "Login authentication failed" in raw_line or "Improperly formatted auth" in raw_line:
                                        raise PermissionError("Twitch отклонил авторизацию. Проверь OAuth-токен и scope chat:read или включи анонимный режим.")
                                    continue
                                tag_map = {}
                                content = raw_line
                                if raw_line.startswith("@") and " " in raw_line:
                                    tag_blob, content = raw_line[1:].split(" ", 1)
                                    for tag in tag_blob.split(";"):
                                        if "=" in tag:
                                            k, v = tag.split("=", 1)
                                            tag_map[k] = v.replace("\\s", " ").replace("\\:", ";").replace("\\\\", "\\")
                                prefix = content.split(" ", 1)[0]
                                sender = prefix[1:].split("!", 1)[0] if prefix.startswith(":") else "viewer"
                                try:
                                    body = content.split(" :", 1)[1]
                                except IndexError:
                                    continue
                                elapsed = max(0.0, time_module.monotonic() - self.started_monotonic)
                                ts_ms = tag_map.get("tmi-sent-ts")
                                try:
                                    sent_at = datetime.fromtimestamp(int(ts_ms) / 1000, timezone.utc).isoformat(timespec="milliseconds") if ts_ms else datetime.now(timezone.utc).isoformat(timespec="milliseconds")
                                except Exception:
                                    sent_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
                                self._record({
                                    "offset_seconds": self.base_offset + elapsed,
                                    "username": tag_map.get("display-name") or sender,
                                    "text": body,
                                    "timestamp": sent_at,
                                    "manual_marker": False,
                                })
                if self.stop_event.is_set():
                    break
            except Exception as exc:
                self.error = str(exc)
                self.status = "Ошибка подключения" if attempt >= 5 else f"Переподключение {attempt}/5…"
                if attempt >= 5:
                    break
                self.stop_event.wait(min(2 * attempt, 8))
        if self.stop_event.is_set():
            self.status = "Остановлено · лог сохранён"
        elif not self.error:
            self.status = "Соединение завершено"



def twitch_helix_request(url, client_id, access_token, method="GET", body=None):
    """Make a small authenticated Helix API request without persisting Twitch credentials."""
    headers = {
        "Client-Id": client_id.strip(),
        "Authorization": "Bearer " + access_token.strip().removeprefix("oauth:"),
        "Accept": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8", errors="replace"))
            message = payload.get("message") or str(payload)
        except Exception:
            message = str(exc)
        raise RuntimeError(f"Twitch API ответил HTTP {exc.code}: {message}") from exc
    except Exception as exc:
        raise RuntimeError(f"Не удалось обратиться к Twitch API: {exc}") from exc


def create_twitch_live_clip(channel, client_id, access_token, duration=30, title="CLIP AI highlight"):
    """Request a native Twitch clip from a live channel. Requires clips:edit."""
    channel = normalize_twitch_channel(channel)
    if not channel:
        raise ValueError("Некорректный логин Twitch-канала.")
    if not client_id.strip() or not access_token.strip():
        raise ValueError("Для создания Twitch Clip нужны Client ID и OAuth-токен со scope clips:edit.")
    users_url = "https://api.twitch.tv/helix/users?" + urllib.parse.urlencode({"login": channel})
    users_data = twitch_helix_request(users_url, client_id, access_token)
    user_rows = users_data.get("data", [])
    if not user_rows:
        raise RuntimeError("Twitch не нашёл канал по этому логину.")
    broadcaster_id = user_rows[0]["id"]
    query = urllib.parse.urlencode({"broadcaster_id": broadcaster_id, "duration": max(5, min(60, float(duration))), "title": (title.strip() or "CLIP AI highlight")[:140]})
    response = twitch_helix_request("https://api.twitch.tv/helix/clips?" + query, client_id, access_token, method="POST")
    rows = response.get("data", [])
    if not rows:
        raise RuntimeError("Twitch не вернул ссылку на созданный клип.")
    return rows[0].get("id", ""), rows[0].get("edit_url", "")


def download_twitch_vod(url, destination_folder, cookies_browser="Не использовать"):
    """Download one Twitch VOD through yt-dlp, never a playlist/live stream."""
    try:
        import yt_dlp
    except ImportError as exc:
        raise RuntimeError("yt-dlp не установлен. Обнови зависимости CLIP AI или загрузи видеофайл.") from exc
    destination_folder.mkdir(parents=True, exist_ok=True)
    opts = {
        "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/best",
        "merge_output_format": "mp4",
        "outtmpl": str(destination_folder / "twitch_vod.%(ext)s"),
        "max_filesize": 500 * 1024 * 1024,
        "noplaylist": True, "quiet": True, "no_warnings": True,
        "retries": 3, "fragment_retries": 3,
    }
    if cookies_browser and cookies_browser != "Не использовать":
        opts["cookiesfrombrowser"] = (cookies_browser.lower(),)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info.get("is_live") and not info.get("duration"):
            raise RuntimeError("Это прямой эфир, а не VOD. Для LIVE используй режим мониторинга чата; видео для экспорта потребуется после завершения эфира.")
        if info.get("entries") is not None:
            raise RuntimeError("Вставь ссылку на один VOD, а не плейлист.")
        size_hint = info.get("filesize") or info.get("filesize_approx")
        if size_hint and size_hint > 500 * 1024 * 1024:
            raise RuntimeError("VOD больше лимита 500 МБ. Используй локальный фрагмент или короткую запись.")
        downloaded_info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(downloaded_info))
        if not path.exists():
            paths = sorted(destination_folder.glob("twitch_vod.*"), key=lambda p: p.stat().st_mtime, reverse=True)
            path = paths[0] if paths else path
        if not path.exists():
            raise RuntimeError("yt-dlp не нашёл скачанный файл VOD.")
        if path.stat().st_size > 500 * 1024 * 1024:
            raise RuntimeError("Скачанный VOD превысил лимит 500 МБ.")
        return path, (info.get("title") or "Twitch VOD")


def export_twitch_moment(source_path, output_path, start, end, aspect="Исходный 16:9", progress_callback=None):
    """Export an MP4 moment using the app's bundled FFmpeg."""
    duration = max(0.1, float(end) - float(start))
    args = ["-ss", f"{float(start):.3f}", "-i", str(source_path), "-t", f"{duration:.3f}", "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart"]
    if aspect == "Shorts 9:16":
        args[0:0] = []
        args.extend([])
        insert_at = args.index("-c:v")
        args[insert_at:insert_at] = ["-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"]
    elif aspect == "Квадрат 1:1":
        insert_at = args.index("-c:v")
        args[insert_at:insert_at] = ["-vf", "scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080"]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = run_ffmpeg(args + [str(output_path)], progress_callback=progress_callback, total_seconds=duration)
    if result.returncode != 0 or not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("FFmpeg не смог экспортировать клип. Проверь исходное видео и наличие видеодорожки.")
    return output_path


def render_twitch_clipper_page():
    page_title("🎮 Twitch Clipper", "Ищи хайлайты по реакции чата: отслеживай LIVE и нарезай уже готовые VOD-записи.")
    st.markdown("<div class='create-note'>LIVE сохраняет сообщения чата и таймкоды всплесков. После эфира используй этот лог вместе с VOD, чтобы экспортировать настоящие MP4-клипы. Видео в LIVE автоматически не записывается.</div>", unsafe_allow_html=True)
    live_tab, vod_tab = st.tabs(["🔴 LIVE · мониторинг чата", "📼 VOD · нарезка по чату"])

    with live_tab:
        st.markdown("### Следить за чатом в прямом эфире")
        c1, c2 = st.columns([1.35, 1])
        with c1:
            channel_input = st.text_input("Канал Twitch", placeholder="например: shroud или https://twitch.tv/shroud", key="tw_live_channel")
            auth_mode = st.radio("Подключение к чату", ["OAuth-токен chat:read", "Анонимный режим (если Twitch разрешит)"], horizontal=False, key="tw_live_auth_mode")
            live_user = ""
            live_token = ""
            live_client_id = ""
            if auth_mode == "OAuth-токен chat:read":
                live_user = st.text_input("Логин Twitch", placeholder="твой_login", key="tw_live_username")
                live_token = st.text_input("OAuth access token", type="password", placeholder="Токен со scope chat:read", key="tw_live_token", help="Токен хранится только в памяти текущей сессии и не записывается в лог. Никому не отправляй его.")
                live_client_id = st.text_input("Twitch Client ID (для создания клипов на Twitch)", type="password", placeholder="Client ID приложения Twitch", key="tw_live_client_id", help="Совпадает с Client ID, для которого выпущен OAuth-токен. Сам Client ID не является секретом, но хранится только в памяти сессии.")
                st.caption("Для чтения чата нужен scope chat:read. Для кнопки создания Twitch Clip тот же токен должен дополнительно иметь clips:edit.")
            else:
                st.caption("Анонимный read-only вход может сработать не на всех каналах/аккаунтах. Для стабильного подключения Twitch документирует OAuth со scope chat:read.")
        with c2:
            base_offset = st.number_input("Текущий таймкод эфира при старте, сек.", min_value=0.0, max_value=86400.0, value=0.0, step=30.0, key="tw_live_base_offset", help="Укажи таймкод VOD, который идёт в момент старта мониторинга. Тогда сообщения получат правильные смещения для будущей нарезки.")
            st.caption("Если запустил мониторинг с самого начала эфира — оставь 0. Если позже — введи текущий таймкод стрима.")
        capture = st.session_state.get("twitch_live_capture")
        is_running = bool(capture and capture.thread and capture.thread.is_alive() and not capture.stop_event.is_set())
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("▶ Начать мониторинг", key="tw_live_start", type="primary", use_container_width=True, disabled=is_running):
                channel = normalize_twitch_channel(channel_input)
                if not channel:
                    st.error("Введи корректный Twitch-канал или ссылку на него.")
                elif auth_mode == "OAuth-токен chat:read" and (not live_user.strip() or not live_token.strip()):
                    st.error("Для OAuth-режима нужны Twitch-логин и токен со scope chat:read.")
                else:
                    log_path = TWITCH_LOGS_DIR / f"{channel}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
                    recorder = TwitchIRCRecorder(channel, log_path, base_offset, live_user, live_token)
                    st.session_state.twitch_live_capture = recorder
                    st.session_state.twitch_last_log_path = str(log_path)
                    recorder.start()
                    st.rerun()
        with b2:
            if st.button("■ Остановить", key="tw_live_stop", use_container_width=True, disabled=not is_running):
                capture.stop()
                st.rerun()
        with b3:
            last_log = Path(st.session_state.get("twitch_last_log_path", "")) if st.session_state.get("twitch_last_log_path") else None
            if last_log and last_log.exists():
                st.download_button("⬇ Скачать лог чата", data=last_log.read_bytes(), file_name=last_log.name, mime="application/x-ndjson", use_container_width=True)
        capture = st.session_state.get("twitch_live_capture")
        if capture:
            def draw_live_capture():
                snap = capture.snapshot()
                state_color = "#67C99B" if "Подключено" in snap["status"] else ("#F2BD69" if "Переподключ" in snap["status"] or "ожидаем" in snap["status"].lower() else "#B99BFA")
                st.markdown(f"<div class='clip-status-card'><div class='clip-status-icon'>●</div><div><div class='clip-status-title'>{html.escape(snap['status'])}</div><div class='clip-status-detail'>Канал: {html.escape(capture.channel)} · Получено сообщений: {snap['total']}</div></div></div>", unsafe_allow_html=True)
                if snap["error"]:
                    st.warning(snap["error"])
                msgs = snap["messages"]
                live_now = capture.base_offset + max(0.0, time_module.monotonic() - (capture.started_monotonic or time_module.monotonic()))
                normal_msgs = [m for m in msgs if not m.get("manual_marker")]
                recent_window = [m for m in normal_msgs if live_now - 30 <= float(m.get("offset_seconds", 0)) <= live_now]
                current_burst = [m for m in normal_msgs if live_now - 10 <= float(m.get("offset_seconds", 0)) <= live_now]
                baseline_msgs = [m for m in normal_msgs if live_now - 310 <= float(m.get("offset_seconds", 0)) < live_now - 10]
                baseline_per_10s = len(baseline_msgs) / 30.0 if baseline_msgs else 0.0
                k1, k2 = st.columns(2)
                k1.metric("Сообщений за последние 30 секунд", len(recent_window))
                k2.metric("Сообщений за последние 10 секунд", len(current_burst))
                if len(current_burst) >= 5 and (baseline_per_10s == 0 or len(current_burst) >= baseline_per_10s * 2.2):
                    st.warning(f"🔥 Похоже на всплеск активности чата: {len(current_burst)} сообщений за 10 секунд против обычных {baseline_per_10s:.1f}. Проверь момент и при необходимости создай Twitch Clip.")
                if msgs:
                    st.markdown("**Последние сообщения**")
                    for msg in reversed(msgs[-8:]):
                        mark = "🎯 " if msg.get("manual_marker") else ""
                        st.markdown(f"`{float(msg.get('offset_seconds', 0)):.1f}с` **{html.escape(str(msg.get('username','viewer')))}:** {mark}{html.escape(str(msg.get('text',''))[:220])}")
                else:
                    st.caption("Пока нет сообщений. Убедись, что канал онлайн и чат открыт.")
                if not capture.stop_event.is_set():
                    if st.button("🎯 Отметить момент сейчас", key="tw_live_mark_now", use_container_width=True):
                        capture.mark_now("Ручная отметка / важный момент")
                        st.rerun()
                    if auth_mode == "OAuth-токен chat:read":
                        with st.expander("Создать настоящий Twitch Clip прямо сейчас"):
                            native_clip_length = st.slider("Длина клипа на Twitch", 5, 60, 30, key="tw_native_clip_length")
                            native_clip_title = st.text_input("Название клипа", value="CLIP AI highlight", key="tw_native_clip_title")
                            if st.button("✂ Создать клип на Twitch", key="tw_native_create_clip", use_container_width=True, disabled=not (live_token and live_client_id)):
                                try:
                                    with st.spinner("Отправляем запрос Twitch на создание клипа…"):
                                        native_id, native_url = create_twitch_live_clip(capture.channel, live_client_id, live_token, native_clip_length, native_clip_title)
                                    st.session_state.twitch_native_last_url = native_url
                                    st.success(f"Twitch принял запрос на создание клипа · ID: {native_id}. Подготовка клипа может занять несколько секунд.")
                                    if native_url:
                                        st.markdown(f"[Открыть редактор Twitch Clip]({native_url})")
                                except Exception as exc:
                                    st.error(str(exc))
                st.caption("Лог сохраняется в CLIP AI/data/twitch_clipper/live_logs. После стрима загрузи его во вкладке VOD вместе с записью. Кнопка Twitch Clip публикует/редактирует клип на стороне Twitch — экспорт Shorts MP4 делается через VOD.")
            fragment = getattr(st, "fragment", None)
            if callable(fragment) and is_running:
                fragment(run_every=3)(draw_live_capture)()
            else:
                draw_live_capture()
                if is_running and st.button("↻ Обновить чат", key="tw_live_refresh"):
                    st.rerun()
        else:
            st.info("Введи канал и нажми «Начать мониторинг». CLIP AI будет собирать сообщения и записывать их таймкоды в локальный JSONL-файл.")

    with vod_tab:
        st.markdown("### Создать клипы из VOD по реакции чата")
        st.write("Для точного сопоставления нужен VOD/локальная запись и лог чата с таймкодами. Поддерживаются JSON TwitchDownloader, JSONL из LIVE, CSV, TXT и SRT.")
        st.markdown("Если лога ещё нет, скачай **TwitchDownloader** с [официальной страницы релизов](https://github.com/lay295/TwitchDownloader/releases), открой режим Chat, вставь ссылку на VOD и сохрани чат в JSON (или TXT с Relative timestamps). Затем загрузи этот файл сюда.")
        vod_source_mode = st.radio("Источник видео", ["Ссылка на Twitch VOD", "Видео с компьютера"], horizontal=True, key="tw_vod_source_mode")
        vod_url = ""
        vod_upload = None
        cookies = "Не использовать"
        if vod_source_mode == "Ссылка на Twitch VOD":
            vod_url = st.text_input("Ссылка на запись Twitch", placeholder="https://www.twitch.tv/videos/123456789", key="tw_vod_url")
            with st.expander("Если VOD доступен только после входа"):
                cookies = st.selectbox("Браузер с активной авторизацией", ["Не использовать", "Chrome", "Edge", "Firefox", "Brave", "Opera", "Vivaldi"], key="tw_vod_cookies")
                st.caption("Используется только локальная авторизация выбранного браузера. Не передавай cookies вручную.")
        else:
            vod_upload = st.file_uploader("Выбери видео VOD · до 500 МБ", type=["mp4", "mov", "mkv", "webm"], key="tw_vod_upload")
        saved_live_logs = sorted(TWITCH_LOGS_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if saved_live_logs:
            chat_mode = st.radio("Источник чата", ["Загрузить лог чата", "Выбрать сохранённый LIVE-лог"], horizontal=True, key="tw_vod_chat_mode")
        else:
            chat_mode = "Загрузить лог чата"
            st.caption("Сохранённых LIVE-логов пока нет. Можешь загрузить экспорт чата ниже.")
        chat_upload = None
        selected_chat_path = None
        if chat_mode == "Выбрать сохранённый LIVE-лог" and saved_live_logs:
            log_labels = {f"{p.name} · {p.stat().st_size/1024:.0f} КБ": str(p) for p in saved_live_logs[:30]}
            chosen_log_label = st.selectbox("Сохранённые LIVE-логи", list(log_labels.keys()), key="tw_vod_saved_log_pick")
            selected_chat_path = log_labels[chosen_log_label]
            st.caption("Выбранный лог останется на диске и не будет удалён после нарезки.")
        else:
            chat_upload = st.file_uploader("Лог чата с таймкодами (JSON / JSON.GZ / JSONL / CSV / TXT / SRT)", type=["json", "jsonl", "csv", "txt", "srt", "gz"], key="tw_vod_chat_upload")
        if chat_upload or selected_chat_path:
            try:
                preview_records = parse_twitch_chat_upload(chat_upload if chat_upload else selected_chat_path)
                st.caption(f"Лог прочитан: {len(preview_records):,} сообщений с таймкодами")
            except Exception as exc:
                st.error(f"Не удалось прочитать лог чата: {exc}")
        cfg1, cfg2, cfg3 = st.columns(3)
        with cfg1:
            clip_length = st.selectbox("Длина клипа", [15, 20, 30, 45, 60, 90], index=3, format_func=lambda x: f"{x} секунд", key="tw_vod_clip_length")
        with cfg2:
            clip_count = st.slider("Сколько клипов создать", 1, 20, 8, key="tw_vod_clip_count")
        with cfg3:
            aspect = st.selectbox("Формат экспорта", ["Shorts 9:16", "Исходный 16:9", "Квадрат 1:1"], key="tw_vod_aspect")
        st.caption("Алгоритм ищет всплески активности чата, повторяющиеся реакции, эмодзи, caps и ручные маркеры. Он не гарантирует вирусность — финальный отбор остаётся за тобой.")
        ready_video = bool(vod_upload) if vod_source_mode == "Видео с компьютера" else bool(vod_url.strip())
        ready_chat = bool(chat_upload or selected_chat_path)
        if st.button("✨ Найти хайлайты и нарезать MP4", key="tw_vod_process", type="primary", use_container_width=True, disabled=not (ready_video and ready_chat)):
            session_id = uuid.uuid4().hex[:12]
            work_dir = TWITCH_DIR / "work" / session_id
            work_dir.mkdir(parents=True, exist_ok=True)
            try:
                with st.spinner("Готовим VOD…"):
                    if vod_upload:
                        ext = Path(vod_upload.name).suffix.lower() or ".mp4"
                        source_path = work_dir / ("source" + ext)
                        with source_path.open("wb") as out_file:
                            out_file.write(vod_upload.getbuffer())
                        source_title = vod_upload.name
                    else:
                        source_path, source_title = download_twitch_vod(vod_url, work_dir, cookies)
                    if source_path.stat().st_size > 500 * 1024 * 1024:
                        raise RuntimeError("Видео больше 500 МБ.")
                    duration = get_media_duration(source_path)
                    if not duration:
                        raise RuntimeError("Не удалось определить длительность видео. Проверь, что файл исправен и содержит видеодорожку.")
                    chat_records = parse_twitch_chat_upload(chat_upload if chat_upload else selected_chat_path)
                    if not chat_records:
                        raise RuntimeError("В логе не найдено сообщений с относительными таймкодами. Нужен экспорт чата с content_offset_seconds/offset_seconds или формат HH:MM:SS.")
                    chat_records = [m for m in chat_records if 0 <= float(m["offset_seconds"]) <= duration]
                    if not chat_records:
                        raise RuntimeError("Таймкоды чата не совпадают с длительностью видео. Проверь, что это лог именно от данного VOD и что таймкоды начинаются от 0.")
                moments = rank_twitch_chat_moments(chat_records, duration, clip_length, clip_count)
                if not moments:
                    raise RuntimeError("Не удалось найти всплески сообщений. Проверь лог чата или увеличь длительность VOD.")
                output_folder = OUT / "twitch_clips" / session_id
                output_folder.mkdir(parents=True, exist_ok=True)
                progress = st.progress(0, text="Экспортируем найденные моменты…")
                exported = []
                for index, moment in enumerate(moments, 1):
                    out_path = output_folder / f"twitch_highlight_{index:02d}.mp4"
                    export_twitch_moment(source_path, out_path, moment["start"], moment["end"], aspect)
                    exported.append({**moment, "file": str(out_path), "index": index})
                    progress.progress(int(index / len(moments) * 100), text=f"Готово клипов: {index} из {len(moments)}")
                session_record = {"id": session_id, "created_at": datetime.now().isoformat(timespec="seconds"), "title": source_title, "source_path": str(source_path), "source_url": vod_url, "duration": duration, "chat_messages": len(chat_records), "clip_length": clip_length, "aspect": aspect, "clips": exported}
                write_json(TWITCH_SESSIONS_DIR / f"{session_id}.json", session_record)
                st.session_state.twitch_last_session = session_id
                st.success(f"Готово: создано {len(exported)} клипов из {len(chat_records):,} сообщений чата.")
            except Exception as exc:
                st.error(f"Не удалось обработать VOD: {exc}")
        # Show current and previously saved Twitch sessions.
        sessions = []
        for path in sorted(TWITCH_SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                sessions.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        selected_session = st.session_state.get("twitch_last_session")
        if sessions:
            st.markdown("---")
            st.markdown("### Готовые клипы")
            for session in sessions[:5]:
                if selected_session and session.get("id") != selected_session and not st.session_state.get("twitch_show_all_sessions", False):
                    continue
                st.caption(f"{session.get('title','Twitch VOD')} · {session.get('chat_messages',0):,} сообщений · {len(session.get('clips',[]))} клипов · {session.get('created_at','')}")
                for clip in session.get("clips", []):
                    file_path = Path(clip.get("file", ""))
                    if not file_path.exists():
                        continue
                    with st.container(border=True):
                        st.markdown(f"**Клип {clip.get('index', '?')}** · {int(clip.get('start',0)//60):02d}:{int(clip.get('start',0)%60):02d} – {int(clip.get('end',0)//60):02d}:{int(clip.get('end',0)%60):02d}")
                        st.caption(f"Чат: {clip.get('messages',0)} сообщений · {clip.get('viewers',0)} участников · оценка активности {clip.get('score',0):.1f}")
                        st.video(str(file_path))
                        st.download_button("⬇ Скачать MP4", data=file_path.read_bytes(), file_name=file_path.name, mime="video/mp4", key=f"tw_dl_{session.get('id')}_{clip.get('index')}")
            if len(sessions) > 1 and selected_session:
                if st.button("Показать все сохранённые сессии", key="tw_show_all_sessions"):
                    st.session_state.twitch_show_all_sessions = True
                    st.rerun()


# ---------- Navigation ----------
NAV = ["Главная", "Новый проект", "Мои проекты", "Мои клипы", "Быстрый редактор", "Twitch Clipper", "Рекламная студия", "Календарь", "Аналитика", "Настройки"]
if "page" not in st.session_state:
    st.session_state.page = "Главная"
if "active_project" not in st.session_state:
    st.session_state.active_project = None

# Apply requested navigation BEFORE creating the sidebar radio widget.
# Streamlit forbids changing a widget's keyed session_state after instantiation.
pending_page = st.session_state.pop("_pending_nav_page", None)
if pending_page in NAV:
    st.session_state.nav_page = pending_page
    st.session_state.page = pending_page

with st.sidebar:
    st.markdown('<div class="nav-brand"><span class="brand-icon">🎬</span> CLIP AI <span style="font-size:11px;color:#B99BFF;border:1px solid #594276;border-radius:6px;padding:2px 6px;">v21</span></div><div class="nav-sub">AI VIDEO WORKSPACE · PREMIUM VIOLET · BY SENYA</div>', unsafe_allow_html=True)
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = st.session_state.page
    page = st.radio("РАБОЧЕЕ ПРОСТРАНСТВО", NAV, index=NAV.index(st.session_state.page), key="nav_page")
    st.session_state.page = page
    st.divider()
    projects_sidebar = load_projects()
    st.caption("ПОСЛЕДНИЙ ПРОЕКТ")
    if projects_sidebar:
        recent = projects_sidebar[0]
        st.markdown(f"**{recent.get('name','Без названия')[:26]}**")
        st.caption(f"{len(recent.get('clips', []))} клипов · {recent.get('status','Проект')}")
        if st.button("Открыть последний проект", use_container_width=True):
            st.session_state.active_project = recent["id"]
            navigate_to("Мои клипы")
            st.rerun()
    else:
        st.caption("Пока нет проектов")
    st.divider()
    st.caption("Обработка выполняется локально на этом компьютере.")
    st.caption("Файлы и история хранятся в папке CLIP AI.")

projects = load_projects()
all_clips = [(p, c) for p in projects for c in p.get("clips", [])]
page = st.session_state.page

def navigate_to(target):
    # Defer the radio's keyed-state update until the next run, before st.radio exists.
    if target not in NAV:
        raise ValueError(f"Неизвестная страница: {target}")
    st.session_state.page = target
    st.session_state._pending_nav_page = target

def page_title(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.markdown("<div style=\"height:5px\"></div>", unsafe_allow_html=True)

def project_selectbox(label="Выбери проект"):
    opts = {f"{p.get('name','Проект')} · {len(p.get('clips',[]))} клипов": p["id"] for p in projects}
    if not opts:
        st.info("Сначала создай проект и сгенерируй клипы.")
        return None
    labels = list(opts.keys())
    current_idx = 0
    if st.session_state.active_project in opts.values():
        current_idx = list(opts.values()).index(st.session_state.active_project)
    chosen = st.selectbox(label, labels, index=current_idx)
    st.session_state.active_project = opts[chosen]
    return opts[chosen]

def detect_source_platform(url):
    """Return a friendly source label without assuming every URL is downloadable."""
    from urllib.parse import urlparse
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    known = {
        "youtube.com":"YouTube", "youtu.be":"YouTube", "m.youtube.com":"YouTube",
        "twitch.tv":"Twitch", "clips.twitch.tv":"Twitch",
        "kick.com":"Kick", "vimeo.com":"Vimeo", "player.vimeo.com":"Vimeo",
        "tiktok.com":"TikTok", "vm.tiktok.com":"TikTok", "instagram.com":"Instagram",
        "facebook.com":"Facebook", "fb.watch":"Facebook", "x.com":"X", "twitter.com":"X",
        "dailymotion.com":"Dailymotion", "dai.ly":"Dailymotion", "rumble.com":"Rumble",
        "reddit.com":"Reddit", "streamable.com":"Streamable", "soundcloud.com":"SoundCloud",
    }
    for domain, label in known.items():
        if host == domain or host.endswith("." + domain):
            return label
    return host or "Внешняя платформа"


def render_progress_card(slot, percent, title, detail="", stage="ОБРАБОТКА", state="running"):
    """Render a compact, readable progress card with the label outside the bar."""
    pct = max(0, min(100, int(round(float(percent)))))
    title_safe = html.escape(str(title))
    detail_safe = html.escape(str(detail))
    stage_safe = html.escape(str(stage))
    state_class = " done" if state == "complete" else (" error" if state == "error" else "")
    value = "✓" if state == "complete" else f"{pct}%"
    fill_color = "linear-gradient(90deg,#4D9B78,#7CC9A0)" if state == "complete" else ""
    fill_style = f"width:{pct}%;" + (f"background:{fill_color};" if fill_color else "")
    foot = "Завершено" if state == "complete" else ("Проверьте сообщение об ошибке ниже" if state == "error" else "Статус обновляется автоматически")
    slot.markdown(
        f'<div class="clip-progress-card{state_class}">'
        f'<div class="clip-progress-head"><div><div class="clip-progress-stage">{stage_safe}</div>'
        f'<div class="clip-progress-title">{title_safe}</div>'
        f'<div class="clip-progress-detail">{detail_safe}</div></div>'
        f'<div class="clip-progress-value">{value}</div></div>'
        f'<div class="clip-progress-track"><div class="clip-progress-fill" style="{fill_style}"></div></div>'
        f'<div class="clip-progress-foot"><span>{foot}</span><span>{pct}%</span></div></div>',
        unsafe_allow_html=True
    )


def render_status_card(slot, title, detail="", state="success"):
    """Render a small state banner that doesn't look like a large alert strip."""
    state = state if state in ("success", "error", "info") else "info"
    icon = "✓" if state == "success" else ("!" if state == "error" else "•")
    slot.markdown(
        f'<div class="clip-status-card {state}"><div class="clip-status-icon">{icon}</div>'
        f'<div><div class="clip-status-title">{html.escape(str(title))}</div>'
        f'<div class="clip-status-detail">{html.escape(str(detail))}</div></div></div>',
        unsafe_allow_html=True
    )


def process_video(uploaded, clip_len, count, language, project_name, youtube_url="", moment_types=None, custom_prompt="", subtitle_style="Классические белые", zoom="Без приближения", cookies_browser="Не использовать"):
    pid = uuid.uuid4().hex[:12]
    folder = project_dir(pid)
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "source.mp4"
    source_name = ""
    status_slot = st.empty()
    render_status_card(status_slot, "Подготавливаем проект", "Проверяем источник и готовим рабочую папку", "info")
    save_slot = st.empty()
    try:
        if uploaded is not None:
            source_name = uploaded.name
            safe_suffix = Path(uploaded.name).suffix.lower() or ".mp4"
            source = folder / ("source" + safe_suffix)
            with source.open("wb") as destination:
                buffer = uploaded.getbuffer()
                total = len(buffer)
                written = 0
                chunk_size = 8 * 1024 * 1024
                render_progress_card(save_slot, 0, "Сохраняем исходник", f"0 из {total/1024/1024:.0f} МБ", "ЗАГРУЗКА ИСХОДНИКА")
                while written < total:
                    end = min(written + chunk_size, total)
                    destination.write(buffer[written:end])
                    written = end
                    mb_done = written / 1024 / 1024
                    mb_total = total / 1024 / 1024
                    render_progress_card(
                        save_slot, written / max(total, 1) * 100,
                        "Сохраняем исходник", f"{mb_done:.0f} из {mb_total:.0f} МБ сохранено",
                        "ЗАГРУЗКА ИСХОДНИКА"
                    )
            del buffer
        else:
            source_url = youtube_url.strip()
            if not re.match(r"^https?://", source_url, re.I):
                raise ValueError("Вставь полную ссылку, начинающуюся с https:// или http://")
            try:
                import yt_dlp
            except ImportError:
                raise RuntimeError("Не установлен универсальный загрузчик yt-dlp. Переустанови CLIP AI v21 или используй локальный файл.")
            platform_name = detect_source_platform(source_url)
            render_status_card(status_slot, f"Подключаемся к {platform_name}", "Проверяем доступность ролика и параметры загрузки", "info")
            ydl_opts = {
                "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/best",
                "merge_output_format": "mp4",
                "outtmpl": str(folder / "source.%(ext)s"),
                "max_filesize": 500 * 1024 * 1024,
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "retries": 3,
                "fragment_retries": 3,
                "continuedl": True,
            }
            if cookies_browser and cookies_browser != "Не использовать":
                ydl_opts["cookiesfrombrowser"] = (cookies_browser.lower(),)
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(source_url, download=False)
                    if info.get("is_live") and not info.get("duration"):
                        raise RuntimeError("Похоже, это прямой эфир. В этой версии поддерживаются записи эфиров (VOD) и клипы, а не бесконечная запись live-трансляции.")
                    if info.get("_type") == "playlist" or info.get("entries") is not None:
                        raise RuntimeError("Это плейлист или подборка. Вставь прямую ссылку на один ролик, VOD или клип.")
                    size_hint = info.get("filesize") or info.get("filesize_approx")
                    if size_hint and size_hint > 500 * 1024 * 1024:
                        raise RuntimeError("Ролик больше лимита 500 МБ. Выбери более короткий фрагмент или загрузи файл меньшего размера.")
                    source_name = (info.get("title") or f"{platform_name} video")[:180]
                    render_status_card(status_slot, "Источник найден · загружаем видео", source_name, "info")
                    downloaded_info = ydl.extract_info(source_url, download=True)
                    downloaded = Path(ydl.prepare_filename(downloaded_info))
                    if not downloaded.exists():
                        candidates_found = sorted(folder.glob("source.*"), key=lambda p:p.stat().st_mtime, reverse=True)
                        if candidates_found:
                            downloaded = candidates_found[0]
                    if not downloaded.exists():
                        raise RuntimeError("Загрузка завершилась, но видеофайл не найден.")
                    source = downloaded
            except Exception as download_error:
                message = str(download_error)
                if "Sign in" in message or "login" in message.lower() or "403" in message:
                    message += "\nЕсли это твой доступный аккаунту ролик, попробуй выбрать браузер с активной авторизацией. Не передавай никому файлы cookies."
                raise RuntimeError(f"Не удалось получить видео с {platform_name}: {message}") from download_error
        if source.stat().st_size > 500 * 1024 * 1024:
            raise ValueError("Исходник больше установленного лимита 500 МБ.")
        size_mb = source.stat().st_size / 1024 / 1024
        render_status_card(status_slot, "Исходник сохранён", f"{source_name or source.name} · {size_mb:.0f} МБ", "success")
        save_slot.empty()
    except Exception as e:
        render_status_card(status_slot, "Не удалось подготовить исходник", str(e), "error")
        st.error(str(e))
        st.info("Используй только материалы, на загрузку и обработку которых у тебя есть права или разрешение. Доступность зависит от платформы, настроек приватности и защиты ролика.")
        return

    media_duration = get_media_duration(source)
    lang = {"Русский":"ru","Английский":"en"}.get(language)
    work_slot = st.empty()
    render_progress_card(work_slot, 3, "Загружаем модель распознавания", "Whisper small · локальная обработка на CPU", "ШАГ 1 ИЗ 4")
    try:
        model = WhisperModel("small", device="cpu", compute_type="int8")
        render_progress_card(work_slot, 7, "Распознаём речь", "Слушаем дорожку и отмечаем таймкоды фраз", "ШАГ 1 ИЗ 4")
        it, info = model.transcribe(str(source), language=lang, vad_filter=True, beam_size=5, word_timestamps=True)
        segs, word_items = [], []
        last_ui_update = 0
        for seg in it:
            segs.append({"start":seg.start,"end":seg.end,"text":seg.text.strip()})
            if seg.words:
                for w in seg.words:
                    word_items.append((w.start,w.end,w.word.strip()))
            if media_duration and seg.end - last_ui_update >= 5:
                pct = min(64, 7 + int(57 * seg.end / max(media_duration, 1)))
                render_progress_card(
                    work_slot, pct, "Распознаём речь",
                    f"Обработано {seg.end/60:.1f} из {media_duration/60:.1f} мин · найдено фраз: {len(segs)}",
                    "ШАГ 1 ИЗ 4"
                )
                last_ui_update = seg.end
        if not segs:
            render_status_card(work_slot, "Речь не распознана", "Проверь, есть ли в исходном видео аудиодорожка", "error")
            st.error("Речь не распознана. Проверь аудиодорожку.")
            return
    except Exception as e:
        render_status_card(work_slot, "Ошибка распознавания", str(e), "error")
        st.error(f"Ошибка распознавания: {e}")
        st.info("Для больших файлов обработка может занять много времени. Не закрывай браузер и окно CMD.")
        return

    duration = max(s["end"] for s in segs)
    render_progress_card(work_slot, 68, "Ищем сильные моменты", "Собираем смысловые фрагменты и убираем повторы", "ШАГ 2 ИЗ 4")
    candidates = choose_clips(segs, duration, clip_len, max(count * 6, 18))
    candidates = apply_moment_intent(candidates, moment_types, custom_prompt)
    if not candidates:
        render_status_card(work_slot, "Подходящих моментов не найдено", "Попробуй увеличить длину клипа или изменить тип моментов", "error")
        st.error("Не удалось найти подходящие фрагменты.")
        return

    api_key = st.session_state.get("clip_ai_api_key", "").strip()
    ai_model = st.session_state.get("clip_ai_model", DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL
    if api_key:
        render_progress_card(work_slot, 72, "AI оценивает кандидатов", f"Сравниваем {len(candidates)} моментов по смыслу, хуку и самостоятельности", "ШАГ 3 ИЗ 4")
        try:
            candidates = ai_rerank_candidates(candidates, api_key, ai_model, moment_types, custom_prompt)
            clips = select_final_candidates(candidates, count)
            render_progress_card(work_slot, 79, "AI-анализ завершён", "Кандидаты ранжированы · выбираем лучшие фрагменты", "ШАГ 3 ИЗ 4")
        except Exception as ai_error:
            st.warning(f"AI-анализ не выполнен: {ai_error}. Используем локальную контекстную оценку.")
            clips = select_final_candidates(candidates, count)
    else:
        clips = select_final_candidates(candidates, count)
        render_progress_card(work_slot, 79, "Локальная оценка завершена", "Выбираем лучшие фрагменты по контексту и качеству речи", "ШАГ 3 ИЗ 4")
        st.info("Используется локальный контекстный анализ. Чтобы включить глубокую AI-оценку, добавь API-ключ в Настройках.")

    if not clips:
        render_status_card(work_slot, "Не удалось выбрать клипы", "Попробуй увеличить длительность клипа или число кандидатов", "error")
        st.error("AI не выбрал подходящие фрагменты. Попробуй увеличить длительность клипа или число кандидатов.")
        return

    clip_records = []
    total_clips = len(clips)
    render_progress_card(work_slot, 80, "Создаём клипы", f"Подготовлено фрагментов: {total_clips} · настраиваем экспорт", "ШАГ 4 ИЗ 4")
    for i, clip in enumerate(clips, 1):
        clip_id = f"{pid}_{i:02d}"
        output = folder / f"clip_{i:02d}.mp4"
        clip["words"] = word_items
        clip["id"] = clip_id
        clip["file"] = str(output)
        clip["settings"] = {"subtitles": True, "subtitle_style": subtitle_style, "zoom": zoom}
        last_rendered = -1
        try:
            def progress(pct, i=i):
                nonlocal last_rendered
                pct = max(0, min(100, int(pct)))
                if pct == 100 or pct - last_rendered >= 3:
                    combined = 80 + 19 * ((i - 1 + pct / 100) / total_clips)
                    render_progress_card(
                        work_slot, combined, f"Создаём клипы · {i} из {total_clips}",
                        f"Экспорт текущего клипа · {pct}%",
                        "ШАГ 4 ИЗ 4"
                    )
                    last_rendered = pct
            warning = export_clip(source, clip, clip["settings"], output, progress_callback=progress)
            clip_records.append({
                "id": clip_id, "start": float(clip["start"]), "end": float(clip["end"]),
                "text": clip["text"], "score": float(clip["score"]), "context_score": int(clip.get("context_score", 0)), "score_reason": clip.get("score_reason", ""), "ai_score": clip.get("ai_score"), "ai_title": clip.get("ai_title", ""), "ai_hook": clip.get("ai_hook", ""), "ai_reason": clip.get("ai_reason", ""), "ai_weakness": clip.get("ai_weakness", ""), "file": str(output),
                "settings": clip["settings"], "warning": warning or "", "words": word_items
            })
        except Exception as e:
            st.warning(f"Клип {i} не создан: {e}")
        completed_pct = 80 + 19 * (i / total_clips)
        render_progress_card(work_slot, completed_pct, "Создаём клипы", f"Готово {i} из {total_clips} · успешно сохранено {len(clip_records)}", "ШАГ 4 ИЗ 4")

    render_progress_card(work_slot, 100, "Обработка завершена", f"Создано клипов: {len(clip_records)} · проект готов к просмотру", "ГОТОВО", "complete")
    project = {
        "id": pid, "name": project_name.strip() or (Path(uploaded.name).stem if uploaded is not None else (source_name or "YouTube project")),
        "source_name": source_name or (uploaded.name if uploaded is not None else "YouTube video"), "source_path": str(source),
        "source_url": youtube_url.strip() if youtube_url else "", "source_platform": detect_source_platform(youtube_url) if youtube_url else "Локальный файл", "creation_preferences": {"moment_types": moment_types or ["Лучшее"], "custom_prompt": custom_prompt, "clip_length": clip_len, "clip_count": count, "language": language, "subtitle_style": subtitle_style, "zoom": zoom},
        "source_size": source.stat().st_size, "duration": float(media_duration or duration),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "status": "Обработан", "clips": clip_records
    }
    save_project(project)
    st.session_state.active_project = pid
    st.success(f"Готово! Создано клипов: {len(clip_records)}")
    navigate_to("Мои клипы")
    st.rerun()

# ---------- Home ----------
if page == "Главная":
    ads_count = len(read_json(ADS_FILE, []))
    calendar_count = len(read_json(CALENDAR_FILE, []))
    st.markdown(
        '<div class="v12-hero">'
        '<div class="v12-kicker">CLIP AI · AI VIDEO WORKSPACE</div>'
        '<div class="v12-hero-title">Твоя видеостудия.<br>От идеи до готового Shorts.</div>'
        '<div class="v12-hero-copy">Создавай проекты из длинных видео, находи сильные моменты, редактируй клипы, готовь рекламные интеграции и планируй публикации — в одном рабочем пространстве.</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.write("")
    stat_cols = st.columns(4)
    stat_values = [
        ("Проекты", str(len(projects)), "Локальная библиотека"),
        ("Готовые клипы", str(len(all_clips)), "Создано на этом компьютере"),
        ("Рекламные черновики", str(ads_count), "Сохранённые сценарии"),
        ("Публикации", str(calendar_count), "Записи в календаре"),
    ]
    for col, (label, value, note) in zip(stat_cols, stat_values):
        with col:
            st.markdown(
                f'<div class="v12-stat"><div class="v12-stat-label">{label}</div>'
                f'<div class="v12-stat-value">{value}</div><div class="v12-stat-note">{note}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown('<div class="v12-section-title">Рабочие модули</div>', unsafe_allow_html=True)
    modules = [
        ("🧠", "Новый проект", "Загрузи длинное видео и найди потенциально сильные фрагменты.", "Новый проект"),
        ("🎞️", "Мои клипы", "Просматривай, настраивай субтитры и приближение, экспортируй MP4.", "Мои клипы"),
        ("🎮", "Twitch Clipper", "Лови хайлайты по реакциям чата в LIVE и нарезай VOD.", "Twitch Clipper"),
        ("📣", "Рекламная студия", "Собирай сценарии баннеров, рекламного звука и пауз.", "Рекламная студия"),
        ("🗓️", "Календарь", "Планируй публикации и следи за датами выхода роликов.", "Календарь"),
    ]
    module_cols = st.columns(5)
    for col, (icon, title, desc, target) in zip(module_cols, modules):
        with col:
            st.markdown(
                f'<div class="v12-module"><div class="v12-module-icon">{icon}</div>'
                f'<div class="v12-module-title">{title}</div><div class="v12-module-copy">{desc}</div></div>',
                unsafe_allow_html=True
            )
            if st.button("Открыть раздел  →", key=f"home_v12_{target}", use_container_width=True):
                navigate_to(target)
                st.rerun()

    left, right = st.columns([1.65, 1], gap="large")
    with left:
        st.markdown('<div class="v12-section-title">Последние проекты</div>', unsafe_allow_html=True)
        if not projects:
            with st.container(border=True):
                st.markdown("**Здесь появятся твои проекты**")
                st.caption("Загрузи первое длинное видео — CLIP AI сохранит исходник и созданные клипы в локальной библиотеке.")
                if st.button("＋ Создать первый проект", type="primary", use_container_width=True):
                    navigate_to("Новый проект")
                    st.rerun()
        else:
            for project_item in projects[:4]:
                with st.container(border=True):
                    a, b = st.columns([4, 1])
                    with a:
                        st.markdown(f'<div class="v12-project-title">{html.escape(project_item.get("name", "Без названия"))}</div>', unsafe_allow_html=True)
                        st.markdown(
                            f'<div class="v12-project-meta">{html.escape(project_item.get("source_name", ""))} · '
                            f'{len(project_item.get("clips", []))} клипов · {html.escape(project_item.get("status", "Проект"))}</div>',
                            unsafe_allow_html=True
                        )
                    with b:
                        if st.button("Открыть", key=f"openhome_v12_{project_item['id']}", use_container_width=True):
                            st.session_state.active_project = project_item["id"]
                            navigate_to("Мои клипы")
                            st.rerun()
    with right:
        st.markdown('<div class="v12-section-title">Быстрые действия</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("**Начать новый монтаж**")
            st.caption("Перейди к загрузке исходного видео и настрой длительность будущих клипов.")
            if st.button("＋ Загрузить видео", key="quick_upload_v12", use_container_width=True):
                navigate_to("Новый проект")
                st.rerun()
            st.divider()
            st.markdown("**Подготовить рекламную интеграцию**")
            st.caption(f"Сохранено рекламных сценариев: {ads_count}")
            if st.button("Открыть рекламную студию", key="quick_ads_v12", use_container_width=True):
                navigate_to("Рекламная студия")
                st.rerun()
            st.divider()
            st.markdown("**Запланировать публикацию**")
            st.caption(f"Записей в календаре: {calendar_count}")
            if st.button("Открыть календарь", key="quick_calendar_v12", use_container_width=True):
                navigate_to("Календарь")
                st.rerun()

# ---------- New project / Creation studio ----------
elif page == "Новый проект":
    st.markdown(
        '<div class="create-hero"><div class="create-kicker">CLIP AI · CREATION STUDIO · V21</div>'
        '<div class="create-title">Создавай короткие ролики</div>'
        '<div class="create-copy">Преврати длинное видео в самостоятельные Shorts. Выбери источник, настрой типы моментов и оформление — CLIP AI найдёт фрагменты с учётом контекста разговора.</div></div>',
        unsafe_allow_html=True
    )
    # User-owned templates live in data/ and are never overwritten by app updates.
    saved_templates = read_json(TEMPLATES_FILE, [])
    default_templates = {
        "Универсальный старт": {"moments":["Лучшее","Ключевые выводы","Лучшие истории"],"length":45,"count":5,"style":"Классические белые","zoom":"Без приближения"},
        "Горячие дискуссии": {"moments":["Горячие мнения","Лучшее"],"length":30,"count":7,"style":"Контрастные","zoom":"Лёгкое приближение"},
        "Истории и факты": {"moments":["Лучшие истории","Удивительные факты"],"length":60,"count":5,"style":"Подкаст","zoom":"Без приближения"},
        "Юмор и реакции": {"moments":["Забавные моменты","Лучшее"],"length":30,"count":8,"style":"Кинетические (одно слово)","zoom":"Лёгкое приближение"},
    }
    top_a, top_b = st.columns([2,1])
    with top_a:
        project_name = st.text_input("Название проекта", placeholder="Например: Подкаст — выпуск 12", key="v15_project_name")
    with top_b:
        template_names = list(default_templates) + [t.get("name", "Мой шаблон") for t in saved_templates]
        selected_template = st.selectbox("Быстрый старт · шаблон", ["Без шаблона"] + template_names, key="v15_template_pick")
    if selected_template != "Без шаблона":
        if selected_template in default_templates:
            template_data = default_templates[selected_template]
        else:
            template_data = next((t for t in saved_templates if t.get("name") == selected_template), {})
        st.session_state["v15_loaded_template"] = template_data
    preset = st.session_state.get("v15_loaded_template", {})
    if st.session_state.get("_v15_applied_template") != selected_template and selected_template != "Без шаблона":
        st.session_state["v15_moment_types"] = [x for x in preset.get("moments", ["Лучшее"]) if x in ["Лучшее", "Горячие мнения", "Забавные моменты", "Ключевые выводы", "Лучшие истории", "Удивительные факты"]] or ["Лучшее"]
        st.session_state["v15_clip_len"] = preset.get("length", 45)
        st.session_state["v15_clip_count"] = preset.get("count", 5)
        st.session_state["v15_subtitle_style"] = preset.get("style", "Классические белые")
        st.session_state["v15_zoom"] = preset.get("zoom", "Без приближения")
        st.session_state["_v15_applied_template"] = selected_template

    st.markdown('<div class="create-step">01 · Исходное видео</div>', unsafe_allow_html=True)
    source_mode = st.radio("Источник видео", ["Ссылка на платформу", "Файл с компьютера"], horizontal=True, key="v16_source_mode")
    youtube_url = ""
    uploaded = None
    cookies_browser = "Не использовать"
    if source_mode == "Ссылка на платформу":
        youtube_url = st.text_input("Вставь ссылку на видео, VOD или клип", placeholder="Twitch, YouTube, Kick, Vimeo, TikTok, Instagram…", key="v16_source_url")
        st.caption("Поддерживаются сайты из списка yt-dlp: Twitch VOD/Clips, YouTube, Kick, Vimeo, TikTok, Instagram, Facebook, X, Dailymotion, Rumble, Reddit и другие. Фактическая доступность зависит от правил и защиты площадки.")
        with st.expander("Дополнительно · доступ к роликам с авторизацией"):
            cookies_browser = st.selectbox("Использовать активную авторизацию браузера", ["Не использовать", "Chrome", "Edge", "Firefox", "Brave", "Opera", "Vivaldi"], key="v16_cookies_browser", help="Используй только собственный профиль и только для роликов, к которым у тебя есть законный доступ. Пароли и cookies приложение не сохраняет.")
            st.caption("Если ролик доступен только после входа, yt-dlp может попробовать прочитать авторизацию выбранного браузера на этом компьютере. Браузер иногда потребуется закрыть.")
    else:
        uploaded = st.file_uploader("Перетащи видео или выбери файл · до 500 МБ", type=["mp4","mov","mkv","webm"], key="v15_upload")
        if uploaded:
            size_mb = len(uploaded.getbuffer()) / 1024 / 1024
            st.caption(f"{uploaded.name} · {size_mb:.1f} МБ")
            st.video(uploaded)

    st.markdown('<div class="create-step">02 · Какие моменты искать</div>', unsafe_allow_html=True)
    moment_options = ["Лучшее", "Горячие мнения", "Забавные моменты", "Ключевые выводы", "Лучшие истории", "Удивительные факты"]
    default_moments = preset.get("moments", ["Лучшее"])
    valid_defaults = [x for x in default_moments if x in moment_options] or ["Лучшее"]
    moment_types = st.multiselect("Типы моментов", moment_options, default=valid_defaults, key="v15_moment_types", help="Можно выбрать несколько категорий одновременно.")
    custom_prompt = st.text_area("Свой запрос к AI (необязательно)", placeholder="Например: Найди момент, где гость резко спорит с ведущим и приводит конкретный пример.", height=85, key="v15_custom_prompt")
    st.caption("Свой запрос и выбранные категории учитываются при ранжировании. С OpenAI API доступна более глубокая смысловая интерпретация; без API работает локальная оценка по тексту.")

    st.markdown('<div class="create-step">03 · Формат и оформление</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1:
        clip_len = st.selectbox("Длительность одного клипа", [15,20,30,45,60,90], index=[15,20,30,45,60,90].index(preset.get("length",45)) if preset.get("length",45) in [15,20,30,45,60,90] else 3, format_func=lambda x:f"{x} секунд", key="v15_clip_len")
    with c2:
        count = st.slider("Количество клипов",1,20,int(preset.get("count",5)), key="v15_clip_count")
    with c3:
        language = st.selectbox("Язык речи",["Авто","Русский","Английский"], key="v15_language")
    c4,c5 = st.columns(2)
    style_options = ["Классические белые","Жёлтое выделение","Минималистичные","Кинетические (одно слово)","Неоновые","Контрастные","Подкаст","Компактные","Розовый акцент","Зелёный акцент"]
    with c4:
        default_style = preset.get("style", "Классические белые")
        subtitle_style = st.selectbox("Стиль субтитров", style_options, index=style_options.index(default_style) if default_style in style_options else 0, key="v15_subtitle_style")
    with c5:
        zoom_options = ["Без приближения","Лёгкое приближение","Сильное приближение"]
        default_zoom = preset.get("zoom", "Без приближения")
        zoom = st.selectbox("Приближение", zoom_options, index=zoom_options.index(default_zoom) if default_zoom in zoom_options else 0, key="v15_zoom")
    st.markdown('<div class="create-note">✨ <b>Как работает отбор:</b> CLIP AI сначала находит кандидатов по расшифровке речи, затем проверяет цельность мысли и соседний контекст. Если подключён OpenAI API, кандидаты дополнительно оцениваются по хуку, конфликту, эмоции, конкретике и развязке. Оценка не гарантирует вирусность.</div>', unsafe_allow_html=True)

    with st.expander("＋ Сохранить текущие настройки как мой шаблон"):
        template_name = st.text_input("Название шаблона", placeholder="Например: Подкаст — горячие мнения", key="v15_template_name")
        if st.button("Сохранить шаблон", key="v15_save_template", use_container_width=True):
            if not template_name.strip():
                st.warning("Введи название шаблона.")
            else:
                saved_templates = [t for t in saved_templates if t.get("name") != template_name.strip()]
                saved_templates.append({"name":template_name.strip(),"moments":moment_types or ["Лучшее"],"length":clip_len,"count":count,"style":subtitle_style,"zoom":zoom})
                write_json(TEMPLATES_FILE, saved_templates)
                st.success("Шаблон сохранён в локальной библиотеке.")
                st.rerun()

    source_ready = bool(uploaded) if source_mode == "Файл с компьютера" else bool(youtube_url.strip())
    if uploaded and len(uploaded.getbuffer()) > 500 * 1024 * 1024:
        st.error("Файл больше установленного лимита 500 МБ.")
        source_ready = False
    if st.button("✨ Найти лучшие моменты и создать клипы", type="primary", use_container_width=True, disabled=not source_ready or not moment_types):
        process_video(uploaded, clip_len, count, language, project_name, youtube_url, moment_types, custom_prompt, subtitle_style, zoom, cookies_browser)

# ---------- Projects ----------
elif page == "Мои проекты":
    page_title("📁 Мои проекты", "Все исходные видео и результаты обработки сохраняются локально.")
    if st.button("＋ Новый проект", type="primary"):
        navigate_to("Новый проект")
        st.rerun()
    projects = load_projects()
    if not projects:
        st.info("Проектов пока нет.")
    else:
        for p in projects:
            with st.container(border=True):
                a,b,c = st.columns([3,1,1])
                a.markdown(f"### {p.get('name','Без названия')}")
                a.caption(f"{p.get('source_name','')} · {p.get('source_size',0)/1024/1024:.1f} МБ · {len(p.get('clips',[]))} клипов")
                b.caption(datetime.fromisoformat(p["created_at"]).strftime("%d.%m.%Y %H:%M") if p.get("created_at") else "")
                if c.button("Открыть клипы", key=f"proj_{p['id']}"):
                    st.session_state.active_project = p["id"]
                    navigate_to("Мои клипы")
                    st.rerun()
                with st.expander("Информация об исходнике"):
                    st.write(f"Путь: `{p.get('source_path','')}`")
                    st.write(f"Длительность: {p.get('duration',0)/60:.1f} мин")

# ---------- Clip library ----------
elif page == "Мои клипы":
    page_title("🎞️ Мои клипы", "Просматривай результаты, меняй оформление и скачивай ролики.")
    pid = project_selectbox()
    if pid:
        project = load_project(pid)
        st.markdown(f"### {project.get('name','Проект')}")
        st.caption(f"{project.get('source_name','')} · {len(project.get('clips',[]))} клипов")
        if not project.get("clips"):
            st.info("В проекте пока нет готовых клипов.")
        for idx, clip in enumerate(project.get("clips", [])):
            with st.container(border=True):
                left,right = st.columns([1,2])
                with left:
                    clip_path = Path(clip["file"])
                    if clip_path.exists():
                        st.video(str(clip_path), width=230)
                    else:
                        st.warning("Файл клипа не найден.")
                with right:
                    st.markdown(f"### Клип {idx+1}")
                    st.caption(f"{int(clip['start']//60):02d}:{int(clip['start']%60):02d} – {int(clip['end']//60):02d}:{int(clip['end']%60):02d} · {clip['end']-clip['start']:.1f} сек.")
                    context_score = int(clip.get("context_score", min(100, max(0, round(clip.get("score", 0) * 25)))))
                    score_reason = html.escape(clip.get("ai_reason") or clip.get("score_reason", "Оценка по структуре и содержанию распознанной речи"))
                    score_mode = "DEEP AI ANALYSIS" if clip.get("ai_score") is not None else "LOCAL CONTEXT ANALYSIS"
                    st.markdown(
                        f'<div class="context-score-card"><div class="context-score-ring">{context_score}<small>/100</small></div>'
                        f'<div><div class="context-score-title">Потенциал клипа · {score_mode}</div>'
                        f'<div class="context-score-copy">{score_reason}<br>Это оценка потенциала, а не гарантия просмотров.</div></div></div>',
                        unsafe_allow_html=True
                    )
                    if clip.get("ai_title"):
                        st.markdown(f"**AI-заголовок:** {html.escape(clip['ai_title'])}")
                    if clip.get("ai_hook"):
                        st.caption(f"Хук: {clip['ai_hook']}")
                    if clip.get("ai_weakness"):
                        st.caption(f"Что можно улучшить: {clip['ai_weakness']}")
                    st.write(clip.get("text","")[:900])
                    settings = clip.setdefault("settings", {"subtitles":True,"subtitle_style":"Классические белые","zoom":"Без приближения"})
                    with st.expander("✏️ Редактировать клип"):
                        sub = st.toggle("Субтитры", value=settings.get("subtitles",True), key=f"sub_{clip['id']}")
                        style_opts = ["Классические белые","Жёлтое выделение","Минималистичные","Кинетические (одно слово)","Неоновые","Контрастные","Подкаст","Компактные","Розовый акцент","Зелёный акцент"]
                        style = st.selectbox("Стиль субтитров", style_opts, index=style_opts.index(settings.get("subtitle_style","Классические белые")), key=f"sty_{clip['id']}")
                        zoom_opts = ["Без приближения","Лёгкое приближение","Сильное приближение"]
                        zoom = st.selectbox("Приближение", zoom_opts, index=zoom_opts.index(settings.get("zoom","Без приближения")), key=f"zm_{clip['id']}")
                        if st.button("Применить и пересоздать", key=f"regen_{clip['id']}", use_container_width=True):
                            clip["settings"] = {"subtitles":sub,"subtitle_style":style,"zoom":zoom}
                            source = Path(project["source_path"])
                            if not source.exists():
                                st.error("Исходный файл проекта не найден.")
                            else:
                                with st.spinner("Пересоздаём клип…"):
                                    warning = export_clip(source, clip, clip["settings"], Path(clip["file"]))
                                project["clips"][idx] = clip
                                save_project(project)
                                if warning: st.warning(warning)
                                else: st.success("Клип обновлён.")
                                st.rerun()
                    shortcut_col, download_col = st.columns([1, 1])
                    if shortcut_col.button("⚡ Быстрые правки", key=f"quick_edit_{clip['id']}", use_container_width=True):
                        st.session_state.active_project = pid
                        st.session_state.quick_editor_clip_id = clip["id"]
                        navigate_to("Быстрый редактор")
                        st.rerun()
                    if clip_path.exists():
                        download_col.download_button("⬇ Скачать MP4", clip_path.read_bytes(), file_name=clip_path.name, mime="video/mp4", key=f"download_{clip['id']}", use_container_width=True)
                    if clip.get("warning"):
                        st.warning(clip["warning"])


# ---------- Quick Shorts Editor ----------
elif page == "Быстрый редактор":
    page_title("⚡ Быстрый редактор", "Быстро подправь готовый Shorts и сохрани отдельную версию — оригинал останется нетронутым.")
    pid = project_selectbox("Выбери проект")
    project = load_project(pid) if pid else None
    clips = project.get("clips", []) if project else []
    if project and not clips:
        st.info("В этом проекте пока нет готовых клипов. Сначала создай нарезки в разделе «Новый проект».")
    elif project and clips:
        clip_labels = {f"Клип {i+1} · {max(0.0, float(c.get('end', 0))-float(c.get('start', 0))):.1f} сек.": c for i, c in enumerate(clips)}
        label_list = list(clip_labels.keys())
        requested_id = st.session_state.get("quick_editor_clip_id")
        requested_index = next((i for i, c in enumerate(clips) if c.get("id") == requested_id), 0)
        chosen_label = st.selectbox("Выбери Shorts для правок", label_list, index=min(requested_index, len(label_list)-1), key="quick_editor_clip_pick")
        clip = clip_labels[chosen_label]
        clip_file = Path(clip.get("file", ""))
        versions = [v for v in clip.get("edited_versions", []) if Path(v.get("file", "")).exists()]
        source_choices = ["Исходный клип"] + (["Последняя редакция"] if versions else [])
        version_choice = st.selectbox("С чего начать", source_choices, key=f"qe_version_{clip.get('id')}")
        input_file = Path(versions[-1]["file"]) if version_choice == "Последняя редакция" and versions else clip_file
        if not input_file.exists():
            st.error("Файл клипа не найден. Проверь, не удалён ли он из папки проекта.")
        else:
            media_duration = get_media_duration(input_file)
            media_duration = float(media_duration or (float(clip.get("end", 30))-float(clip.get("start", 0))))
            media_duration = max(0.5, media_duration)
            preview_col, settings_col = st.columns([1, 1.25], gap="large")
            with preview_col:
                st.markdown("#### Предпросмотр")
                st.video(str(input_file), width=320)
                st.caption(f"{input_file.name} · {media_duration:.1f} секунд")
                if versions:
                    latest = versions[-1]
                    st.caption(f"Последняя редакция: {Path(latest['file']).name}")
            with settings_col:
                st.markdown("#### Быстрые настройки")
                trim_start, trim_end = st.slider(
                    "Обрезка · начало и конец", min_value=0.0, max_value=float(media_duration),
                    value=(0.0, float(media_duration)), step=0.1, key=f"qe_trim_{clip.get('id')}"
                )
                aspect_label = st.selectbox("Формат кадра", [
                    "Вертикальный 9:16 (Shorts/Reels/TikTok)",
                    "Горизонтальный 16:9 (YouTube)",
                    "Квадратный 1:1"
                ], key=f"qe_aspect_{clip.get('id')}")
                speed_label = st.selectbox("Скорость", ["0,5×", "0,75×", "1× · обычная", "1,25×", "1,5×", "2×"], index=2, key=f"qe_speed_{clip.get('id')}")
                speed = {"0,5×":0.5, "0,75×":0.75, "1× · обычная":1.0, "1,25×":1.25, "1,5×":1.5, "2×":2.0}[speed_label]
                original_volume = st.slider("Громкость исходного звука", 0, 150, 100, 5, key=f"qe_orig_vol_{clip.get('id')}")
                fade_edges = st.checkbox("Плавное появление и затухание", value=False, key=f"qe_fade_{clip.get('id')}")

            with st.expander("＋ Добавить текст на видео", expanded=False):
                overlay_text = st.text_area("Текст (необязательно)", max_chars=180, placeholder="Например: ЭТО ПОВОРОТНЫЙ МОМЕНТ…", key=f"qe_text_{clip.get('id')}")
                t1, t2, t3 = st.columns(3)
                overlay_size = t1.select_slider("Размер", options=[32, 40, 48, 54, 62, 70], value=54, key=f"qe_text_size_{clip.get('id')}")
                overlay_position = t2.selectbox("Положение", ["Сверху", "По центру", "Снизу"], index=2, key=f"qe_text_position_{clip.get('id')}")
                overlay_color = t3.selectbox("Цвет", ["Белый", "Жёлтый", "Розовый"], key=f"qe_text_color_{clip.get('id')}")

            with st.expander("♫ Добавить фоновую музыку", expanded=False):
                music_upload = st.file_uploader("Аудиофайл MP3, WAV, M4A или AAC", type=["mp3", "wav", "m4a", "aac", "flac", "ogg"], key=f"qe_music_{clip.get('id')}")
                music_volume = st.slider("Громкость музыки", 0, 100, 25, 5, key=f"qe_music_vol_{clip.get('id')}")
                if music_upload:
                    st.caption(f"Загружено: {music_upload.name}")

            st.caption("Редактор применяет обрезку, формат, скорость, громкость, текст и музыку при экспорте. Исходный клип не перезаписывается.")
            if st.button("✨ Применить правки и экспортировать MP4", type="primary", use_container_width=True, key=f"qe_export_{clip.get('id')}"):
                if trim_end - trim_start < 0.5:
                    st.error("Выбери отрезок не короче 0,5 секунды.")
                else:
                    project_folder = project_dir(pid)
                    edited_folder = project_folder / "edited_versions"
                    edited_folder.mkdir(exist_ok=True, parents=True)
                    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = edited_folder / f"{Path(clip_file).stem}_edited_{stamp}.mp4"
                    music_path = None
                    try:
                        if music_upload:
                            music_ext = Path(music_upload.name).suffix.lower() or ".mp3"
                            music_path = edited_folder / f"music_temp_{uuid.uuid4().hex[:8]}{music_ext}"
                            music_path.write_bytes(music_upload.getbuffer())
                        with st.spinner("Собираем твою редакцию…"):
                            export_quick_edit(
                                input_file, output_path, trim_start, trim_end, aspect_label,
                                speed, original_volume, music_path, music_volume,
                                overlay_text, overlay_size, overlay_position, overlay_color, fade_edges
                            )
                        clip.setdefault("edited_versions", []).append({
                            "file": str(output_path), "created_at": datetime.now().isoformat(timespec="seconds"),
                            "source_file": str(input_file), "trim_start": float(trim_start), "trim_end": float(trim_end),
                            "aspect": aspect_label, "speed": speed, "text": overlay_text,
                        })
                        project["clips"] = [clip if c.get("id") == clip.get("id") else c for c in project.get("clips", [])]
                        save_project(project)
                        st.session_state.quick_editor_last_export = str(output_path)
                        st.success("Готово! Отредактированный MP4 сохранён отдельным файлом.")
                        st.video(str(output_path), width=320)
                        st.download_button("⬇ Скачать отредактированный MP4", output_path.read_bytes(),
                                            file_name=output_path.name, mime="video/mp4", key=f"qe_download_{clip.get('id')}_{stamp}")
                    except Exception as exc:
                        st.error(f"Не удалось экспортировать видео: {exc}")
                    finally:
                        if music_path and Path(music_path).exists():
                            try: Path(music_path).unlink()
                            except Exception: pass
            if versions:
                with st.expander("Готовые редакции этого клипа", expanded=False):
                    for version_index, version in enumerate(reversed(versions), 1):
                        version_path = Path(version["file"])
                        a, b = st.columns([3, 1])
                        a.caption(f"{version_index}. {version_path.name} · {version.get('created_at','')}")
                        if version_path.exists():
                            b.download_button("Скачать", version_path.read_bytes(), file_name=version_path.name,
                                              mime="video/mp4", key=f"qe_old_download_{clip.get('id')}_{version_index}")
    else:
        st.info("Сначала создай проект и клипы — после этого они появятся здесь для быстрых правок.")


# ---------- Ad Studio ----------
elif page == "Twitch Clipper":
    render_twitch_clipper_page()

elif page == "Рекламная студия":
    page_title("📣 Рекламная студия", "Подготовка рекламных вставок и сценариев размещения внутри коротких видео.")
    projects = load_projects()
    if not projects:
        st.info("Сначала создай проект и клипы. Здесь можно будет выбрать ролик для рекламной интеграции.")
    else:
        pid = project_selectbox("Выбери проект для рекламы")
        project = load_project(pid) if pid else None
        clips = project.get("clips",[]) if project else []
        if clips:
            labels = {f"Клип {i+1} · {c['end']-c['start']:.1f} сек.":c for i,c in enumerate(clips)}
            selected_label = st.selectbox("Выбери клип", list(labels))
            selected_clip = labels[selected_label]
            col1,col2 = st.columns([1,1])
            with col1:
                st.markdown("**Исходный клип**")
                if Path(selected_clip["file"]).exists(): st.video(selected_clip["file"], width=230)
            with col2:
                st.markdown("**Параметры рекламной паузы**")
                ad_name = st.text_input("Название интеграции", placeholder="Например: Реклама партнёра")
                ad_mode = st.selectbox("Формат", ["Стоп-кадр + баннер","Полноэкранная рекламная пауза","Баннер поверх видео"])
                ad_at = st.number_input("Момент появления (секунда клипа)", min_value=0.0, max_value=float(max(0.0,selected_clip["end"]-selected_clip["start"])), value=min(10.0,float(max(0.0,selected_clip["end"]-selected_clip["start"]))), step=0.5)
                ad_duration = st.selectbox("Длительность рекламы", [3,5,7,10,15], index=1, format_func=lambda x:f"{x} секунд")
                pause_original = st.selectbox("Звук основного видео", ["Приглушить","Выключить","Оставить как есть"])
                ad_position = st.select_slider("Положение баннера в кадре", options=["Выше","По центру","Ниже"], value="Ниже")
                ad_scale = st.slider("Размер баннера", 35, 100, 78, 5, format="%d%%")
                banner = st.file_uploader("Баннер / логотип", type=["png","jpg","jpeg"], key="ad_banner")
                audio = st.file_uploader("Звук рекламы", type=["mp3","wav","m4a","aac"], key="ad_audio")
                ad_copy = st.text_area("Текст на баннере", placeholder="Название бренда, предложение, промокод…")
            st.markdown("#### Предпросмотр рекламной вставки")
            preview_col, preview_info = st.columns([1,1])
            with preview_col:
                st.markdown('<div class="ad-preview-shell">', unsafe_allow_html=True)
                st.caption(f"Позиция: {ad_position.lower()} · появление: {ad_at:.1f} сек. · длительность: {ad_duration} сек.")
                preview_image = None
                if Path(selected_clip["file"]).exists():
                    preview_image = render_ad_preview_frame(
                        selected_clip["file"], ad_at,
                        banner.getvalue() if banner else None,
                        ad_copy, ad_position, ad_scale
                    )
                if preview_image is not None:
                    st.image(preview_image, caption="Стоп-кадр с примерным размещением рекламы", use_container_width=True)
                elif Path(selected_clip["file"]).exists():
                    st.video(selected_clip["file"], width=230)
                    st.caption("Не удалось собрать стоп-кадр предпросмотра на этом компьютере.")
                st.markdown('</div>', unsafe_allow_html=True)
            with preview_info:
                st.markdown("**Как будет работать вставка**")
                st.write(f"• В точке {ad_at:.1f} сек. клип поставится на паузу.")
                st.write(f"• Баннер появится: {ad_position.lower()}.")
                st.write(f"• Основной звук: {pause_original.lower()}.")
                st.write(f"• Рекламный блок: {ad_duration} сек.")
                if audio:
                    st.audio(audio, format=audio.type)
                else:
                    st.caption("Добавь аудиофайл, чтобы прослушать рекламный звук.")
            st.warning("Сейчас можно настроить и сохранить макет рекламной вставки с позицией и размером. Финальное встраивание стоп-кадра, наложение баннера и микширование двух аудиодорожек в MP4 пока не подключено.")

            if st.button("Сохранить рекламный сценарий", type="primary"):
                ads = read_json(ADS_FILE, [])
                ad_id = uuid.uuid4().hex[:10]
                ad_dir = DATA / "ads" / ad_id
                ad_dir.mkdir(parents=True, exist_ok=True)
                banner_path = ""
                audio_path = ""
                if banner:
                    banner_path = str(ad_dir / banner.name)
                    (ad_dir / banner.name).write_bytes(banner.getbuffer())
                if audio:
                    audio_path = str(ad_dir / audio.name)
                    (ad_dir / audio.name).write_bytes(audio.getbuffer())
                ads.append({
                    "id":ad_id,"name":ad_name or "Рекламная интеграция","project_id":pid,
                    "clip_id":selected_clip["id"],"mode":ad_mode,"at":ad_at,"duration":ad_duration,
                    "original_audio":pause_original,"position":ad_position,"scale":ad_scale,"banner_path":banner_path,"audio_path":audio_path,
                    "copy":ad_copy,"created_at":datetime.now().isoformat(timespec="seconds")
                })
                write_json(ADS_FILE, ads)
                st.success("Рекламный сценарий сохранён.")
        ads = read_json(ADS_FILE, [])
        st.subheader("Сохранённые рекламные сценарии")
        if not ads:
            st.caption("Пока нет рекламных сценариев.")
        for ad in reversed(ads):
            with st.container(border=True):
                st.markdown(f"**{ad.get('name','Реклама')}**")
                st.caption(f"{ad.get('mode')} · {ad.get('at')} сек. · пауза {ad.get('duration')} сек.")
                st.write(ad.get("copy",""))

# ---------- Calendar ----------
elif page == "Календарь":
    page_title("🗓️ Календарь публикаций", "Планируй выход Shorts по датам и площадкам. Автопубликация пока не подключена.")
    events = read_json(CALENDAR_FILE, [])
    with st.container(border=True):
        st.subheader("Добавить публикацию")
        with st.form("calendar_form"):
            title = st.text_input("Название ролика")
            platform = st.selectbox("Площадка", ["YouTube Shorts","Instagram Reels","TikTok","Facebook","Другое"])
            publish_date = st.date_input("Дата публикации", value=date.today())
            publish_time = st.time_input("Время публикации", value=time(18,0))
            status = st.selectbox("Статус", ["Идея","Черновик","Запланировано","Опубликовано"])
            note = st.text_input("Заметка / ссылка (необязательно)")
            submitted = st.form_submit_button("＋ Добавить в календарь", type="primary")
            if submitted:
                if not title.strip():
                    st.error("Добавь название ролика.")
                else:
                    events.append({"id":uuid.uuid4().hex[:10],"title":title,"platform":platform,"date":publish_date.isoformat(),"time":publish_time.strftime("%H:%M"),"status":status,"note":note})
                    write_json(CALENDAR_FILE, events)
                    st.success("Публикация добавлена в календарь.")
                    st.rerun()
    events = sorted(events, key=lambda e:(e.get("date",""),e.get("time","")))
    st.subheader("Расписание")
    if not events:
        st.info("Пока нет запланированных публикаций.")
    else:
        for event in events:
            with st.container(border=True):
                a,b,c = st.columns([3,2,1])
                a.markdown(f"**{event['title']}**")
                a.caption(f"{event['platform']} · {event.get('note','')}")
                b.write(f"{event['date']} · {event['time']}")
                b.caption(event["status"])
                if c.button("Удалить", key=f"del_event_{event['id']}"):
                    events = [x for x in events if x["id"] != event["id"]]
                    write_json(CALENDAR_FILE, events)
                    st.rerun()
    st.subheader("Месячный обзор")
    if events:
        for event in events:
            st.write(f"**{event['date']}** · {event['time']} — {event['title']} ({event['platform']})")

# ---------- Analytics ----------
elif page == "Аналитика":
    page_title("📊 Аналитика", "Локальная статистика работы CLIP AI. Метрики просмотров появятся при подключении платформ.")
    projects = load_projects()
    clips = [(p,c) for p in projects for c in p.get("clips",[])]
    c1,c2,c3 = st.columns(3)
    c1.metric("Проекты",len(projects))
    c2.metric("Создано клипов",len(clips))
    c3.metric("Общий размер исходников",f"{sum(p.get('source_size',0) for p in projects)/1024/1024:.0f} МБ")
    if projects:
        st.subheader("Проекты и результаты")
        for p in projects:
            st.write(f"**{p['name']}** — {len(p.get('clips',[]))} клипов · {p.get('status','')}")
    st.info("Просмотры, удержание аудитории и вовлечённость нельзя достоверно показать без подключения API аккаунтов YouTube, Instagram или TikTok.")

# ---------- Settings ----------
elif page == "Настройки":
    page_title("⚙️ Настройки", "CLIP AI v21 · актуальные модели OpenAI и локальная обработка видео.")
    st.markdown("### Обработка")
    st.write("Устройство распознавания: CPU · faster-whisper small · int8")
    st.write("Лимит загрузки: до 500 МБ (настройка Streamlit)")
    st.write(f"Папка проектов: `{PROJECTS}`")
    st.write(f"Папка результатов: `{OUT}`")
    st.markdown("### Оформление по умолчанию")
    st.caption("Подпись By Senya отображается постоянно.")
    st.selectbox("Стиль субтитров по умолчанию",["Классические белые","Жёлтое выделение","Минималистичные","Кинетические (одно слово)","Неоновые","Контрастные","Подкаст","Компактные","Розовый акцент","Зелёный акцент"],key="global_style")
    st.selectbox("Приближение по умолчанию",["Без приближения","Лёгкое приближение","Сильное приближение"],key="global_zoom")
    st.markdown("### Глубокий AI-анализ")
    st.write("Локальный анализ работает без API. Для смыслового ранжирования подключи OpenAI API.")
    st.text_input(
        "OpenAI API key",
        type="password",
        key="clip_ai_api_key",
        placeholder="sk-…",
        help="Ключ хранится только в текущей сессии приложения и не записывается в файлы проектов."
    )
    model_ids = list(OPENAI_MODEL_LABELS.keys())
    current_model = st.session_state.get("clip_ai_model", DEFAULT_OPENAI_MODEL)
    # Migrate the previous v18 default once. User model selections remain changeable afterward.
    if not st.session_state.get("clip_ai_model_v19_migrated", False):
        if current_model in (None, "", "gpt-4o-mini", "gpt-6.1-terra"):
            current_model = DEFAULT_OPENAI_MODEL
        st.session_state.clip_ai_model_v19_migrated = True
    if current_model not in model_ids:
        current_model = DEFAULT_OPENAI_MODEL
    st.session_state.clip_ai_model = current_model
    st.selectbox(
        "AI-модель",
        options=model_ids,
        format_func=lambda model_id: OPENAI_MODEL_LABELS.get(model_id, model_id),
        key="clip_ai_model",
        help="GPT-6 Astra — самая мощная модель OpenAI; в CLIP AI она использует Responses API, Pro mode и Max reasoning."
    )
    if st.session_state.get("clip_ai_model") == "gpt-6-astra":
        st.warning("Включён максимальный режим GPT-6 Astra: Pro + Max. Он даёт модели больше вычислительного времени, но обычно работает дольше и расходует больше API-токенов. API оплачивается отдельно от подписки ChatGPT.")
    if st.button("Проверить ключ и доступность модели", key="check_openai_model_access"):
        key_for_test = st.session_state.get("clip_ai_api_key", "").strip()
        model_for_test = st.session_state.get("clip_ai_model", DEFAULT_OPENAI_MODEL)
        if not key_for_test:
            st.warning("Сначала вставь OpenAI API key в поле выше.")
        else:
            with st.spinner("Проверяем доступ к выбранной модели…"):
                ok, detail = check_openai_model_access(key_for_test, model_for_test)
            if ok:
                st.success(f"Ключ принят. API видит модель: {detail}. Это проверка доступа к модели; реальный анализ также требует активного API-баланса и доступных лимитов.")
            else:
                st.error(f"Проверка не пройдена: {detail}")
    st.caption("При включённом API в облако отправляются только текстовые фрагменты расшифровки и таймкоды — исходное видео не отправляется. API оплачивается отдельно от подписки ChatGPT. Ключ хранится только в текущей сессии приложения.")
    st.markdown("### Резервное копирование")
    if st.button("Скачать резервную копию данных"):
        backup = {"projects":load_projects(),"calendar":read_json(CALENDAR_FILE,[]),"ads":read_json(ADS_FILE,[])}
        st.download_button("Скачать JSON",json.dumps(backup,ensure_ascii=False,indent=2),file_name="clip_ai_backup.json",mime="application/json")

st.markdown('<div class="by-senya">By <span>Senya</span></div>', unsafe_allow_html=True)
