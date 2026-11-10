# ブロックパーツ集

CTAの配置とリンクは`07_execution_contract.md` #5、何を書くかは05・09に従う。このファイルはHTMLの書き方だけを定める。形式の多くは`scripts/check_article.py`で機械チェックされる。

このファイルは、完成した記事内容を**WordPress Gutenberg＋SWELLで正常に表示できるブロックHTMLへ実装するための仕様**を定める。

文章内容、検索意図、構成、CTA訴求内容、SEO判断は他のreferenceに従う。

---

# 1. 基本出力形式

記事本文はすべて、

**Gutenbergブロック形式のHTML**

で出力する。

各ブロックの開始・終了コメントを正しく対応させる。

---

# 2. H2

```html
<!-- wp:heading -->
<h2 class="wp-block-heading">見出しテキスト</h2>
<!-- /wp:heading -->
```

---

# 3. H3

```html
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">見出しテキスト</h3>
<!-- /wp:heading -->
```

---

# 4. 通常段落

```html
<!-- wp:paragraph -->
<p>本文テキスト</p>
<!-- /wp:paragraph -->
```

通常本文は、

* 1段落60文字前後
* 原則3文以内

を目安とする。

意味の途中で不自然に分割しない。

# 4-1. 情報最終確認日

情報最終確認日は、導入文の最後に1回だけ配置する。文言「時点で確認しています」は`check_article.py`の判定に使うため変えない。

```html
<!-- wp:paragraph {"fontSize":"small"} -->
<p class="has-small-font-size">※記事内の変動しやすい情報は、YYYY年M月D日時点で確認しています。</p>
<!-- /wp:paragraph -->
```

---

# 5. 通常の箇条書き

通常ulは以下の形式へ統一する。

```html
<!-- wp:list {"className":"is-style-num_circle -list-under-dashed","style":{"color":{"background":"var(--color_main_thin)"}},"fontSize":"small"} -->
<ul class="wp-block-list is-style-num_circle -list-under-dashed has-background has-small-font-size" style="background-color:var(--color_main_thin)"><!-- wp:list-item -->
<li>項目</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>項目</li>
<!-- /wp:list-item --></ul>
<!-- /wp:list -->
```

対応関係：

* `className` → `is-style-num_circle -list-under-dashed`
* `style.color.background` → `var(--color_main_thin)`
* `fontSize` → `small`

HTML側には、

* `style="background-color:var(--color_main_thin)"`
* `has-background`
* `has-small-font-size`

を含める。

以下の形式は使用しない。

* `backgroundColor:"swl-main-thin"`
* `has-swl-main-thin-background-color`
* 旧`swl-pale-02`形式

---

# 6. 番号付きリスト

順番が重要な内容には以下を使用する。

```html
<!-- wp:list {"ordered":true} -->
<ol class="wp-block-list"><!-- wp:list-item -->
<li>ステップ1</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>ステップ2</li>
<!-- /wp:list-item --></ol>
<!-- /wp:list -->
```

番号付きリストへ通常ul用の、

* 背景色
* small指定
* `is-style-num_circle`
* `-list-under-dashed`

を付けない。

---

# 7. 囲いボックス内のリスト

囲いボックス内では装飾なしのリストを使用する。

```html
<!-- wp:list -->
<ul class="wp-block-list"><!-- wp:list-item -->
<li>項目</li>
<!-- /wp:list-item --></ul>
<!-- /wp:list -->
```

AIOは囲いボックスではないため、この例外には含まれない。

---

# 8. テーブル

基本形式：

```html
<!-- wp:table {"className":"has-xs-font-size"} -->
<figure class="wp-block-table has-xs-font-size"><table><thead><tr><th>見出し</th><th>見出し</th></tr></thead><tbody><tr><th scope="row">項目名</th><td>内容</td></tr></tbody></table></figure>
<!-- /wp:table -->
```

必須：

* figure：`class="wp-block-table has-xs-font-size"`
* ブロックコメント：`{"className":"has-xs-font-size"}`
* tbody内1列目：`<th scope="row">`

tbody内1列目を`<td>`にしない。

---

# 9. SWELL吹き出し

```html
<!-- wp:loos/balloon {"balloonID":"1","balloonTitle":"キャラ1"} -->
<p>セリフ</p>
<!-- /wp:loos/balloon -->
```

`balloonID`が未確定なら`"1"`のまま出力し、公開前確認事項として残す。

---

# 10. 吹き出し使用数

本文1,000文字につき1個を基準に、記事全体へ分散する（例：7,000文字 → 7個）。内容は05に従う。

---

# 11. X埋め込み

