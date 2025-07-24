# 必要なライブラリを読み込み
if (!require("pacman", quietly = TRUE)) install.packages("pacman")
pacman::p_load(rvest, httr, jsonlite, dplyr, readr)

# 出力ディレクトリを作成
output_dir <- "output"
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# 1. ページを取得
url <- "https://jbgm.org/qa/"
resp <- GET(url)
content_html <- content(resp, as = "text", encoding = "UTF-8")

# 2. rvest で解析
page <- read_html(content_html)

# 3. 質問と回答要素を探す
qa_list <- page %>% html_nodes(".qa_type_list dl")
categories <- list()

for (i in seq_along(qa_list)) {
  dl <- qa_list[[i]]
  category <- dl %>% html_node("dt") %>% html_text(trim = TRUE)
  
  sub_categories <- list()
  links <- dl %>% html_nodes("dd ul a")
  
  for (j in seq_along(links)) {
    a <- links[[j]]
    sub_category <- a %>% html_text(trim = TRUE)
    link <- a %>% html_attr("href")
    
    # サブカテゴリページにアクセスして個別質問のURLを取得
    sub_resp <- GET(link)
    sub_content <- content(sub_resp, as = "text", encoding = "UTF-8")
    sub_page <- read_html(sub_content)
    
    question_links <- sub_page %>% 
      html_nodes(".qa_list_a a") %>% 
      html_attr("href")
    
    questions <- list()
    
    for (k in seq_along(question_links)) {
      q_link <- question_links[[k]]
      q_resp <- GET(q_link)
      q_content <- content(q_resp, as = "text", encoding = "UTF-8")
      q_page <- read_html(q_content)
      
      question_node <- q_page %>% html_node(".qa_page_single > dl > dt")
      answer_node <- q_page %>% html_node(".qa_page_single > dl > dd")
      
      # .qa_page_single > dl 内のリンクurlとタイトルテキストを取得
      links_in_dl <- list()
      link_tags <- q_page %>% html_nodes(".qa_page_single > dl a")
      
      for (l in seq_along(link_tags)) {
        link_tag <- link_tags[[l]]
        link_url <- link_tag %>% html_attr("href")
        link_text <- link_tag %>% html_text(trim = TRUE)
        links_in_dl[[l]] <- list(url = link_url, title = link_text)
      }
      
      if (!is.na(question_node) && !is.na(answer_node)) {
        question_text <- question_node %>% html_text(trim = TRUE)
        answer_text <- answer_node %>% html_text(trim = TRUE)
        
        questions[[k]] <- list(
          question = question_text,
          answer = answer_text,
          url = q_link,
          links_in_dl = links_in_dl
        )
        
        cat("Question:", question_text, ", Answer:", answer_text, "\n")
      }
    }
    
    sub_categories[[j]] <- list(
      sub_category = sub_category,
      link = link,
      questions = questions
    )
  }
  
  cat("Category:", category, ", Sub-categories:", length(sub_categories), "\n")
  categories[[i]] <- list(
    category = category,
    sub_categories = sub_categories
  )
}

# 4. データをJSONファイルに保存
json_data <- toJSON(categories, auto_unbox = TRUE, pretty = TRUE)
write(json_data, file = file.path(output_dir, "qa_data.json"))

# 5. Markdownファイルに保存
md_content <- ""
for (i in seq_along(categories)) {
  category <- categories[[i]]
  md_content <- paste0(md_content, "# ", category$category, "\n\n")
  
  for (j in seq_along(category$sub_categories)) {
    sub_category <- category$sub_categories[[j]]
    md_content <- paste0(md_content, "## ", sub_category$sub_category, "\n\n")
    
    for (k in seq_along(sub_category$questions)) {
      question <- sub_category$questions[[k]]
      md_content <- paste0(md_content, "### ", question$question, "\n\n")
      md_content <- paste0(md_content, question$answer, "\n\n")
      md_content <- paste0(md_content, "- [参照元](", question$url, ")\n")
      
      if (length(question$links_in_dl) > 0) {
        md_content <- paste0(md_content, "- 関連リンク\n")
        for (l in seq_along(question$links_in_dl)) {
          link <- question$links_in_dl[[l]]
          md_content <- paste0(md_content, "    - [", link$title, "](", link$url, ")\n")
        }
      }
      md_content <- paste0(md_content, "\n")
    }
  }
}

write(md_content, file = file.path(output_dir, "qa_data.md"))

# 6. データをデータフレームに変換
rows <- list()
row_count <- 1

for (i in seq_along(categories)) {
  category <- categories[[i]]
  for (j in seq_along(category$sub_categories)) {
    sub_category <- category$sub_categories[[j]]
    for (k in seq_along(sub_category$questions)) {
      question <- sub_category$questions[[k]]
      
      rows[[row_count]] <- data.frame(
        category = category$category,
        sub_category = sub_category$sub_category,
        question = question$question,
        answer = question$answer,
        url = question$url,
        links_in_dl = toJSON(question$links_in_dl, auto_unbox = TRUE),
        stringsAsFactors = FALSE
      )
      row_count <- row_count + 1
    }
  }
}

# データフレームを結合
df <- do.call(rbind, rows)

# 7. CSVファイルに保存
write_csv(df, file.path(output_dir, "qa_data.csv"))

cat("スクレイピングが完了しました。\n")
cat("出力ファイル:\n")
cat("- ", file.path(output_dir, "qa_data.json"), "\n")
cat("- ", file.path(output_dir, "qa_data.md"), "\n") 
cat("- ", file.path(output_dir, "qa_data.csv"), "\n")
