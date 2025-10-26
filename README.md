# The AI Patent Analyst
🏆 **Winner — Google Cloud & Kaggle Hackathon (2025)**

This project was selected as a winner in the Google Cloud & Kaggle Hackathon. The submission demonstrates an end‑to‑end BigQuery AI pipeline and an interactive Streamlit demo.

<p align="center">
	<a href="https://www.kaggle.com/competitions/bigquery-ai-hackathon/hackathon-winners">
		<img src="https://img.shields.io/badge/Winner-Google%20Cloud%20%26%20Kaggle-brightgreen.svg" alt="Winner — Google Cloud & Kaggle Hackathon" width="220" />
	</a>
</p>

<p align="center"><em>Awarded Winner — Google Cloud & Kaggle Hackathon (2025).</em></p>

---

### From Unstructured PDFs to Interactive Strategic Intelligence with BigQuery AI

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://patent-search-analytics.streamlit.app/)

This repository contains the code for the interactive Streamlit dashboard and the data pipeline that transforms unstructured patent PDFs into a queryable knowledge graph, delivering real-time insights.

---

## 🚀 Live Demo & Video Walkthrough

The best way to experience this project is through the live, deployed prototype and the 2.5-minute video overview.

-   **Live Streamlit App:** [**https://patent-search-analytics.streamlit.app/**](https://patent-search-analytics.streamlit.app/)
-   **Video Walkthrough:** [**https://youtu.be/6WVi1cdd5fw**](https://youtu.be/6WVi1cdd5fw)

---

## 🎯 Business Impact & ROI

Manually analyzing technical patent data is a slow, expensive process. Our platform automates this workflow, delivering a significant and immediate return on investment.

-   **Expert Hours Automated:** 600+
-   **Manual Cost Avoided:** >$90,000
-   **Immediate Project ROI:** **>4,500x** (based on a sub-$20 pipeline cost)

---

## 🛠️ The Strategic AI Architecture

Our solution is a serverless AI architecture built entirely within Google BigQuery, designed to transform raw data into a queryable intelligence asset without complex ETL.

![Architecture Diagram](https://raw.githubusercontent.com/veyselserifoglu/bq-ai-patent-analyst/main/doc/Patent%20Analysis%20Pipeline%20Architecture%20-%20PNG.png)

The four key technical stages are:

1.  **Direct-to-Query Ingestion (`Object Tables`):** A direct SQL interface is created over the raw PDF files in Cloud Storage, making them instantly queryable.
2.  **Structured Metadata Extraction (`ML.GENERATE_TEXT`):** A multimodal Gemini model performs initial metadata and diagram analysis to create a structured textual foundation.
3.  **Deep Knowledge Graph Generation (`AI.GENERATE_TABLE`):** A second, more complex prompt is used to parse the structured text and build a detailed, nested graph of all technical components and their relationships.
4.  **Context-Aware Vector Synthesis (`UDF` & `VECTOR_SEARCH`):** A dual-embedding strategy, combined with a custom SQL UDF for weighted vector averaging, provides a rich, context-aware signal to the `VECTOR_SEARCH` function for highly accurate results.

---

## ⚙️ Project Assets & Code

This project includes both the data processing pipeline and the interactive front-end.

### 1. The Data Pipeline
The data processing pipeline is detailed in the Jupyter Notebook. It contains the one-time setup for creating the BigQuery tables, models, and UDFs.

-   **Kaggle Notebook:** [https://www.kaggle.com/code/fissalalsharef/bigquery-ai-the-patent-analyst-project](https://www.kaggle.com/code/fissalalsharef/bigquery-ai-the-patent-analyst-project)

### 2. The Streamlit Application
The code for the interactive dashboard is contained in this repository.

**To Run Locally:**
```bash
# Clone the repository
git clone https://github.com/veyselserifoglu/bq-ai-patent-analyst.git
cd bq-ai-patent-analyst

# Create and activate a virtual environment & install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# For local development, ensure you have run 'gcloud auth application-default login'

# Run the app
bash start.sh