.PHONY: all scrape build export-chatgpt clean help

# デフォルト: 全ステップ実行
all: scrape build export-chatgpt

# 1. jbgm.org からデータ収集
scrape:
	uv run scrape_qa.py
	uv run scrape_pdfs.py

# 2. referenceディレクトリを構築 (Claude Code用)
build:
	uv run organize_reference.py

# 3. ChatGPT Skills形式でエクスポート
export-chatgpt:
	uv run export_chatgpt_skill.py

# 更新フロー: scrape → build → export (allと同じ)
update: all

# 掃除
clean:
	rm -rf dist/

help:
	@echo "使い方:"
	@echo "  make all            全ステップ実行 (scrape → build → export)"
	@echo "  make scrape         jbgm.org からデータ収集"
	@echo "  make build          Claude Code用 referenceディレクトリ構築"
	@echo "  make export-chatgpt ChatGPT Skills用 ZIP生成"
	@echo "  make update         全ステップ実行 (allと同じ)"
	@echo "  make clean          dist/ を削除"
