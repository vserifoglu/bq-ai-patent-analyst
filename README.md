# The AI Patent Analyst

This project demonstrates a novel, end-to-end AI pipeline built entirely within Google BigQuery. It transforms a complex dataset of unstructured patent PDFs into a structured, queryable **Knowledge Graph**, unlocking deep architectural insights that are impossible with traditional data processing methods.

---
## 1. The Problem: Unlocking Trapped Value

Patent documents contain immense technical value, but this information is locked away in dense prose and complex diagrams. Finding specific design patterns, common component relationships, or performing quantitative analysis across thousands of patents requires immense manual effort, making it impractical at scale. This project tackles the challenge of processing this messy, mixed-format data to make it useful and queryable.

---
## 2. The Solution: A Generative Knowledge Graph

This project's core innovation is the creation of a **Generative Knowledge Graph**. Instead of just summarizing text, we use BigQuery's AI capabilities to read, understand, and structure the patent data automatically. The pipeline ingests raw PDFs and outputs a rich, structured table where each patent is represented as a "knowledge graph" of its components, their functions, and their interconnections.

This turns a corpus of opaque documents into a powerful analytical asset where complex questions about invention architecture can be answered with standard SQL.

---
## 3. End-to-End Workflow in BigQuery

The entire process is orchestrated within BigQuery, treating AI as a native extension of SQL.

* **Step 1: Multimodal Data Ingestion**
    * **Action:** Raw PDF files from Google Cloud Storage are mapped directly into BigQuery using an **`Object Table`**.
    * **BigQuery Feature:** This creates a structured SQL interface over unstructured files without moving or duplicating data.

* **Step 2: AI-Powered Diagram & Text Analysis**
    * **Action:** Google's Gemini model analyzes both the text and the technical diagrams within each PDF to generate rich, text-based descriptions.
    * **BigQuery Feature:** **`ML.GENERATE_TEXT`** is used to understand and describe the visual components, enriching the dataset.

* **Step 3: Knowledge Graph Extraction**
    * **Action:** The consolidated text is fed into the **`AI.GENERATE_TABLE`** function with a custom prompt. The AI extracts high-level fields (like `invention_domain`) and a detailed, **nested table** of all technical components, their functions, and their connections.
    * **BigQuery Feature:** This showcases using Generative AI for advanced, structured data extraction at scale, directly within the data warehouse.

---
## 4. Dataset & Technical Stack

* **Dataset:** The public **"Patent PDF Samples with Extracted Structured Data"** (`gs://gcs-public-data--labeled-patents/`).
* **Core Technologies:**
    * Google BigQuery
    * Cloud Storage
    * BigQuery AI Functions: `Object Tables`, `ML.GENERATE_TEXT`, `AI.GENERATE_TABLE`
    * AI Model: `gemini-2.5-flash`