実在確認済みURLがある場合のみ使用する。

```html
<!-- wp:embed {"url":"https://x.com/ユーザー名/status/投稿ID","type":"rich","providerNameSlug":"twitter","responsive":true} -->
<figure class="wp-block-embed is-type-rich is-provider-twitter wp-block-embed-twitter"><div class="wp-block-embed__wrapper">
https://x.com/ユーザー名/status/投稿ID
</div></figure>
<!-- /wp:embed -->
```

未確保の場合：

```html
<!-- 【埋め込み追加枠①】X検索「（検索語）」で該当投稿URLを貼り付けてください -->
```

---

# 11-1. 口コミ引用ブロック

口コミ・評判記事で、X埋め込み以外の口コミ（楽天トラベル、みん評、Yahoo!知恵袋、YouTubeコメント）を引用する場合に使用する。引用元のルールは`08_review_reputation_rules.md`に従う。

```html
<!-- wp:quote -->
<blockquote class="wp-block-quote"><!-- wp:paragraph -->
<p>（原文どおりの短い引用）</p>
<!-- /wp:paragraph --><cite>出典：<a href="（投稿URL全文）" target="_blank" rel="noopener">（媒体名）</a>（投稿日：YYYY年M月D日）</cite></blockquote>
<!-- /wp:quote -->
```

* 出典リンクには`rel="noopener"`を付け、`sponsored`は付けない
* 投稿日が不明な場合は「（YYYY年M月D日確認）」と書く
* YouTubeコメントは動画URLをリンク先にし、`（媒体名）`を「YouTube（動画タイトル）のコメント」とする。`cite`内にコメント投稿者名と投稿時期を含める（例：`出典：<a …>YouTube（動画タイトル）のコメント</a>（投稿者：〇〇／YYYY年M月頃）`）
* 実在確認済みの投稿URLだけを使用する。URLを推測して作らない

---

# 13. 画像挿入枠

```html
<!-- 【画像挿入①】（何のスクショか）をここに挿入
alt="（alt文）" / キャプション例:「出典:（サービス名）公式サイト」 -->
```

画像番号は記事内で連番にする。

画像挿入枠は納品時に残してよい。

---

# 14. CTAリンク

配置とリンクの決め方は07 #5に従う（受領した申込みリンク → 確認済みの公式サイトURL → AFF_LINK の順）。

CTAリンクには必ず`target="_blank" rel="noopener sponsored"`を付ける。

---

# 15. CTA基本テンプレート

```html
<!-- ▼CTA 「AFF_LINK」をアフィリエイトリンクに差し替えてください -->
<!-- wp:group {"className":"cta-box","style":{"border":{"color":"#e5484d","width":"2px","radius":"12px"},"color":{"background":"#fff5f5"},"spacing":{"padding":{"top":"24px","bottom":"24px","left":"20px","right":"20px"}}},"layout":{"type":"constrained"}} -->
<div class="wp-block-group cta-box has-border-color has-background" style="border-color:#e5484d;border-width:2px;border-radius:12px;background-color:#fff5f5;padding-top:24px;padding-right:20px;padding-bottom:24px;padding-left:20px"><!-- wp:paragraph {"align":"center"} -->
<p class="has-text-align-center" style="color:#e5484d;font-size:1.1em"><strong>＼（確認済みの訴求文）／</strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph {"align":"center"} -->
<p class="has-text-align-center">（確認済みのメリット・条件・特徴）</p>
<!-- /wp:paragraph -->

<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->
<div class="wp-block-buttons"><!-- wp:button {"style":{"color":{"background":"#e5484d","text":"#ffffff"},"border":{"radius":"50px"},"typography":{"fontStyle":"normal","fontWeight":"700"}}} -->
<div class="wp-block-button"><a class="wp-block-button__link has-text-color has-background wp-element-button" style="border-radius:50px;color:#ffffff;background-color:#e5484d;font-weight:700" href="AFF_LINK" target="_blank" rel="noopener sponsored">（ボタン文言） &#9654;</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons -->

<!-- wp:paragraph {"align":"center","fontSize":"small"} -->
<p class="has-text-align-center has-small-font-size">※（対象条件・変更可能性・注意事項）</p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->
<!-- ▲CTA -->
```

開始コメントは、リンクの種類に応じて以下にする。

* 受領した申込みリンク：`<!-- ▼CTA -->`
* 公式サイトURL：`<!-- ▼CTA 公式サイトURLを仮設定中。アフィリエイトリンク取得後に差し替えてください -->`
* AFF_LINK：`<!-- ▼CTA 「AFF_LINK」をアフィリエイトリンクに差し替えてください -->`

