import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# 1. ページを取得
url = "https://jbgm.org/qa/"
resp = requests.get(url)
resp.encoding = resp.apparent_encoding  # 文字化け対策

# 2. BeautifulSoup で解析
soup = BeautifulSoup(resp.text, "html.parser")

# 3. 質問と回答要素を探す
qa_list = soup.select(".qa_type_list dl")
categories = []

for dl in qa_list:
    category = dl.find("dt").get_text(strip=True)
    sub_categories = []
    for a in dl.select("dd ul a"):
        sub_category = a.get_text(strip=True)
        link = a["href"]
        sub_categories.append({"sub_category": sub_category, "link": link})
        # サブカテゴリページにアクセスして個別質問のURLを取得
        sub_resp = requests.get(link)
        sub_resp.encoding = sub_resp.apparent_encoding
        sub_soup = BeautifulSoup(sub_resp.text, "html.parser")
        question_links = [
            a["href"] for a in sub_soup.select(".qa_list_a a")
        ]
        questions = []
        for q_link in question_links:
            q_resp = requests.get(q_link)
            q_resp.encoding = q_resp.apparent_encoding
            q_soup = BeautifulSoup(q_resp.text, "html.parser")
            question = q_soup.select_one(".qa_page_single > dl > dt")
            answer = q_soup.select_one(".qa_page_single >  dl > dd")
            # .qa_page_single > dl 内のリンクurlとタイトルテキストを取得
            links_in_dl = []
            for link_tag in q_soup.select(".qa_page_single > dl a"):
                link_url = link_tag.get("href")
                link_text = link_tag.get_text(strip=True)
                links_in_dl.append({"url": link_url, "title": link_text})
            if question and answer:
                questions.append({
                    "question": question.get_text(strip=True),
                    "answer": answer.get_text(strip=True),
                    "url": q_link,
                    "links_in_dl": links_in_dl
                })
                print(f"Question: {question.get_text(strip=True)}, Answer: {answer.get_text(strip=True)}")
        sub_categories[-1]["questions"] = questions
    print(f"Category: {category}, Sub-categories: {len(sub_categories)}")
    categories.append({"category": category, "sub_categories": sub_categories})

# 4. データをJSONファイルに保存
with open("output/qa_data.json", "w", encoding="utf-8") as f:
    json.dump(categories, f, ensure_ascii=False, indent=2)

# 5. Markdownファイルに保存
with open("output/qa_data.md", "w", encoding="utf-8") as f:
    for category in categories:
        f.write(f"# {category['category']}\n\n")
        for sub_category in category["sub_categories"]:
            f.write(f"## {sub_category['sub_category']}\n\n")
            for question in sub_category["questions"]:
                f.write(f"### {question['question']}\n\n")
                f.write(f"{question['answer']}\n\n")
                f.write(f"- [参照元]({question['url']})\n")
                if question["links_in_dl"]:
                    f.write("- 関連リンク\n")
                    for link in question["links_in_dl"]:
                        f.write(f"    - [{link['title']}]({link['url']})\n")
                f.write("\n")

# 6. データをDataFrameに変換
rows = []
for category in categories:
    for sub_category in category["sub_categories"]:
        for question in sub_category["questions"]:
            rows.append({
                "category": category["category"],
                "sub_category": sub_category["sub_category"],
                "question": question["question"],
                "answer": question["answer"],
                "url": question["url"],
                "links_in_dl": json.dumps(question["links_in_dl"], ensure_ascii=False)
            })
df = pd.DataFrame(rows, columns=["category", "sub_category", "question", "answer", "url", "links_in_dl"])

# 7. CSVファイルに保存
df.to_csv("output/qa_data.csv", index=False, encoding="utf-8-sig")