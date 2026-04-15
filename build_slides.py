# -*- coding: utf-8 -*-
"""
slides.md（YAML マルチドキュメント）から #slide-area を生成し slide.html に埋め込む。
依存: リポジトリ直下で pip install -r requirements.txt

使い方:
  python build_slides.py SLIDE/<デック名>

正本: <デック>/slides.md
型: cover | toc | section | bullets | cards
  bullets は任意で image: 相対パス（slide.html と同じフォルダ）, image_alt: 省略可
  cards は任意で footer_section: フッター用の表示を上書き（例: 3. まとめ）

目次は section スライドの並びでジャンプ先が決まる（手で target を書かない）。
data-section は section の section_num + title から自動命名。
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as e:
    raise SystemExit(
        "PyYAML が必要です。リポジトリ直下で次を実行してください: pip install -r requirements.txt"
    ) from e

# main() でデックパス確定後に設定される
ROOT: Path | None = None
LOGO: str | None = None
SLIDES_MD: Path | None = None


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def esc_attr(s: str) -> str:
    return html.escape(s, quote=True)


def load_documents() -> list[dict[str, Any]]:
    assert SLIDES_MD is not None
    raw = SLIDES_MD.read_text(encoding="utf-8")
    docs: list[dict[str, Any]] = []
    for doc in yaml.safe_load_all(raw):
        if doc is None:
            continue
        if not isinstance(doc, dict):
            raise ValueError(f"各ドキュメントはマッピングである必要があります: {doc!r}")
        docs.append(doc)
    if not docs:
        raise SystemExit(f"{SLIDES_MD} にスライドがありません")
    return docs


def join_title_lines(lines: list[str] | Any) -> str:
    if lines is None:
        return ""
    if isinstance(lines, str):
        return esc(lines)
    if isinstance(lines, list):
        return "<br>".join(esc(str(x)) for x in lines)
    return esc(str(lines))


def section_data_section(d: dict[str, Any]) -> str:
    """フッター等に出す data-section 用の1行（例: 1. はじめに）"""
    num = int(d["section_num"])
    title = str(d["title"]).strip()
    return f"{num}. {title}"


def normalize_toc_labels(raw_items: Any) -> list[str]:
    """items: [ "ラベル", ... ] または旧形式 [{label, target}, ...] のラベルだけ取り出し"""
    if not raw_items:
        return []
    out: list[str] = []
    for i, it in enumerate(raw_items, start=1):
        if isinstance(it, str):
            out.append(it)
        elif isinstance(it, dict) and "label" in it:
            out.append(str(it["label"]))
        else:
            raise ValueError(f"toc items[{i}] は文字列か {{label: ...}} 形式にしてください")
    return out


def render_cover(d: dict[str, Any], active: bool) -> str:
    assert LOGO is not None
    cls = "slide slide-title" + (" active" if active else "")
    main_title = join_title_lines(d.get("main_title"))
    sub_title = esc(str(d.get("sub_title", "")))
    meta = esc(str(d.get("meta", "")))
    return f"""    <div class="{cls}" data-section="表紙">
      <div class="slide-bar"></div>
      <div class="slide-body">
        <div class="main-title">{main_title}</div>
        <div class="sub-title">{sub_title}</div>
        <div class="meta">{meta}</div>
      </div>
      {LOGO}
    </div>"""


def render_toc(d: dict[str, Any], section_slide_indices: list[int]) -> str:
    assert LOGO is not None
    heading = esc(str(d.get("heading", "目次")))
    labels = normalize_toc_labels(d.get("items"))
    if len(labels) != len(section_slide_indices):
        raise ValueError(
            f"目次の項目数（{len(labels)}）と section の枚数（{len(section_slide_indices)}）が一致しません"
        )
    lines: list[str] = [
        '    <div class="slide slide-toc" data-section="目次">',
        '      <div class="slide-bar"></div>',
        '      <div class="slide-body">',
        f'        <div class="toc-heading">{heading}</div>',
        '        <ul class="toc-list" id="toc-list">',
    ]
    for i, (label, slide_idx) in enumerate(zip(labels, section_slide_indices), start=1):
        lab = esc(label)
        idx = int(slide_idx)
        lines.append(
            f'          <li data-slide-index="{idx}">'
            f'<span class="toc-num">{i}</span><span>{lab}</span></li>'
        )
    lines.extend(
        [
            "        </ul>",
            "      </div>",
            f"      {LOGO}",
            "    </div>",
        ]
    )
    return "\n".join(lines)


def render_bullet_item(x: Any, index: int) -> str:
    """箇条書き1行。文字列はエスケープ、{ html: ... } はスライド正本なのでそのまま埋め込み。"""
    if isinstance(x, str):
        return esc(x)
    if isinstance(x, dict) and "html" in x:
        return str(x["html"])
    raise ValueError(
        f"bullets items[{index}] は文字列か {{html: ...}}（リンク用HTML）にしてください: {x!r}"
    )


def render_section(d: dict[str, Any]) -> str:
    assert LOGO is not None
    display = section_data_section(d)
    num = int(d["section_num"])
    title = esc(str(d["title"]))
    sec_attr = esc_attr(display)
    return f"""    <div class="slide slide-section" data-section="{sec_attr}">
      <div class="slide-bar"></div>
      <div class="slide-body">
        <div class="section-num">SECTION {num}</div>
        <div class="section-title">{title}</div>
      </div>
      {LOGO}
    </div>"""


def render_bullets(data_section: str, d: dict[str, Any]) -> str:
    assert LOGO is not None
    sk = esc_attr(data_section)
    heading = esc(str(d["heading"]))
    items = d.get("items") or []
    lis = "\n".join(
        f"          <li>{render_bullet_item(x, i)}</li>"
        for i, x in enumerate(items, start=1)
    )
    img_rel = d.get("image")
    if img_rel:
        img_src = esc_attr(str(img_rel).strip())
        alt = esc(str(d.get("image_alt", "")))
        body = f"""      <div class="slide-body">
        <div class="slide-heading">{heading}</div>
        <div class="slide-bullets-with-media">
        <ul class="slide-list">
{lis}
        </ul>
          <div class="slide-inline-figure">
            <img src="{img_src}" alt="{alt}" />
          </div>
        </div>
      </div>"""
    else:
        body = f"""      <div class="slide-body">
        <div class="slide-heading">{heading}</div>
        <ul class="slide-list">
{lis}
        </ul>
      </div>"""
    return f"""    <div class="slide slide-content" data-section="{sk}">
      <div class="slide-bar"></div>
{body}
      {LOGO}
    </div>"""


def render_cards(data_section: str, d: dict[str, Any]) -> str:
    assert LOGO is not None
    sk = esc_attr(data_section)
    heading = esc(str(d["heading"]))
    cards = d.get("cards") or []
    parts: list[str] = []
    for i, text in enumerate(cards, start=1):
        num = str(i).zfill(2)
        parts.append(
            f"""          <div class="card">
            <div class="card-num">{num}</div>
            <div class="card-text">{esc(str(text))}</div>
          </div>"""
        )
    cards_html = "\n".join(parts)
    return f"""    <div class="slide slide-summary" data-section="{sk}">
      <div class="slide-bar"></div>
      <div class="slide-body">
        <div class="slide-heading">{heading}</div>
        <div class="summary-cards">
{cards_html}
        </div>
      </div>
      {LOGO}
    </div>"""


def collect_section_slide_indices(docs: list[dict[str, Any]]) -> list[int]:
    return [i for i, d in enumerate(docs) if d.get("type") == "section"]


def render_slides_html(docs: list[dict[str, Any]]) -> tuple[str, str]:
    """戻り値: (slide_area_inner_html, html_title)"""
    section_indices = collect_section_slide_indices(docs)
    chunks: list[str] = []
    html_title = "ichini スライド"
    last_section_display: str | None = None

    for i, doc in enumerate(docs):
        t = doc.get("type")
        if t == "cover":
            html_title = str(doc.get("html_title", html_title))
            chunks.append(render_cover(doc, active=(i == 0)))
        elif t == "toc":
            chunks.append(render_toc(doc, section_indices))
        elif t == "section":
            last_section_display = section_data_section(doc)
            chunks.append(render_section(doc))
        elif t == "bullets":
            if last_section_display is None:
                raise ValueError(
                    f"スライド {i + 1}: bullets より前に type: section が必要です"
                )
            chunks.append(render_bullets(last_section_display, doc))
        elif t == "cards":
            if last_section_display is None:
                raise ValueError(
                    f"スライド {i + 1}: cards より前に type: section が必要です"
                )
            ds_cards = last_section_display
            if doc.get("footer_section") is not None:
                ds_cards = str(doc["footer_section"]).strip()
            chunks.append(render_cards(ds_cards, doc))
        else:
            raise ValueError(f"未知の type: {t!r} (スライド {i + 1})")
    return "\n\n".join(chunks), html_title


def patch_slide_html(inner: str, html_title: str, slide_count: int) -> None:
    assert ROOT is not None
    path = ROOT / "slide.html"
    s = path.read_text(encoding="utf-8")
    start_tag = '<div id="slide-area">'
    end_marker = "  </div><!-- /slide-area -->"
    start = s.find(start_tag)
    if start == -1:
        raise SystemExit("slide.html: start tag not found")
    end = s.find(end_marker)
    if end == -1:
        raise SystemExit("slide.html: end marker not found")
    inner_start = start + len(start_tag)
    new_inner = "\n" + inner.rstrip() + "\n\n  "
    s = s[:inner_start] + new_inner + s[end:]

    s = re.sub(
        r"<title>.*?</title>",
        f"<title>{esc_attr(html_title)}</title>",
        s,
        count=1,
        flags=re.DOTALL,
    )
    s = re.sub(
        r'(<div class="ctrl-page" id="page-num">)1 / \d+(</div>)',
        rf"\g<1>1 / {slide_count}\g<2>",
        s,
        count=1,
    )
    path.write_text(s, encoding="utf-8")


def main() -> None:
    global ROOT, LOGO, SLIDES_MD

    parser = argparse.ArgumentParser(
        description="slides.md から slide.html のスライド領域を生成する。"
    )
    parser.add_argument(
        "deck",
        type=Path,
        help="デックのディレクトリ（slides.md / slide.html / _logo_frag.txt がある場所）",
    )
    args = parser.parse_args()
    ROOT = args.deck.resolve()
    if not ROOT.is_dir():
        raise SystemExit(f"ディレクトリがありません: {ROOT}")

    logo_path = ROOT / "_logo_frag.txt"
    if not logo_path.is_file():
        raise SystemExit(f"_logo_frag.txt がありません: {logo_path}")

    LOGO = logo_path.read_text(encoding="utf-8")
    SLIDES_MD = ROOT / "slides.md"

    docs = load_documents()
    inner, html_title = render_slides_html(docs)
    n = len(docs)
    patch_slide_html(inner, html_title, n)
    print("patched:", ROOT / "slide.html", "slides:", n, "title:", html_title)


if __name__ == "__main__":
    main()
