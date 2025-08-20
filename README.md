# The AI Patent Analyst: From Unstructured PDFs to a Queryable Knowledge Graph

## 1. High-Level Summary

This project demonstrates an end-to-end AI pipeline built entirely within Google BigQuery that transforms unstructured patent PDFs into a structured, queryable Knowledge Graph. The final prototype acts as a sophisticated IP analysis tool, enabling deep architectural analysis, component-level semantic search, all using BigQuery AI functions.

This solution directly addresses the challenge of making sense of messy, mixed-format data that is often overlooked, turning it into a powerful, interactive analytical asset.

## 2. Architecture Pipeline
![Patent Analysis Pipeline](https://github.com/veyselserifoglu/bq-ai-patent-analyst/blob/main/doc/Patent%20Analysis%20Pipeline%20Architecture%20-%20PNG.png?raw=true)

## 3. The Workflow: A Multi-Stage AI Pipeline

Our solution follows a three-stage process, showcasing a powerful combination of BigQuery's multimodal, generative, and vector search capabilities.

### Stage 1: Multimodal Data Processing (🖼️ Pioneer)
We use **Object Tables** to directly read and process raw PDFs from Cloud Storage. The Gemini model is then used with `ML.GENERATE_TEXT` to analyze the both the text and the technical diagrams within the PDFs.

### Stage 2: Generative Knowledge Graph Extraction (🧠 Architect)
The consolidated patent text is fed into the `AI.GENERATE_TABLE` function. A custom prompt instructs the AI to act as an expert analyst, extracting a structured table of high-level insights (`invention_domain`, `problem_solved`) and a detailed, nested graph of all technical components, their functions, and their interconnections.

### Stage 3: Component-Level Semantic Search (🕵️‍♀️ Detective)
To enable deep discovery, we build a novel search engine that understands context. We use `ML.GENERATE_EMBEDDING` to create two separate vectors:
1.  One for the patent's high-level context (title, abstract)
2.  Another for each component's specific function

These vectors are mathematically averaged into a single, final vector for each component via BigQuery's UDF (User-Defined Functions).

Finally, `VECTOR_SEARCH` is used on these combined vectors, creating a powerful search that returns highly relevant, context-aware results.

## 4. Key Features & Analytical Capabilities

The final `patent_knowledge_graph` table is not just a dataset; it's an interactive analysis engine that can answer questions which are more difficult and time consuming with the original text:

*   **Deep Architectural Analysis:** Use standard SQL with `UNNEST` and `GROUP BY` to discover the most common design patterns and component connections across hundreds of inventions.

*   **Component Search:** Go beyond patent-level search to find specific, functionally similar technical parts across different domains (e.g., "find a mechanism for encrypting data").


*   **Quantitative Portfolio Analysis:** Compare patent applicants by the complexity (average component count) and breadth (number of domains) of their innovations.


## 5. Dataset Overview
- **403 PDFs** (197 English, others in FR/DE) at `gs://gcs-public-data--labeled-patents/*.pdf`.
- **Tables**: `extracted_data` (metadata), `invention_types` (labels), `figures` (91 diagram coordinates).
- **Source**: [Labeled Patents](https://console.cloud.google.com/marketplace/product/global-patents/labeled-patents?inv=1&invt=Ab5j9A&project=bq-ai-patent-analyst&supportedpurview=organizationId,folder,project) (1TB/mo free tier).

## 6. Code
*   **Notebook:** [https://github.com/veyselserifoglu/bq-ai-patent-analyst/blob/main/notebooks/bigquery-ai-the-patent-analyst-project.ipynb](https://github.com/veyselserifoglu/bq-ai-patent-analyst/blob/main/notebooks/bigquery-ai-the-patent-analyst-project.ipynb)


## 7. Project Structure
```
.
├── LICENSE
├── README.md
├── doc
│   ├── Patent Analysis Pipeline Architecture - PNG.png
│   ├── Patent Analysis Pipeline Architecture - SVG.svg
│   └── diagrams.md
└── notebooks
    └── bigquery-ai-the-patent-analyst-project.ipynb
```
