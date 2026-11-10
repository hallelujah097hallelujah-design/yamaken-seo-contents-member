#!/usr/bin/env python3
"""完成記事（Gutenberg HTML）の本文文字数を機械計測する。

使い方:
  python3 count_draft.py 記事ファイル.md --target-min 6400 --target-max 9600

入力ファイルはGutenbergブロックHTMLをそのまま保存した .md / .html を想定する。

計測ルール（固定）:
  1. CTAを除外する
     - <!-- ▼CTA ... --> から <!-- ▲CTA --> までの範囲
     - class に cta-box を含む要素（入れ子を考慮）
  2. 埋め込み（wp-block-embed の figure）、<script>、<style> を除外する
  3. HTMLコメント（Gutenbergブロックコメント、公開前作業コメント等）を除外する
  4. タグを除去し、HTMLエンティティを文字に戻す
  5. 空白文字（半角・全角スペース、改行、タブ）を除外して数える

  見出し、本文、表、リスト、吹き出し、「この記事を読んでわかること」、まとめは計測対象に含む。

返却値（JSON）:
  character_count, target_min, target_max, achievement_rate(%), status
  status: under_target / within_target / over_target
  あわせて参考情報（H2数・吹き出し数・CTA数・ブロックコメントの対応チェック）を返す。
AIはこの値を再計算・補正せず、そのまま記録する。
"""
import argparse
import html
import json
import re
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class Remover(HTMLParser):
    """指定条件に合う要素を入れ子ごと除去したHTMLを再構築する。"""

    def __init__(self, should_remove):
        super().__init__(convert_charrefs=False)
        self.should_remove = should_remove
        self.out = []
        self.depth = 0  # 除去中の入れ子深さ
        self.removed = 0

    def handle_starttag(self, tag, attrs):
        if self.depth:
            if tag not in VOID:
                self.depth += 1
            return
        if self.should_remove(tag, dict(attrs)):
            self.removed += 1
            if tag not in VOID:
                self.depth = 1
            return
        self.out.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if self.depth or self.should_remove(tag, dict(attrs)):
            return
        self.out.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.depth:
            if tag not in VOID:
                self.depth -= 1
            return
        self.out.append(f"</{tag}>")

    def handle_data(self, d):
        if not self.depth:
            self.out.append(d)

    def handle_entityref(self, n):
        if not self.depth:
            self.out.append(f"&{n};")

    def handle_charref(self, n):
        if not self.depth:
            self.out.append(f"&#{n};")

    def handle_comment(self, d):
        if not self.depth:
            self.out.append(f"<!--{d}-->")


def remove_elements(src, pred):
    r = Remover(pred)
    r.feed(src)
    r.close()
    return "".join(r.out), r.removed


def has_class(attrs, name):
    return name in (attrs.get("class") or "").split()


def block_balance(src):
    """Gutenbergブロックコメントの開始・終了の対応を確認する。"""
    stack, errors = [], []
    for m in re.finditer(r"<!--\s*(/?)wp:([a-z0-9\-/]+)(.*?)(/?)\s*-->", src, re.S):
        closing, name, _, selfclose = m.group(1), m.group(2), m.group(3), m.group(4)
        if selfclose:
            continue
        if not closing:
            stack.append(name)
        else:
            if stack and stack[-1] == name:
                stack.pop()
            else:
                errors.append(f"対応しない終了コメント: /wp:{name}（直前の開始: {stack[-1] if stack else 'なし'}）")
                if name in stack:
                    while stack and stack.pop() != name:
                        pass
    errors += [f"閉じられていない開始コメント: wp:{n}" for n in stack]
    return errors


def measure(src, tmin, tmax):
    """本文文字数を計測して結果のdictを返す。"""
    h2_count = len(re.findall(r"<h2[\s>]", src))
    balloon_count = len(re.findall(r"<!--\s*wp:loos/balloon[\s>]", src))
    balance_errors = block_balance(src)

    # 1. CTA範囲コメントで囲まれた部分を除外
    text, n_cta_range = re.subn(r"<!--\s*▼CTA.*?<!--\s*▲CTA[^>]*-->", "", src, flags=re.S)
    # cta-box要素を除外
    text, n_cta_box = remove_elements(text, lambda t, at: has_class(at, "cta-box"))
    cta_count = n_cta_range + n_cta_box
    # 2. 埋め込み・script・style を除外
    text, _ = remove_elements(
        text,
        lambda t, at: t in ("script", "style") or (t == "figure" and has_class(at, "wp-block-embed")),
    )
    # 3. コメント除去
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # 4. タグ除去・エンティティ復元
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    # 5. 空白除去
    text = re.sub(r"\s+", "", text)

    count = len(text)
    if count < tmin:
        status = "under_target"
    elif count > tmax:
        status = "over_target"
    else:
        status = "within_target"
    return {
        "character_count": count,
        "target_min": tmin,
        "target_max": tmax,
        "achievement_rate": round(count / tmin * 100, 1) if tmin else None,
        "status": status,
        "shortfall": max(tmin - count, 0),
        "reference": {
            "h2_count": h2_count,
            "balloon_count": balloon_count,
            "balloon_guideline": count // 1000,
            "cta_count_excluded": cta_count,
            "gutenberg_block_errors": balance_errors,
        },
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--target-min", type=int, required=True)
    p.add_argument("--target-max", type=int, required=True)
    a = p.parse_args()
    with open(a.file, encoding="utf-8") as f:
        src = f.read()
    print(json.dumps(measure(src, a.target_min, a.target_max), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
