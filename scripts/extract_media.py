# Extract data-URI media from WeChat-style HTML articles
# and write a lighter copy under articles/<slug>/.

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "作品"
OUT_DIR = ROOT / "articles"

ARTICLES = [
    {
        "src": "机器人运动会门道_v2.1.html",
        "slug": "jiqiren-yundonghui",
        "title": "田径运动Alpha Go时刻，百米跑比人类记录快出1秒！",
        "date": "2026-08-26",
        "excerpt": "天工Ultra以8.64秒跑完百米，比博尔特的人类纪录快近1秒。第二届人形机器人运动会，热闹背后是行业变革。",
    },
    {
        "src": "只给盾不给矛 v3.html",
        "slug": "zhi-gei-dun",
        "title": "只给盾，不给矛？Anthropic的网安新模式",
        "date": "2026-08-21",
        "excerpt": "最强网安模型可以给企业用了，但开放的不是模型，而是一份扫描报告。矛收在自己手里，只替你撑起盾。",
    },
    {
        "src": "Jalapeño_v8.html",
        "slug": "jalapeno",
        "title": "OpenAI下场造芯片，巨头们为何纷纷逃离英伟达",
        "date": "2026-08-04",
        "excerpt": "英伟达算力一骑绝尘，OpenAI、谷歌、亚马逊却争相下场造芯片。答案是一道简单的算术题。",
    },
    {
        "src": "AI月报_2026年07月_v5.html",
        "slug": "ai-yuebao-2026-07",
        "title": "每月AI洞见：Transformer还在狂飙",
        "date": "2026-07-31",
        "excerpt": "AI新闻千千万，过段时间再看大都不值得关注。本月4条最重要的新闻，对应5个洞见。",
    },
    {
        "src": "GPT live 语音v1.7.html",
        "slug": "gpt-live",
        "title": "GPT live语音，真正改变的，是交互思维方式",
        "date": "2026-08-01",
        "excerpt": "不是你说完、它再说的录音式语音，而是能边听边说、随时打断的持续对话。实测之后，这是人机交互效率的一次明显提升。",
    },
    {
        "src": "平价战神v4.html",
        "slug": "pingjia-zhanshen",
        "title": "谁是平价战神，千问、智谱、Grok横评",
        "date": "2026-07-27",
        "excerpt": "顶尖模型很强，但贵，还有网络、付费和封号成本。这期横评平价高分模型：千问、智谱、Grok。",
    },
    {
        "src": "starmind v7.html",
        "slug": "starmind",
        "title": "马斯克的疯狂赌注：把100GW AI算力送上太空",
        "date": "2026-07-06",
        "excerpt": "SpaceX 的 AI 卫星项目命名为 Starmind，目标是把巨量算力送上轨道。地面算力好建也好维护，为什么要送上天？",
    },
]

NAV_HTML = """
<a class="site-back" href="../../index.html">← 返回首页</a>
<style>
.site-back{
  position:fixed;top:14px;left:14px;z-index:9999;
  display:inline-flex;align-items:center;gap:8px;
  padding:13px 22px;border-radius:999px;
  background:#9a3412;
  color:#fff;text-decoration:none;
  font:16px/1.1 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
  font-weight:700;
  letter-spacing:0.06em;
  box-shadow:0 6px 18px rgba(154,52,18,.45);
}
.site-back:hover{background:#1c1917;color:#fff;}
@media (max-width:720px){
  .site-back{top:10px;left:10px;padding:12px 18px;font-size:15px;}
}
body{padding-top:72px !important;}
.site-cover{margin:0 0 18px;}
.site-cover img{width:100%;height:auto;display:block;}
</style>
"""

DATA_URI = re.compile(
    r'((?:src|poster)\s*=\s*")data:(image|video)/([a-zA-Z0-9.+-]+);base64,([^"]+)(")',
    re.IGNORECASE,
)

REL_SRC = re.compile(
    r'(src\s*=\s*")((?!data:|https?:|//|media/)[^"]+\.(?:mp4|webm|mov|png|jpe?g|gif|webp))(")',
    re.IGNORECASE,
)


def ext_for(kind: str, subtype: str) -> str:
    subtype = subtype.lower().split("+")[0]
    if kind == "image":
        return {"jpeg": "jpg", "jpg": "jpg", "png": "png", "gif": "gif", "webp": "webp"}.get(subtype, "bin")
    if kind == "video":
        return {"mp4": "mp4", "webm": "webm", "quicktime": "mov"}.get(subtype, "bin")
    return "bin"


