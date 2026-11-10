#!/usr/bin/env python3
"""競合本文文字数から記事の目標文字数を算出する。

使い方:
  python3 calc_targets.py 8200 6500 9100 7300 5800
  python3 calc_targets.py --json '[{"url":"https://...","count":8200}, {"url":"https://...","count":null}]'

  count が null / 0 / 空のURLは計測不能（failed）として扱い、平均から除外する。

算出式（固定）:
  average_count = 成功URLの文字数の平均（四捨五入）
  target_110    = average_count × 1.1（四捨五入）
  target_min    = average_count × 0.8（平均の-20%、四捨五入）
  target_max    = average_count × 1.2（平均の+20%、四捨五入）

返却値はJSONで出力する。AIはこの値を再計算・補正せず、そのまま記録する。
"""
import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP


def half_up(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def reliability(success):
    if success >= 5:
        return "正式平均"
    if success >= 3:
        return "参考値（3〜4本）"
    if success >= 1:
        return "信頼性低（1〜2本）：候補が10URL未満なら別のSEO競合を追加して再計算する。10URLに達していれば、信頼性低として記録しこの値で進む"
    return "計測不能（0本）：目標文字数を確定できない"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("counts", nargs="*", help="各競合の本文文字数")
    p.add_argument("--json", help='[{"url":..., "count":...}, ...] 形式')
    a = p.parse_args()

    items = []
    if a.json:
        for it in json.loads(a.json):
            items.append({"url": it.get("url"), "count": it.get("count")})
    for c in a.counts:
        items.append({"url": None, "count": c})

    results = []
    ok = []
    for it in items:
        c = it["count"]
        try:
            c = int(str(c).replace(",", "")) if c not in (None, "") else 0
        except ValueError:
            c = 0
        status = "success" if c > 0 else "failed"
        if status == "success":
            ok.append(c)
        results.append({"url": it["url"], "count": c if c > 0 else None, "status": status})

    out = {
        "results": results,
        "url_count": len(results),
        "success_count": len(ok),
        "failed_count": len(results) - len(ok),
        "reliability": reliability(len(ok)),
    }
    if ok:
        avg = sum(ok) / len(ok)
        out.update({
            "average_count": half_up(avg),
            "target_110": half_up(avg * 1.1),
            "target_min": half_up(avg * 0.8),
            "target_max": half_up(avg * 1.2),
        })
    else:
        out.update({"average_count": None, "target_110": None, "target_min": None, "target_max": None})

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
