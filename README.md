# jbgm-reference

[日本専門医機構 総合診療専門医検討委員会](https://jbgm.org/)の公開情報（公式資料・FAQ）を収集・整理した Agent Skills です。

総合診療専門医制度（認定・更新・移行措置・研修プログラム・指導医・ダブルボード等）についての質問に、公式資料を検索して回答します。

## インストール

### Claude.ai / ChatGPT

1. [Releases](https://github.com/ncukondo/jbgm-reference/releases) から `jbgm-reference.zip` をダウンロード
2. アップロード:
   - **Claude.ai**: Settings → Features → Upload Skill
   - **ChatGPT**: Settings → Capabilities → Upload Skill

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

## 収録データ

| カテゴリ | 内容 |
|---|---|
| 専門医認定 | 認定試験の実施要領・受験資格 |
| 専門医更新 | 更新要件・更新試験・費用・提出書類 |
| 移行措置 | 移行措置規則 |
| 指導医・講習会 | 指導医認定更新・講習会 |
| 研修プログラム | 整備基準・研修の流れ・評価 |
| ダブルボード | 内科/救急科ダブルボード |
| 規則・細則 | ハラスメント細則等 |
| その他 | 生涯学修等 |

## データ更新（開発者向け）

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

## 注意事項

- このスキルは jbgm.org の公開情報に基づいています。最新・正確な情報は [jbgm.org](https://jbgm.org/) を直接ご確認ください
- 資料に記載がない内容については「記載なし」と回答します