開始コメント（`▼CTA`）・終了コメント（`▲CTA`）と`cta-box`クラスは、文字数計測でCTAを除外するために必ず維持する。

CTAの訴求内容は`05_article_writing.md`に従う。

---

# 15-1. 具体例CTA（3パターンの具体例の直後）

見積もり・査定額・料金シミュレーション等を3パターンの具体例で示した直後に置く、簡易版のCTA。指定案件の情報の場合だけ使う（09）。

```html
<!-- ▼CTA（具体例） -->
<!-- wp:group {"className":"cta-box","style":{"border":{"color":"#e5484d","width":"2px","radius":"12px"},"spacing":{"padding":{"top":"16px","bottom":"16px","left":"20px","right":"20px"}}},"layout":{"type":"constrained"}} -->
<div class="wp-block-group cta-box has-border-color" style="border-color:#e5484d;border-width:2px;border-radius:12px;padding-top:16px;padding-right:20px;padding-bottom:16px;padding-left:20px"><!-- wp:paragraph {"align":"center"} -->
<p class="has-text-align-center"><strong>（自分のケースの結果が分かる行動。例：写真3枚で無料査定・最短15分）</strong></p>
<!-- /wp:paragraph -->

<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->
<div class="wp-block-buttons"><!-- wp:button {"style":{"color":{"background":"#e5484d","text":"#ffffff"},"border":{"radius":"50px"},"typography":{"fontStyle":"normal","fontWeight":"700"}}} -->
<div class="wp-block-button"><a class="wp-block-button__link has-text-color has-background wp-element-button" style="border-radius:50px;color:#ffffff;background-color:#e5484d;font-weight:700" href="（見積もり・査定・シミュレーションの該当ページURL）" target="_blank" rel="noopener sponsored">（行動が分かるボタン文言。例：無料で査定額を調べる） &#9654;</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons --></div>
<!-- /wp:group -->
<!-- ▲CTA -->
```

* 開始コメントは`<!-- ▼CTA（具体例） -->`、終了コメントは`<!-- ▲CTA -->`にする（文字数計測でCTAとして除外される）
* 公式サイトURLを仮設定する場合は、開始コメントを`<!-- ▼CTA（具体例） 公式サイトURLを仮設定中。アフィリエイトリンク取得後に差し替えてください -->`にする
* 「自分のケースを調べる方法」の説明と該当ページへのテキストリンクは、このCTAの**外**（直前の通常段落）に書く。CTA枠の中に本文の説明を入れない

---

# 16. CTAボタン文言

使用可能な例：

```text
〇〇の公式サイトを見てみる ▶
```

```text
公式サイトで査定を申し込む ▶
```

```text
公式サイトで料金を確認する ▶
```

```text
キャンペーン条件を確認する ▶
```

```text
〇〇の買取サービスを確認する ▶
```

リンク先・行動内容が分からない、

```text
詳しくはこちら
```

だけの文言は避ける。

---

# 17. CTA配色

標準：

* メイン：`#e5484d`
* 背景：`#fff5f5`

必要に応じて記事ジャンルに合わせて変更してよい。

---

# 18. AIO型要点サマリー

AIOは囲いボックスを使わず、

* paragraph
* list
* ordered list

だけで実装する。

使用しない：

* `wp:group`
* `has-border`
* `-border02`

---

# 19. AIO基本形式

```html
<!-- wp:paragraph -->
<p><strong>（直答）</strong>（条件・理由）</p>
<!-- /wp:paragraph -->

<!-- wp:list {"className":"is-style-num_circle -list-under-dashed","style":{"color":{"background":"var(--color_main_thin)"}},"fontSize":"small"} -->
<ul class="wp-block-list is-style-num_circle -list-under-dashed has-background has-small-font-size" style="background-color:var(--color_main_thin)"><!-- wp:list-item -->
<li><strong>（ラベル）</strong>:（説明）</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><strong>（ラベル）</strong>:（説明）</li>
<!-- /wp:list-item --></ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>（例外・判断材料）</p>
<!-- /wp:paragraph -->
```

AIOに必要な内容・設置場所は`05_article_writing.md`に従う。

---

# 20. 「この記事を読んでわかること」

本文内容は`03_title_structure.md`および`05_article_writing.md`に従う。

「この記事を読んでわかること」は見出しではない。

以下を必須とする。

* `h2`・`h3`・`h4`等の見出しタグを使用しない
* `wp:heading`ブロックを使用しない
* タイトル文言は通常段落内の`<strong>`で表示する
* タイトル文言と5項目のリストを同じ囲みボックス内へ入れる
* 囲みボックス内のリストは装飾なしのulを使用する
* 通常ul用の`is-style-num_circle`、背景色、small指定は付けない

