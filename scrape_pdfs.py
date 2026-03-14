"""jbgm.org からBox上のPDFリンクを収集・ダウンロード・テキスト抽出するスクリプト"""

import re
import json
import os
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF


# --- 設定 ---
SITE_URL = "https://jbgm.org"
PAGES_TO_SCAN = [
    "/menu/専門医認定試験/",
    "/menu/認定・更新/",
    "/menu/基準・細則等/",
    "/menu/生涯学修/",
    "/menu/講習会/",
    "/menu/研修の流れ-2/",
    "/menu/専門研修プログラム/",
    "/menu/ダブルボード/",
]
PDF_DIR = "pdfs"
TEXT_DIR = "texts"
OUTPUT_DIR = "output"


def collect_box_links(session: requests.Session) -> list[dict]:
    """jbgm.org の各ページからBox共有リンクを収集する"""
    box_links = {}

    for page_path in PAGES_TO_SCAN:
        url = SITE_URL + page_path
        print(f"Scanning: {url}")
        try:
            resp = session.get(url, timeout=30)
            resp.encoding = resp.apparent_encoding
        except requests.RequestException as e:
            print(f"  Skip (error): {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "box.com/s/" in href or "box.com/file/" in href:
                title = a.get_text(strip=True) or "untitled"
                # 正規化: jmsb.box.com → jmsb.app.box.com
                href = href.replace("jmsb.box.com", "jmsb.app.box.com")
                if href not in box_links:
                    box_links[href] = {
                        "url": href,
                        "title": title,
                        "source_page": unquote(page_path),
                    }
                    print(f"  Found: {title}")

    return list(box_links.values())


def download_box_pdf(session: requests.Session, shared_url: str, output_path: str) -> bool:
    """Box共有リンクからPDFをダウンロードする"""
    try:
        resp = session.get(shared_url, timeout=30)
    except requests.RequestException as e:
        print(f"  Page fetch error: {e}")
        return False

    content = resp.text

    # requestToken と fileID を抽出
    rt_match = re.search(r'"requestToken"\s*:\s*"([^"]+)"', content)
    fid_match = re.search(r'"typedID"\s*:\s*"f_(\d+)"', content)

    if not (rt_match and fid_match):
        print("  Failed to extract token/fileID")
        return False

    request_token = rt_match.group(1)
    file_id = fid_match.group(1)

    # Box APIでアクセストークンを取得
    try:
        token_resp = session.post(
            "https://jmsb.app.box.com/app-api/enduserapp/elements/tokens",
            json={"fileIDs": [f"file_{file_id}"]},
            headers={
                "Request-Token": request_token,
                "X-Request-Token": request_token,
            },
            timeout=30,
        )
        token_data = token_resp.json()
        access_token = token_data.get(f"file_{file_id}", {}).get("read", "")
    except (requests.RequestException, ValueError) as e:
        print(f"  Token error: {e}")
        return False

    if not access_token:
        print("  No access token")
        return False

    # shared_items APIでファイル情報取得 → ダウンロード
    try:
        dl_resp = session.get(
            f"https://api.box.com/2.0/files/{file_id}/content",
            headers={
                "Authorization": f"Bearer {access_token}",
                "BoxApi": f"shared_link={shared_url}",
            },
            allow_redirects=True,
            timeout=60,
        )
    except requests.RequestException as e:
        print(f"  Download error: {e}")
        return False

    if dl_resp.content[:4] == b"%PDF":
        with open(output_path, "wb") as f:
            f.write(dl_resp.content)
        print(f"  OK: {len(dl_resp.content):,} bytes")
        return True

    print(f"  Not a PDF (status={dl_resp.status_code})")
    return False


def extract_text(pdf_path: str, txt_path: str) -> str:
    """PDFからテキストを抽出する"""
    doc = fitz.open(pdf_path)
    pages = doc.page_count
    text = ""
    for i in range(pages):
        text += doc[i].get_text() + f"\n--- page {i + 1}/{pages} ---\n"
    doc.close()

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    return text


def safe_filename(title: str) -> str:
    """タイトルからファイル名を生成する"""
    name = re.sub(r'[\\/:*?"<>|]', "_", title)
    name = name.strip()[:80]
    return name or "untitled"


def main():
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(TEXT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    # 1. リンク収集
    print("=" * 60)
    print("Step 1: Collecting Box links from jbgm.org")
    print("=" * 60)
    links = collect_box_links(session)
    print(f"\nFound {len(links)} Box links total\n")

    # リンク一覧を保存
    with open(f"{OUTPUT_DIR}/box_links.json", "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

    # 2. PDFダウンロード
    print("=" * 60)
    print("Step 2: Downloading PDFs from Box")
    print("=" * 60)
    results = []
    for i, link in enumerate(links, 1):
        filename = safe_filename(link["title"]) + ".pdf"
        pdf_path = os.path.join(PDF_DIR, filename)

        # 既にダウンロード済みならスキップ
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 100:
            print(f"[{i}/{len(links)}] Skip (exists): {filename}")
            link["pdf_path"] = pdf_path
            link["downloaded"] = True
            results.append(link)
            continue

        print(f"[{i}/{len(links)}] {link['title']}")
        ok = download_box_pdf(session, link["url"], pdf_path)
        link["pdf_path"] = pdf_path if ok else None
        link["downloaded"] = ok
        results.append(link)

    downloaded = sum(1 for r in results if r["downloaded"])
    print(f"\nDownloaded: {downloaded}/{len(results)}\n")

    # 3. テキスト抽出
    print("=" * 60)
    print("Step 3: Extracting text from PDFs")
    print("=" * 60)
    for r in results:
        if not r.get("downloaded") or not r.get("pdf_path"):
            continue
        pdf_path = r["pdf_path"]
        txt_name = os.path.splitext(os.path.basename(pdf_path))[0] + ".txt"
        txt_path = os.path.join(TEXT_DIR, txt_name)

        try:
            text = extract_text(pdf_path, txt_path)
            r["text_path"] = txt_path
            r["text_length"] = len(text)
            print(f"  {txt_name}: {len(text):,} chars")
        except Exception as e:
            print(f"  {txt_name}: ERROR - {e}")
            r["text_path"] = None

    # 4. 結果を保存
    with open(f"{OUTPUT_DIR}/scrape_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Results saved to {OUTPUT_DIR}/scrape_results.json")


if __name__ == "__main__":
    main()
