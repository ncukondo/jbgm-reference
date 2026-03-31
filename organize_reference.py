"""PDFテキストとQ&Aデータを分類整理し、参照用ディレクトリを生成するスクリプト"""

import json
import os
import re
import shutil

REFERENCE_DIR = ".claude/skills/jbgm-reference/references"
TEXTS_DIR = "texts"
OUTPUT_DIR = "output"

# --- カテゴリ定義: (ディレクトリ名, 表示名, タイトルのキーワードマッチ, ソースページマッチ) ---
CATEGORIES = [
    {
        "dir": "01_専門医認定",
        "label": "専門医認定（新規）",
        "title_keywords": ["認定試験", "実施要領", "受験資格", "受験申請", "一次審査", "二次審査"],
        "source_pages": [],
        "exclude_keywords": ["更新試験", "更新IBT", "セルフトレーニング", "指導医", "移行措置"],
        "qa_categories": ["認定試験"],
    },
    {
        "dir": "02_専門医更新",
        "label": "専門医更新",
        "title_keywords": [
            "更新試験", "更新IBT", "セルフトレーニング", "更新手続き",
            "認定・更新", "認定更新", "My Portfolio", "提出書類",
            "学修コンテンツ", "領域講習", "説明動画", "諸費用",
        ],
        "source_pages": [],
        "exclude_keywords": ["指導医認定", "指導医更新", "特任指導医認定", "プログラム整備"],
        "qa_categories": ["専門医", "更新試験"],
    },
    {
        "dir": "03_移行措置",
        "label": "移行措置",
        "title_keywords": ["移行措置"],
        "source_pages": [],
        "exclude_keywords": [],
        "qa_categories": ["移行措置"],
    },
    {
        "dir": "04_指導医・講習会",
        "label": "特任指導医・指導医・講習会",
        "title_keywords": [
            "指導医認定", "指導医更新", "特任指導医", "指導医活動休止",
            "指導医更新猶予", "7年間", "指導実績", "講習会",
        ],
        "source_pages": ["/menu/講習会/"],
        "exclude_keywords": ["ダブルボード"],
        "qa_categories": ["プログラム統括責任者／特任指導医／指導医"],
    },
    {
        "dir": "05_研修プログラム",
        "label": "研修プログラム・研修の流れ",
        "title_keywords": [
            "研修プログラム", "整備基準", "カリキュラム制", "単位制",
            "チェックリスト", "修了証明", "J-GOAL", "J-OSLER",
            "研修手帳", "診療場面評価", "360", "ディスカッション",
            "年次報告", "中断", "再開", "延長", "辞退",
            "医療資源の乏しい地域", "医師少数区域", "申請書",
            "申請の注意", "記入例", "プログラム", "説明会資料",
            "研修目標", "単位換算", "学会発表", "論文発表",
            "ブロック研修", "小児科研修", "救急科研修",
            "受講証明", "研修開始届",
        ],
        "source_pages": ["/menu/研修の流れ-2/", "/menu/専門研修プログラム/"],
        "exclude_keywords": ["ダブルボード", "認定・更新", "移行措置", "更新試験", "指導医認定"],
        "qa_categories": ["専門研修プログラム", "GRS　J－GOAL", "J-Osler"],
    },
    {
        "dir": "06_ダブルボード",
        "label": "ダブルボード",
        "title_keywords": ["ダブルボード"],
        "source_pages": ["/menu/ダブルボード/"],
        "exclude_keywords": [],
        "qa_categories": ["ダブルボード"],
    },
    {
        "dir": "07_規則・細則",
        "label": "規則・細則",
        "title_keywords": ["ハラスメント", "コロナ", "特別措置", "メンタルヘルス"],
        "source_pages": [],
        "exclude_keywords": ["更新IBT", "セルフトレーニング"],
        "qa_categories": [],
    },
    {
        "dir": "08_その他",
        "label": "その他・生涯学修",
        "title_keywords": ["生涯学修"],
        "source_pages": ["/menu/生涯学修/"],
        "exclude_keywords": [],
        "qa_categories": ["その他"],
    },
]

# タイトルが不明瞭なファイルの手動マッピング (Box URL -> わかりやすいタイトル)
TITLE_OVERRIDES = {
    "こちら": None,  # 除外（内容不明瞭）
    "https://jmsb.box.com/s/7yxm60xp7ql1ul0uq539sphi9lxkg9cq": None,  # URL名のファイルは除外
}


def classify_document(doc: dict) -> str:
    """文書をカテゴリに分類する"""
    title = doc.get("title", "")
    source = doc.get("source_page", "")

    for cat in CATEGORIES[:-1]:  # 最後の「その他」以外
        # 除外キーワードチェック
        if any(kw in title for kw in cat["exclude_keywords"]):
            continue

        # タイトルキーワードマッチ
        if any(kw in title for kw in cat["title_keywords"]):
            return cat["dir"]

        # ソースページマッチ
        if source in cat["source_pages"]:
            return cat["dir"]

    return CATEGORIES[-1]["dir"]


def classify_qa_category(qa_cat_name: str) -> str:
    """Q&Aカテゴリをディレクトリに分類する"""
    for cat in CATEGORIES:
        if qa_cat_name in cat.get("qa_categories", []):
            return cat["dir"]
    return CATEGORIES[-1]["dir"]


