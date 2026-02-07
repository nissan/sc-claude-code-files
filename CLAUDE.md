# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Course materials and companion code for the DeepLearning.AI short course "Claude Code: A Highly Agentic Coding Assistant". This repo contains reading notes, lesson files, and links — not a traditional software project with build/test pipelines.

## Structure

- `reading_notes/` — Lesson notes (L0-L8) with prompts, summaries, and feature walkthroughs
- `updated_reading_notes/` — Revised versions of select lesson notes
- `lesson7_files/` — Complete e-commerce data analysis project (the only runnable code in this repo)
- `additional_files/` — Figma mockup (`key-indicators.fig`) and a visualization HTML from Lesson 1
- `links_to_course_repos.md` — Links to external repos used in lessons 2-6 and 8

## Lesson 7 Project (lesson7_files/)

This is the only code project in the repo. It's a Python-based e-commerce analytics suite with two interfaces:

**Architecture:**
- `data_loader.py` — `EcommerceDataLoader` class: loads 6 CSV files from `ecommerce_data/`, cleans timestamps, and joins them into a filtered sales dataset via `create_sales_dataset()`
- `business_metrics.py` — `BusinessMetricsCalculator` (revenue, product, geographic, satisfaction, delivery metrics) and `MetricsVisualizer` (matplotlib + plotly charts). Takes the sales dataset as input.
- `dashboard.py` — Streamlit app that wires `data_loader` and `business_metrics` together with interactive year/month filters, KPI cards, and a 2x2 Plotly chart grid
- `EDA.ipynb` — Original exploratory notebook; `EDA_Refactored-original.ipynb` — refactored version using the modules above

**Data flow:** CSV files → `EcommerceDataLoader.load_raw_data()` → `process_all_data()` → `create_sales_dataset(year, month, status)` → `BusinessMetricsCalculator` → metrics dict / `MetricsVisualizer`

**Commands (run from `lesson7_files/`):**
```bash
pip install -r requirements.txt
streamlit run dashboard.py
jupyter notebook EDA_Refactored-original.ipynb
```

**Dependencies:** pandas, numpy, matplotlib, seaborn, plotly, streamlit, jupyter

## Course Context

The course teaches Claude Code best practices through three projects:
1. RAG chatbot codebase (Lessons 2-6) — external repos, not in this repo
2. E-commerce data analysis (Lesson 7) — in `lesson7_files/`
3. Figma-to-Next.js dashboard (Lesson 8) — external repo, mockup file in `additional_files/`
