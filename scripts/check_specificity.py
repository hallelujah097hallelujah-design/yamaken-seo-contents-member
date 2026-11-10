#!/usr/bin/env python3
"""記事本文から「公式サイトへの丸投げ」「具体名の省略」「ぼかし表現」を洗い出す。

使い方:
  python3 check_specificity.py 記事ファイル.md

  CTA（▼CTA〜▲CTA、cta-box）・埋め込み・HTMLコメント・タグを除いた本文を検査する。
  検出箇所をカテゴリ別に、前後の文脈つきでJSON出力する。

カテゴリ:
  marunage : 公式サイト等への丸投げ（完成条件：例外の書き方を満たすもの以外は0件）
  shoryaku : 「など」「等」「ほか」「をはじめ」等による具体名の省略
  bokashi  : 「各種」「多数」「豊富」「さまざまな」等の中身を書かないぼかし表現

検出は機械的なため、正しい用法も含まれうる。AIは1件ずつ見直して判断する。
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_draft import remove_elements, has_class  # noqa: E402

PATTERNS = {
    "marunage": [
        r"(公式|オフィシャル)(サイト|ホームページ|HP|ページ|アプリ|SNS)[^。！？\n]{0,20}?(ご?確認|ご覧|チェック|参照|見て|ご参考)",
        r"詳(しく|細)は[^。！？\n]{0,25}?(公式|サイト|ページ|こちら|リンク先|窓口|問い合わせ)",
        r"(最新|正確|詳細)な?(の)?情報は[^。！？\n]{0,25}?(公式|サイト|ページ|確認)",
        r"(公式|サイト|ページ)[^。！？\n]{0,10}?(に|で)(掲載|記載|案内|紹介)されて(います|いる)",
        r"(問い合わせ|お問い合わせ)(して|ください|をおすすめ)",
    ],
    "shoryaku": [
        r"など",
        r"(?<![平均上同対初高劣差優一二三四五六七八九十何])等(?=[、。・）\)」のをがにはでもと\s])",
        r"(?<!その)(?<!この)ほか(?=[、。にのも])",
        r"をはじめ",
        r"といった",
    ],
    "bokashi": [
        r"各種",
        r"多数",
        r"豊富(な|に|です|さ)",
        r"(さまざま|様々|色々|いろいろ|いろんな)",
        r"幅広い",
        r"数多く",
        r"一部の",
    ],
}


def body_text(src):
    text = re.sub(r"<!--\s*▼CTA.*?<!--\s*▲CTA[^>]*-->", "", src, flags=re.S)
    text, _ = remove_elements(text, lambda t, at: has_class(at, "cta-box"))
    text, _ = remove_elements(
        text,
        lambda t, at: t in ("script", "style") or (t == "figure" and has_class(at, "wp-block-embed")),
    )
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # リンクの位置を残す（丸投げの例外判定用）
    text = re.sub(r"<a\b[^>]*href=\"https?://[^\"]+\"[^>]*>(.*?)</a>", r"\1［リンク］", text, flags=re.S)
    # ブロック要素の区切りを改行にして文脈を読みやすくする
    text = re.sub(r"</(p|li|h[1-6]|th|td|tr|figcaption|cite|blockquote)>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t　]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def scan(src):
    """丸投げ・省略・ぼかし表現を検出してdictを返す。"""
    text = body_text(src)

    hits = []
    seen = set()
    for cat, pats in PATTERNS.items():
        for pat in pats:
            for m in re.finditer(pat, text):
                if cat == "marunage":
                    # 丸投げは1文につき1件として数える
                    sent_start = max(text.rfind("。", 0, m.start()), text.rfind("\n", 0, m.start()))
                    key = (cat, "sent", sent_start)
                else:
                    key = (cat, m.start())
                if key in seen:
                    continue
                seen.add(key)
                line_start = text.rfind("\n", 0, m.start()) + 1
                line_end = text.find("\n", m.end())
                line_end = len(text) if line_end == -1 else line_end
                s = max(line_start, m.start() - 30)
                e = min(line_end, m.end() + 30)
                sent_s = max(text.rfind("。", 0, m.start()), text.rfind("\n", 0, m.start())) + 1
                para_e = text.find("\n", m.end())
                para = text[sent_s:(para_e if para_e != -1 else len(text))]
                has_link = "［リンク］" in para
                hits.append({
                    "category": cat,
                    "has_link_in_paragraph": has_link,
                    "match": m.group(0),
                    "context": text[s:e],
                    "line": text.count("\n", 0, m.start()) + 1,
                })
    hits.sort(key=lambda h: (["marunage", "shoryaku", "bokashi"].index(h["category"]), h["line"]))
    counts = {c: sum(1 for h in hits if h["category"] == c) for c in PATTERNS}
    counts["marunage_without_link"] = sum(1 for h in hits if h["category"] == "marunage" and not h["has_link_in_paragraph"])
    out = {
        "counts": counts,
        "marunage_zero": counts["marunage"] == 0,
        "hits": hits,
        "note": "検出箇所を1つずつ見直し、具体情報へ書き換える。残す場合は理由を納品メモに記録する。marunageは例外の書き方（記事内の情報＋該当ページの場所とURL）を満たすもの以外0件にする。",
    }
    return out


def main():
    if len(sys.argv) != 2:
        print("使い方: python3 check_specificity.py 記事ファイル.md", file=sys.stderr)
        return 2
    src = Path(sys.argv[1]).read_text(encoding="utf-8")
    print(json.dumps(scan(src), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
