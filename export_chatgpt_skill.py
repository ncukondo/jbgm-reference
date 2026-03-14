"""Claude Code用のreferenceデータをChatGPT Skills形式にエクスポートするスクリプト

Agent Skills オープンスタンダード (agentskills.io) 準拠のZIPを生成する。
ChatGPTの Settings → Capabilities → Upload Skill からアップロード可能。
"""

import os
import shutil
import zipfile

CLAUDE_REFERENCE_DIR = ".claude/skills/jbgm-reference/reference"
CLAUDE_SKILL_MD = ".claude/skills/jbgm-reference/SKILL.md"
DIST_DIR = "dist"
CHATGPT_SKILL_DIR = os.path.join(DIST_DIR, "jbgm-reference")
OUTPUT_ZIP = os.path.join(DIST_DIR, "jbgm-reference.zip")

# ChatGPT用のSKILL.md（Agent Skills標準フォーマット）
CHATGPT_SKILL_MD = """\
---
name: jbgm-reference
description: >-
  総合診療専門医制度（認定・更新・移行措置・研修プログラム・指導医・ダブルボード等）
  についての質問に、jbgm.orgから収集した公式資料とFAQを検索して回答する。
  日本専門医機構 総合診療専門医検討委員会の公開情報に基づく。
---

# 総合診療専門医制度 リファレンス検索

ユーザーの質問に対して、このスキルの `references/` にある公式資料とFAQを検索し、正確に回答してください。

## 参照資料

全体目次は `references/index.md` を参照してください。

資料は以下のカテゴリに分類されています:

| ディレクトリ | 内容 | 主な検索対象 |
|---|---|---|
| 01_専門医認定 | 認定試験の実施要領・受験資格 | 試験日程、受験区分、出題数、受験料 |
| 02_専門医更新 | 更新要件・更新試験・費用・提出書類 | 必要単位数、更新料、IBT試験、My Portfolio |
| 03_移行措置 | 移行措置規則 | 対象者、期限、条件 |
| 04_指導医・講習会 | 指導医認定更新・講習会 | 特任指導医、講習会申込、認定フロー |
| 05_研修プログラム | 整備基準・研修の流れ・評価 | チェックリスト、J-GOAL、カリキュラム制 |
| 06_ダブルボード | 内科/救急科ダブルボード | 期間短縮、単位換算 |
| 07_規則・細則 | ハラスメント細則等 | 細則 |
| 08_その他 | 生涯学修等 | WS報告書 |

各カテゴリ内に `FAQ_*.md` ファイル（公式Q&A）があります。

## 検索手順

1. **キーワード抽出**: ユーザーの質問から検索キーワードを特定する
2. **カテゴリ絞り込み**: 上記の表を参考に関連カテゴリを特定する
3. **ファイル検索**: `references/` 内の関連ファイルをキーワードで検索する
4. **内容確認**: マッチしたファイルを読み、回答に必要な情報を収集する
5. **FAQ 確認**: `FAQ_` プレフィックスのファイルに関連Q&Aがないか確認する

## 回答のルール

- 参照資料の内容に基づいて回答すること。資料に記載がない内容は推測せず「資料に記載なし」と明記する
- 金額・期限・単位数などの数値情報は原文のまま引用する
- 関連するFAQがあれば併せて紹介する
- 複数の資料に関連情報がある場合はまとめて整理する
- **出典の明示（必須）**: 回答の末尾に「参考資料」セクションを設け、回答に使用した資料の元情報を一覧で示すこと。各参照ファイルの先頭にある `出典:` （元のPDF/ページURL）と `収集元ページ:` （jbgm.orgの該当メニューページ）を抽出し、以下の形式で記載する:

```
### 参考資料
- [資料タイトル](出典URL)（[収集元ページ](収集元ページURL)）
- [FAQ: カテゴリ名](https://jbgm.org/qa/)（[個別Q&AのURL](参照元URL)）
```
"""


def export():
    """ChatGPT Skills形式でエクスポートする"""
    # 元データの存在確認
    if not os.path.exists(CLAUDE_REFERENCE_DIR):
        print(f"Error: {CLAUDE_REFERENCE_DIR} が見つかりません。")
        print("先に organize_reference.py を実行してください。")
        raise SystemExit(1)

    # 古い出力を削除
    if os.path.exists(CHATGPT_SKILL_DIR):
        shutil.rmtree(CHATGPT_SKILL_DIR)
    os.makedirs(CHATGPT_SKILL_DIR, exist_ok=True)

    # SKILL.md を生成
    skill_path = os.path.join(CHATGPT_SKILL_DIR, "SKILL.md")
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(CHATGPT_SKILL_MD)
    print(f"Created: {skill_path}")

    # references/ にコピー（Agent Skills標準のディレクトリ名）
    dst_references = os.path.join(CHATGPT_SKILL_DIR, "references")
    shutil.copytree(CLAUDE_REFERENCE_DIR, dst_references)
    file_count = sum(
        len(files) for _, _, files in os.walk(dst_references) if files
    )
    print(f"Copied: {CLAUDE_REFERENCE_DIR} -> {dst_references} ({file_count} files)")

    # ZIP作成
    if os.path.exists(OUTPUT_ZIP):
        os.remove(OUTPUT_ZIP)

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(CHATGPT_SKILL_DIR):
            for file in sorted(files):
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, DIST_DIR)
                zf.write(file_path, arcname)

    zip_size = os.path.getsize(OUTPUT_ZIP)
    print(f"\nCreated: {OUTPUT_ZIP} ({zip_size / 1024:.0f} KB)")
    print(f"\nChatGPTへのインストール:")
    print(f"  Settings → Capabilities → Upload Skill から {OUTPUT_ZIP} をアップロード")


if __name__ == "__main__":
    export()