def clean_text(text: str) -> str:
    """PDFから抽出したテキストを整形する"""
    # ページ区切りを整理
    text = re.sub(r"\n-{3} page (\d+)/(\d+) -{3}\n", r"\n\n", text)
    text = re.sub(r"\n---PAGE---\n", "\n\n", text)
    # 連続空行を2つまでに
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_reference():
    # 古いreferenceディレクトリを削除
    if os.path.exists(REFERENCE_DIR):
        shutil.rmtree(REFERENCE_DIR)

    # ディレクトリ作成
    for cat in CATEGORIES:
        os.makedirs(os.path.join(REFERENCE_DIR, cat["dir"]), exist_ok=True)

    # --- PDF文書の分類・格納 ---
    with open(os.path.join(OUTPUT_DIR, "scrape_results.json"), encoding="utf-8") as f:
        docs = json.load(f)

    doc_by_category: dict[str, list] = {cat["dir"]: [] for cat in CATEGORIES}

    for doc in docs:
        if not doc.get("text_path"):
            continue
        text_path = doc["text_path"]
        if not os.path.exists(text_path):
            continue

        title = doc.get("title", "")
        # タイトルが不明瞭なファイルをスキップ
        if title in TITLE_OVERRIDES and TITLE_OVERRIDES[title] is None:
            continue

        cat_dir = classify_document(doc)
        doc_by_category[cat_dir].append(doc)

    # 各カテゴリごとにmarkdownを生成
    for cat in CATEGORIES:
        cat_docs = doc_by_category[cat["dir"]]
        if not cat_docs:
            continue

        cat_path = os.path.join(REFERENCE_DIR, cat["dir"])

        for doc in cat_docs:
            text_path = doc["text_path"]
            with open(text_path, encoding="utf-8") as f:
                raw_text = f.read()
            cleaned = clean_text(raw_text)
            if not cleaned or len(cleaned) < 10:
                continue

            title = doc["title"]
            safe_name = re.sub(r'[\\/:*?"<>|]', "_", title).strip()[:80]
            md_path = os.path.join(cat_path, f"{safe_name}.md")

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(f"- 出典: {doc['url']}\n")
                f.write(f"- 収集元ページ: https://jbgm.org{doc['source_page']}\n\n")
                f.write("---\n\n")
                f.write(cleaned)
                f.write("\n")

        print(f"{cat['label']}: {len(cat_docs)} documents")

    # --- Q&Aの分類・格納 ---
    with open(os.path.join(OUTPUT_DIR, "qa_data.json"), encoding="utf-8") as f:
        qa_data = json.load(f)

    for qa_cat in qa_data:
        cat_name = qa_cat["category"]
        cat_dir = classify_qa_category(cat_name)
        cat_path = os.path.join(REFERENCE_DIR, cat_dir)

        safe_name = re.sub(r'[\\/:*?"<>|]', "_", cat_name).strip()[:80]
        md_path = os.path.join(cat_path, f"FAQ_{safe_name}.md")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# FAQ: {cat_name}\n\n")
            f.write(f"- 出典: https://jbgm.org/qa/\n\n")

            for sc in qa_cat["sub_categories"]:
                f.write(f"## {sc['sub_category']}\n\n")
                for q in sc.get("questions", []):
                    f.write(f"### {q['question']}\n\n")
                    f.write(f"{q['answer']}\n\n")
                    f.write(f"- [参照元]({q['url']})\n")
                    links = q.get("links_in_dl", [])
                    if links:
                        for lnk in links:
                            f.write(f"    - [{lnk['title']}]({lnk['url']})\n")
                    f.write("\n")

        total_q = sum(len(sc.get("questions", [])) for sc in qa_cat["sub_categories"])
        print(f"FAQ {cat_name}: {total_q} Q&A -> {cat_dir}")

    # --- インデックス生成 ---
    generate_index(doc_by_category, qa_data)

    print(f"\nReference directory created: {REFERENCE_DIR}/")


def generate_index(doc_by_category: dict, qa_data: list):
    """reference/index.md を生成する"""
    index_path = os.path.join(REFERENCE_DIR, "index.md")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# 総合診療専門医 制度情報リファレンス\n\n")
        f.write("> 日本専門医機構 総合診療専門医検討委員会 (https://jbgm.org/) の公開情報を整理したものです。\n\n")
        f.write("---\n\n")

        for cat in CATEGORIES:
            cat_dir = cat["dir"]
            cat_path = os.path.join(REFERENCE_DIR, cat_dir)
            if not os.path.exists(cat_path):
                continue

            files = sorted(f for f in os.listdir(cat_path) if f.endswith(".md"))
            if not files:
                continue

            f.write(f"## {cat['label']}\n\n")

            # 文書ファイル（FAQ以外）
            doc_files = [fi for fi in files if not fi.startswith("FAQ_")]
            faq_files = [fi for fi in files if fi.startswith("FAQ_")]

            if doc_files:
                f.write("### 文書\n\n")
                for fi in doc_files:
                    display_name = fi.replace(".md", "")
                    f.write(f"- [{display_name}]({cat_dir}/{fi})\n")
                f.write("\n")

            if faq_files:
                f.write("### よくある質問\n\n")
                for fi in faq_files:
                    display_name = fi.replace("FAQ_", "").replace(".md", "")
                    f.write(f"- [{display_name}]({cat_dir}/{fi})\n")
                f.write("\n")

        # 問い合わせ先
        f.write("---\n\n")
        f.write("## 問い合わせ先\n\n")
        f.write("| 用途 | 連絡先 |\n")
        f.write("|------|--------|\n")
        f.write("| 申請関連 | support-gpr@jmsb.or.jp |\n")
        f.write("| 受講料関連 | gm_account@jmsb.or.jp |\n")
        f.write("| お問い合わせフォーム | https://jbgm.org/personal_information/ |\n")

    print(f"Index created: {index_path}")


if __name__ == "__main__":
    build_reference()