def save_image(raw: bytes, dest_no_ext: Path) -> Path:
    from io import BytesIO

    im = Image.open(BytesIO(raw))
    im = im.convert("RGB") if im.mode in {"RGBA", "P", "LA"} else im
    w, h = im.size
    # Keep readable screenshots, cap the long edge for web.
    max_edge = 1600
    if max(w, h) > max_edge:
        ratio = max_edge / max(w, h)
        im = im.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
    out = dest_no_ext.with_suffix(".jpg")
    im.save(out, format="JPEG", quality=82, optimize=True, progressive=True)
    return out


def inject_cover(html: str, article: dict, out_dir: Path) -> str:
    """Insert cover.jpg above the first h1 if the article has no cover yet."""
    cover = out_dir / "cover.jpg"
    if not cover.exists():
        return html
    if re.search(r'<figure[^>]*class="[^"]*\bcover\b', html, re.IGNORECASE):
        return html
    if re.search(r'class="site-cover"', html):
        return html
    alt = (
        article["title"]
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
    )
    block = f'<figure class="site-cover"><img src="cover.jpg" alt="{alt}"></figure>\n'
    if re.search(r"<h1\b", html, re.IGNORECASE):
        return re.sub(r"(<h1\b)", block + r"\1", html, count=1, flags=re.IGNORECASE)
    return html


def process(article: dict) -> dict:
    src_path = SRC_DIR / article["src"]
    out_dir = OUT_DIR / article["slug"]
    media_dir = out_dir / "media"
    out_dir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)

    html = src_path.read_text(encoding="utf-8")
    counters = {"image": 0, "video": 0}
    cover = None

    def repl(match: re.Match) -> str:
        nonlocal cover
        prefix, kind, subtype, b64, suffix = match.groups()
        kind = kind.lower()
        counters[kind] += 1
        n = counters[kind]
        import base64

        raw = base64.b64decode(b64)
        stem = media_dir / f"{kind}-{n:02d}"
        if kind == "image":
            path = save_image(raw, stem)
            if cover is None:
                cover = path.relative_to(ROOT).as_posix()
        else:
            path = stem.with_suffix("." + ext_for(kind, subtype))
            path.write_bytes(raw)
        rel = path.relative_to(out_dir).as_posix()
        return f'{prefix}{rel}{suffix}'

    html = DATA_URI.sub(repl, html)

    def copy_rel(match: re.Match) -> str:
        prefix, rel, suffix = match.groups()
        rel_norm = rel.replace("\\", "/")
        candidate = (src_path.parent / rel_norm)
        if not candidate.exists():
            print(f"  missing relative media: {rel}")
            return match.group(0)
        kind = "video" if candidate.suffix.lower() in {".mp4", ".webm", ".mov"} else "image"
        counters[kind] += 1
        n = counters[kind]
        dest = media_dir / f"{kind}-{n:02d}{candidate.suffix.lower()}"
        dest.write_bytes(candidate.read_bytes())
        return f"{prefix}{dest.relative_to(out_dir).as_posix()}{suffix}"

    html = REL_SRC.sub(copy_rel, html)

    if re.search(r"<body[^>]*>", html, re.IGNORECASE):
        html = re.sub(r"(<body[^>]*>)", r"\1" + NAV_HTML, html, count=1, flags=re.IGNORECASE)
    else:
        html = NAV_HTML + html

    html = inject_cover(html, article, out_dir)

    (out_dir / "index.html").write_text(html, encoding="utf-8")

    sizes = {
        "original_mb": round(src_path.stat().st_size / 1024 / 1024, 2),
        "html_mb": round((out_dir / "index.html").stat().st_size / 1024 / 1024, 2),
        "media_mb": round(sum(p.stat().st_size for p in media_dir.iterdir()) / 1024 / 1024, 2),
        "images": counters["image"],
        "videos": counters["video"],
        "cover": cover,
    }
    print(f"{article['slug']}: {sizes}")
    article_out = {**article, **sizes, "href": f"articles/{article['slug']}/"}
    return article_out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slugs = sys.argv[1:]
    selected = [a for a in ARTICLES if a["slug"] in slugs] if slugs else ARTICLES
    if slugs and not selected:
        print(f"unknown slug(s): {slugs}", file=sys.stderr)
        return 1
    results = [process(a) for a in selected]
    if slugs:
        by_slug = {}
        man = OUT_DIR / "manifest.json"
        if man.exists():
            for item in json.loads(man.read_text(encoding="utf-8")):
                by_slug[item["slug"]] = item
        for item in results:
            by_slug[item["slug"]] = item
        manifest = [by_slug[a["slug"]] for a in ARTICLES if a["slug"] in by_slug]
    else:
        manifest = results
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
