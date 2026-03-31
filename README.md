# 総合診療専門医制度 リファレンス

[日本専門医機構 総合診療専門医検討委員会（jbgm.org）](https://jbgm.org/)が公開している資料・FAQを、ChatGPT や Claude で手軽に検索できるようにしたものです。

「更新に必要な単位数は？」「ダブルボードの要件は？」のように普段の言葉で質問するだけで、公式資料に基づいた回答と出典リンクが返ってきます。

---

## こんな質問ができます

- 専門医更新に必要な単位数を教えて
- 認定試験の受験料はいくら？
- 移行措置の対象者と期限は？
- 指導医になるにはどうすればいい？
- 内科とのダブルボードで研修期間は短縮される？

---

## 使い方

### 用意するもの

- **ChatGPT** の有料プラン（Plus / Team / Enterprise）、または
- **Claude** の有料プラン（Pro / Team / Enterprise）

無料プランではこの機能を利用できません。

### 手順1：ファイルをダウンロードする

下のボタンをクリックして、設定用ファイル（jbgm-reference.zip）をパソコンに保存してください。

> **[ダウンロードはこちら](https://github.com/ncukondo/jbgm-reference/releases/latest/download/jbgm-reference.zip)**

### 手順2：ChatGPT または Claude にアップロードする

#### ChatGPT の場合

1. [chatgpt.com](https://chatgpt.com) を開きます
2. 画面右上の自分のアイコンをクリック →「**Settings（設定）**」を選択します
3. 左メニューから「**Customization（カスタマイズ）**」を選びます
4. 「**Agent skills**」にある「**Upload skill**」ボタンをクリックします
5. 手順1で保存した `jbgm-reference.zip` を選択します
6. 設定画面を閉じます

#### Claude の場合

1. [claude.ai](https://claude.ai) を開きます
2. 画面右上の自分のアイコンをクリック →「**Settings（設定）**」を選択します
3. 左メニューから「**Features（機能）**」を選びます
4. 「**Skills**」にある「**Upload skill**」ボタンをクリックします
5. 手順1で保存した `jbgm-reference.zip` を選択します
6. 設定画面を閉じます

### 手順3：質問する

設定は以上で完了です。あとは **新しいチャットを開いて** 質問するだけです。

総合診療専門医制度に関する質問をすると、AIが自動的に収録資料を検索して、出典付きで回答します。特別な操作は必要ありません。

---

## うまくいかないときは

| 症状 | 対処法 |
| --- | --- |
| 「Upload skill」ボタンが見つからない | 有料プランに加入しているか確認してください |
| 質問しても資料を使った回答にならない | 新しいチャットを開いて質問してみてください |
| 古い情報が返ってくる | [こちら](https://github.com/ncukondo/jbgm-reference/releases)から最新版をダウンロードし直してください |

---

## 収録データについて

[jbgm.org](https://jbgm.org/) から収集した公式資料・FAQを以下のカテゴリに分類して収録しています。

| カテゴリ | 含まれる内容の例 |
| --- | --- |
| 専門医認定 | 認定試験の実施要領・受験資格・受験区分・出題数 |
| 専門医更新 | 更新要件・更新試験（IBT）・費用・提出書類・My Portfolio |
| 移行措置 | 移行措置規則・対象者・期限・条件 |
| 指導医・講習会 | 指導医認定フロー・特任指導医・講習会申込 |
| 研修プログラム | 整備基準・研修の流れ・J-GOAL・チェックリスト・カリキュラム制 |
| ダブルボード | 内科/救急科ダブルボード・期間短縮・単位換算 |
| 規則・細則 | ハラスメント細則 等 |
| その他 | 生涯学修 等 |

---

## 注意事項

- このデータは jbgm.org の**公開情報**に基づいています。最新・正確な情報は必ず [jbgm.org](https://jbgm.org/) を直接ご確認ください
- 資料に記載がない内容については「資料に記載なし」と回答します
- 回答には必ず出典（元の資料へのリンク）が付きます

---

<details>
<summary>開発者・技術者向け情報</summary>

### Claude Code

このリポジトリをクローンしてそのまま使えます:

```bash
git clone https://github.com/ncukondo/jbgm-reference.git
cd jbgm-reference
```

スキルは `.claude/skills/jbgm-reference/` に配置済みです。`/jbgm-reference 更新試験の受験料は？` のようにスラッシュコマンドで呼び出せます。

### Gemini CLI

```bash
git clone https://github.com/ncukondo/jbgm-reference.git
cp -r jbgm-reference/.claude/skills/jbgm-reference ~/.gemini/skills/jbgm-reference
```

### データ更新・リリース

jbgm.org から最新データを取得して再ビルドする場合:

```bash
uv sync
make all    # scrape → build → export
```

タグを push すると GitHub Actions が Release に ZIP を自動アタッチします:

```bash
git tag v0.0.2
git push origin v0.0.2
```

</details>
