#!/usr/bin/env python3
"""完成記事（Gutenberg HTML）を一括で機械チェックする。工程6ではこのコマンドを使う。

使い方:
  python3 check_article.py 記事ファイル.md --target-min 5904 --target-max 8856
  python3 check_article.py 記事ファイル.md --target-min 5904 --target-max 8856 --no-case   # 案件なしの記事

実行内容:
  1. 文字数計測（count_draft.py と同じ計測ルール）
  2. 構造チェック（冒頭の並び、CTAの位置・数・属性、この記事を読んでわかること5項目、
     まとめ8〜15項目、H3が1つだけのH2、情報最終確認日、吹き出し数、表、禁止クラス、空タグ等）
  3. 具体性チェック（check_specificity.py と同じ：丸投げ・省略・ぼかし表現）

出力:
  summary.errors   … 修正必須（0件にする）
  summary.warnings … 見直して、残す場合は理由を納品メモに記録
  AIは返却値を再計算・補正しない。修正したら再実行する。
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_draft import measure  # noqa: E402
from check_specificity import scan  # noqa: E402

MARKER = "この記事を読んでわかること"


def strip_tags(s):
    return re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", re.sub(r"<!--.*?-->", "", s, flags=re.S)))


def first_list_items(segment):
    m = re.search(r"<(ul|ol)\b.*?</\1>", segment, re.S)
    return len(re.findall(r"<li[\s>]", m.group(0))) if m else 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--target-min", type=int, required=True)
    p.add_argument("--target-max", type=int, required=True)
    p.add_argument("--no-case", action="store_true", help="案件なしの記事（CTAを置かない）")
    a = p.parse_args()
    src = Path(a.file).read_text(encoding="utf-8")

    errors, warnings = [], []

    def err(name, detail):
        errors.append({"check": name, "detail": detail})

    def warn(name, detail):
        warnings.append({"check": name, "detail": detail})

    # ---------- 1. 文字数 ----------
    m = measure(src, a.target_min, a.target_max)
    if m["status"] == "under_target":
        err("文字数", f"{m['character_count']}文字。target_min {a.target_min} まで {m['shortfall']}文字不足")
    for e in m["reference"]["gutenberg_block_errors"]:
        err("Gutenbergブロック", e)

    # ---------- 2. 構造 ----------
    h2s = [(x.start(), strip_tags(x.group(1))) for x in re.finditer(r"<h2[^>]*>(.*?)</h2>", src, re.S)]
    first_h2 = h2s[0][0] if h2s else len(src)
    if not h2s:
        err("H2", "H2がない")

    # この記事を読んでわかること（<strong>のマーカーで判定）
    for hx in re.finditer(r"<h[1-6][^>]*>(.*?)</h[1-6]>", src, re.S):
        if MARKER in strip_tags(hx.group(1)):
            err("この記事を読んでわかること", "見出しタグになっている（通常段落のstrongにする）")
    mk_m = re.search(r"<strong>\s*" + MARKER + r"\s*</strong>", src)
    mk = mk_m.start() if mk_m else -1
    if mk == -1:
        err("この記事を読んでわかること", "<strong>この記事を読んでわかること</strong> の段落が見つからない")
    else:
        g_open = src.rfind("<!-- wp:group", 0, mk)
        if g_open == -1 or "<!-- /wp:group -->" in src[g_open:mk]:
            err("この記事を読んでわかること", "囲みボックス（wp:group）の中にない")
        g_close = src.find("<!-- /wp:group -->", mk)
        box = src[mk:g_close if g_close != -1 else first_h2]
        n = first_list_items(box)
        if n != 5:
            err("この記事を読んでわかること", f"項目数が{n}（5項目にする）")
        if "is-style-num_circle" in box or "has-background" in re.sub(r'<div class="wp-block-group[^"]*"', "", box):
            err("この記事を読んでわかること", "ボックス内のリストに通常ulの装飾が付いている（装飾なしulにする）")
        if mk > first_h2:
            err("冒頭の並び", "「この記事を読んでわかること」が最初のH2より後にある")

    # 情報最終確認日（文言「時点で確認しています」は機械チェック対象のため変えない）
    dates = [x.start() for x in re.finditer(r"時点で確認しています", src)]
    if len(dates) != 1:
        err("情報最終確認日", f"{len(dates)}件（導入文末尾に「※記事内の変動しやすい情報は、YYYY年M月D日時点で確認しています。」を1件だけ置く）")
    elif mk != -1:
        d0 = dates[0]
        p_end = src.find("<!-- /wp:paragraph -->", d0)
        after = src[p_end + len("<!-- /wp:paragraph -->"):] if p_end != -1 else ""
        if d0 > mk or not after.lstrip().startswith("<!-- wp:group"):
            err("冒頭の並び", "情報最終確認日の段落の直後が「この記事を読んでわかること」のボックスになっていない")
        if not re.search(r"<p[\s>]", src[:src.rfind("<!-- wp:paragraph", 0, d0)]):
            err("冒頭の並び", "情報最終確認日の前に導入文の段落がない")

    # 見出しブロックの形式
    for hx in re.finditer(r"<h([23])\b[^>]*>", src):
        before = src[max(0, hx.start() - 200):hx.start()]
        bc = re.findall(r"<!--\s*wp:heading([^>]*)-->", before)
        if not bc or not before.rstrip().endswith("-->"):
            err("見出し", f"H{hx.group(1)}が wp:heading ブロックで囲まれていない")
        elif hx.group(1) == "3" and '"level":3' not in bc[-1]:
            err("見出し", 'H3のブロックコメントに {"level":3} がない')
        if 'class="wp-block-heading"' not in hx.group(0):
            err("見出し", f'H{hx.group(1)}に class="wp-block-heading" がない')

    # CTA
    cta_starts = [(x.start(), x.end(), x.group(1)) for x in re.finditer(r"<!--\s*▼CTA(.*?)-->", src, re.S)]
    cta_ends = [x.end() for x in re.finditer(r"<!--\s*▲CTA[^>]*-->", src)]
    if len(cta_starts) != len(cta_ends):
        err("CTA", f"開始コメント{len(cta_starts)}件と終了コメント{len(cta_ends)}件が一致しない")
    ranges = []
    for s0, _, _ in cta_starts:
        e0 = next((e for e in cta_ends if e > s0), len(src))
        ranges.append((s0, e0))
    main_ctas = [c for c in cta_starts if "具体例" not in c[2]]
    ex_ctas = [c for c in cta_starts if "具体例" in c[2]]
    boxes = len(re.findall(r'class="[^"]*\bcta-box\b', src))
    if boxes != len(cta_starts):
        err("CTA", f"cta-boxが{boxes}件、CTAコメントが{len(cta_starts)}件（cta-boxは必ず▼CTA〜▲CTAで囲む）")
    # CTA範囲外のsponsoredリンク（CTAの置き忘れ・囲い忘れ）
    for a_m in re.finditer(r"<a\b[^>]*>", src):
        if re.search(r'rel="[^"]*sponsored', a_m.group(0)) and not any(r0 <= a_m.start() < r1 for r0, r1 in ranges):
            err("CTA", f"▼CTA〜▲CTAの外に広告リンク（sponsored）がある: {a_m.group(0)[:80]}")
    if a.no_case:
        if cta_starts:
            err("CTA", "案件なしの記事にCTAがある")
    else:
        if len(main_ctas) != 1:
            err("メインCTA", f"{len(main_ctas)}件（最初のH2の直上に1件）")
        else:
            s0 = main_ctas[0][0]
            end = next((e for e in cta_ends if e > s0), None)
            between = src[end:first_h2] if end else ""
            between = re.sub(r"<!--\s*wp:heading[^>]*-->", "", between)
            if s0 > first_h2 or (end and between.strip()):
                err("メインCTA", "最初のH2の直上にない（CTAとH2の間に他の要素がある、またはH2より後）")
            if mk != -1 and s0 < mk:
                err("冒頭の並び", "メインCTAが「この記事を読んでわかること」より前にある")
        heads = [x.start() for x in re.finditer(r"<h[23][\s>]", src)]
        for s0, _, _ in ex_ctas:
            prev_head = max([h for h in heads if h < s0], default=0)
            seg = src[prev_head:s0]
            t_end = seg.rfind("</table>")
            if t_end == -1:
                err("具体例CTA", "同じ見出し内に3パターンの具体例の表がない")
            elif not re.search(r'<a\b[^>]*href="https?://', seg[t_end:]):
                err("具体例CTA", "表とCTAの間に、自分のケースの調べ方と該当ページへのリンクがない")
            if s0 < first_h2:
                err("具体例CTA", "最初のH2より前にある")
    # CTAリンク属性
    for r0, r1 in ranges:
        for tag in re.findall(r"<a\b[^>]*>", src[r0:r1]):
            rel = re.search(r'rel="([^"]*)"', tag)
            relv = rel.group(1).split() if rel else []
            if 'target="_blank"' not in tag or "noopener" not in relv or "sponsored" not in relv:
                err("CTAリンク", f'target="_blank" と rel="noopener sponsored" が必要: {tag[:80]}')
            if 'href="AFF_LINK"' in tag:
                warn("CTAリンク", "AFF_LINKが残っている（公開前作業に差し替えを明記する）")

    # まとめ
    if h2s:
        last_pos, last_txt = h2s[-1]
        if "まとめ" not in last_txt:
            err("まとめ", f"最後のH2がまとめになっていない（{last_txt[:30]}）")
        else:
            n = first_list_items(src[last_pos:])
            if not 8 <= n <= 15:
                err("まとめ", f"まとめのリストが{n}項目（8〜15項目）")

    # H3が1つだけのH2
    bounds = [p0 for p0, _ in h2s] + [len(src)]
    for i, (p0, txt) in enumerate(h2s):
        n3 = len(re.findall(r"<h3[\s>]", src[p0:bounds[i + 1]]))
        if n3 == 1:
            warn("H3", f"H2「{txt[:30]}」のH3が1つだけ（本文へ統合できないか検討）")

    # 吹き出し
    bc, bg = m["reference"]["balloon_count"], m["reference"]["balloon_guideline"]
    if bg and not (bg * 0.7 <= bc <= bg * 1.3 + 1):
        warn("吹き出し", f"{bc}個（目安は本文1,000文字につき1個＝{bg}個）")

    # 表：tbody内1列目
    for tb in re.findall(r"<tbody>(.*?)</tbody>", src, re.S):
        for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", tb, re.S):
            if not tr.strip().startswith('<th scope="row"'):
                err("表", 'tbody内の1列目が<th scope="row">になっていない')
                break

    # HTMLの禁止パターン
    for pat, name in [
        (r"<p>\s*</p>", "空の<p>"),
        (r"<(div|span)\b[^>]*>\s*</\1>", "空の<div>/<span>"),
        (r'href=""', '空のhref'),
        (r'src=""', '空のsrc'),
        (r"swl-pale-02|has-swl-main-thin-background-color|\"backgroundColor\":\"swl-main-thin\"", "旧形式の背景クラス"),
    ]:
        if re.search(pat, src):
            err("HTML", f"{name}が残っている")
    if re.search(r"【PR】|アフィリエイト広告を利用|本記事はプロモーション", strip_tags(src)):
        err("PR表記", "本文にPR表記がある（WordPress共通設定を使うため本文には入れない）")

    # ---------- 3. 具体性 ----------
    sp = scan(src)
    if sp["counts"]["marunage_without_link"]:
        err("具体性：丸投げ", f"{sp['counts']['marunage_without_link']}件（同じ段落に該当ページへのリンクがない）。具体情報に書き換えるか、09 #2の例外の書き方にする")
    n_link = sp["counts"]["marunage"] - sp["counts"]["marunage_without_link"]
    if n_link:
        warn("具体性：公式サイト案内", f"{n_link}件（リンクあり）。09 #2の例外に当たり、記事内の情報を先に書き、該当ページの場所を示しているか確認する")
    if sp["counts"]["shoryaku"] or sp["counts"]["bokashi"]:
        warn("具体性：省略・ぼかし", f"省略{sp['counts']['shoryaku']}件・ぼかし{sp['counts']['bokashi']}件。具体名へ書き換える。残す場合は理由を納品メモへ")

    out = {
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "character_count": m["character_count"],
            "target_min": a.target_min,
            "status": m["status"],
            "main_cta": len(main_ctas),
            "example_cta": len(ex_ctas),
        },
        "errors": errors,
        "warnings": warnings,
        "length": m,
        "specificity_hits": sp["hits"],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