基本形式：

```html
<!-- wp:group {"style":{"border":{"radius":"8px"},"color":{"background":"var(--color_main_thin)"},"spacing":{"padding":{"top":"20px","bottom":"20px","left":"20px","right":"20px"}}},"layout":{"type":"constrained"}} -->
<div class="wp-block-group has-background" style="border-radius:8px;background-color:var(--color_main_thin);padding-top:20px;padding-right:20px;padding-bottom:20px;padding-left:20px">

<!-- wp:paragraph -->
<p><strong>この記事を読んでわかること</strong></p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul class="wp-block-list"><!-- wp:list-item -->
<li>具体的な結論</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>具体的な結論</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>具体的な結論</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>具体的な結論</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>具体的な結論</li>
<!-- /wp:list-item --></ul>
<!-- /wp:list -->

</div>
<!-- /wp:group -->
```

項目数は5項目。

「この記事を読んでわかること」に対して、以下の形式は禁止する。

```html
<h2>この記事を読んでわかること</h2>
<h3>この記事を読んでわかること</h3>
<h4>この記事を読んでわかること</h4>
```

および、

```html
<!-- wp:heading -->
```

```html
<!-- wp:heading {"level":3} -->
```

など、すべての`wp:heading`ブロックを使用しない。


---

# 21. まとめリスト

まとめH2内の結論リストにも通常ul形式を使用する。

背景色を含む実装形式は、#5「通常の箇条書き」に従い、`var(--color_main_thin)`を使用する。

項目数は、

**8〜15項目**

とする。

内容ルールは`03_title_structure.md`および`05_article_writing.md`に従う。

---

# 22. 強調

重要語句は、

```html
<strong>重要な内容</strong>
```

を使用してよい。

段落全文を不必要にstrongへしない。

---

# 23. 外部リンク

実在確認済みURLだけを使用する。

アフィリエイトリンクには、

```html
rel="noopener sponsored"
```

を使用する。

---

# 24. PR表記

WordPress側の共通設定を使用するため、

**記事本文HTMLへPR表記を追加しない。**

---

# 25. 削除するHTML

出力前に以下を削除する。

* 空の`<p></p>`
* 空の`<div></div>`
* 空の`<span></span>`
* 不要なspan
* `href=""`
* `src=""`
* 空HTMLブロック
* 壊れたショートコード
* 意味のない連続改行
* 本当に未使用のプレースホルダー

---

# 26. 削除してはいけないもの

以下は保持する。

* Gutenberg開始・終了コメント
* 必要なSWELLクラス
* CTA構造
* 表・リスト構造
* 吹き出し構造
* `AFF_LINK`
* 画像挿入枠
* SNS追加枠
* balloonID確認
* 公開前作業コメント

---

# 27. 公開前作業コメント

納品時に残してよいもの：

* CTAリンク（公式サイトURL・AFF_LINK）のアフィリエイトリンクへの差し替え
* 画像挿入
* SNS埋め込み追加
* balloonID確認
* 公開前に人間が行う差し替え指示

削除するもの：

* AI内部メモ
* 構成検討メモ
* 古い修正指示
* 対応済み作業メモ
* 意味のない仮コメント

---

# 28. Gutenberg入れ子

ブロックの開始・終了順を正しく対応させる。

外側ブロックの中にある子ブロックを先に閉じる。

---

# 29. 目視で確認すること

`check_article.py`で確認されない以下は、出力前に目視で確認する。

* [ ] 通常ulに`is-style-num_circle -list-under-dashed`・背景`var(--color_main_thin)`・small指定がある（ordered list・囲みボックス内のリストには付けない）
* [ ] tableのfigureが`wp-block-table has-xs-font-size`
* [ ] AIOを`wp:group`やborder系クラスで囲っていない
* [ ] balloonIDが未確定なら`"1"`のまま、公開前作業に記載
* [ ] SNS・口コミのURLを推測していない
* [ ] 不要なAI作業メモがなく、必要な公開前作業コメント（画像挿入枠・SNS追加枠・リンク差し替え）は残っている
* [ ] スマホ表示：テーブルが過度に横長でない、長い段落が続かない、CTAボタンが読みやすい、装飾が集中しすぎない

---

# 30. 最終原則

このファイルでは、

**何を書くかではなく、どう正しく実装するか**

だけを決める。

最終HTMLでは、

1. Gutenbergで壊れない
2. SWELLで意図どおり表示される
3. スマホ・PCで読みやすい
4. 公開前の差し替え箇所が明確

ことを優先する。
