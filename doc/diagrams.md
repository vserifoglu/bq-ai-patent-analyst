# AI Patent Analyst: Application Diagrams

This file contains the architectural and workflow diagrams for the "AI Patent Analyst 2.0" project.

---

## Workflow Overview

This diagram illustrates the end-to-end data flow, from ingesting raw patent PDFs to generating the final AI-powered analysis.

```mermaid
flowchart TD
    %% --- LEGEND --- 
    subgraph Legend [Color Legend]
        direction LR
        L_GPT[GPT/GenAI Function]:::ai-function
        L_Data[Data Storage]:::data-storage
        L_Process[Processing Logic]:::processing-logic
        L_Result[Results & Output]:::results-output
        L_Input[User Input]:::user-input
    end

    %% --- MAIN PIPELINE ---
    subgraph SG1 [ ]
        title1[1- Data Ingestion]
        A[fa:fa-google GCS Bucket: Raw PDFs] -->|Creates SQL Interface via<br><strong>Object Table</strong>| B[BQ: patent_documents_object_table]
    end

    subgraph SG2 [ ]
        title2[2- Multimodal Extraction]
        B -->|Processes PDFs| C[<strong>ML.GENERATE_TEXT</strong><br><em>Gemini Model</em>]
        C -->|Extracts PDFs' Text & Diagrams Description | D[BQ: ai_text_extraction]
    end

    subgraph SG3 [ ]
        title3[3- Knowledge Graph Generation]
        D -->|Feeds Consolidated Text| E[<strong>AI.GENERATE_TABLE</strong><br><em>Gemini Model</em>]
        E -->|Outputs Nested 
              Technical Components| F[BQ: patent_knowledge_graph]
        
        F -->|UNNEST| G[BQ: patent_components_flat]
    end

    %% --- PARALLEL PATHS ---
    subgraph SG5 [5- Embedding Generation]
        G --> H[<strong>ML.GENERATE_EMBEDDING</strong>]
        H --> I[BQ: component_function_embeddings]
        D --> L[<strong>ML.GENERATE_EMBEDDING</strong>]
        L --> M[BQ: patent_context_embeddings]
    end

    subgraph SG6 [6- Semantic Search Construction]
        M --> N[<strong>Custom UDF</strong><br>Combines & averages Vectors]
        I --> N
        N --> O[BQ: component_search_index]
    end

    %% These two subgraphs are forced to the same level at the bottom
    subgraph SG4 [4- Analytical Applications]
        G --> J[SQL Queries<br><em>GROUP BY, AVG, etc.</em>]
        J --> K[fa:fa-chart-bar Quantitative Insights]
    end

    subgraph SG7 [7- Semantic Search Usage]
        P[User Query] --> Q[<strong>VECTOR_SEARCH</strong>]
        O --> Q
        Q --> R[fa:fa-search Search Results]
    end

    %% Invisible link to align the outputs horizontally
    K ~~~ R
    
    %% -- STYLING DEFINITIONS -- 
    
    classDef ai-function fill:#d47461,stroke:#a85a4b,stroke-width:2px,color:#fff
    classDef data-storage fill:#4a7bd0,stroke:#2a4b8d,stroke-width:2px,color:#fff
    classDef processing-logic fill:#6c9d7f,stroke:#436953,stroke-width:2px,color:#fff
    classDef results-output fill:#e6b87a,stroke:#b3874f,stroke-width:2px,color:#333
    classDef user-input fill:#95a3b9,stroke:#6c7991,stroke-width:2px,color:#fff
    classDef legend-box fill:#fafafa,stroke:#ddd,stroke-width:2px,color:#333

    %% Apply classes to Main Pipeline Nodes
    style A fill:#4a7bd0,stroke:#2a4b8d,stroke-width:2px,color:#fff
    style B fill:#4a7bd0,stroke:#2a4b8d,stroke-width:2px,color:#fff
    style D fill:#4a7bd0,stroke:#2a4b8d,stroke-width:2px,color:#fff
    style F fill:#4a7bd0,stroke:#2a4b8d,stroke-width:2px,color:#fff
    style I fill:#4a7bd0,stroke:#2a4b8d,stroke-width:2px,color:#fff
    style M fill:#4a7bd0,stroke:#2a4b8d,stroke-width:2px,color:#fff
    style O fill:#4a7bd0,stroke:#2a4b8d,stroke-width:2px,color:#fff
    style G fill:#4a7bd0,stroke:#2a4b8d,stroke-width:2px,color:#fff

    style C fill:#d47461,stroke:#a85a4b,stroke-width:2px,color:#fff
    style E fill:#d47461,stroke:#a85a4b,stroke-width:2px,color:#fff
    style H fill:#d47461,stroke:#a85a4b,stroke-width:2px,color:#fff
    style L fill:#d47461,stroke:#a85a4b,stroke-width:2px,color:#fff
    style Q fill:#d47461,stroke:#a85a4b,stroke-width:2px,color:#fff

    style N fill:#6c9d7f,stroke:#436953,stroke-width:2px,color:#fff

    style K fill:#e6b87a,stroke:#b3874f,stroke-width:2px,color:#333
    style R fill:#e6b87a,stroke:#b3874f,stroke-width:2px,color:#333

    style P fill:#95a3b9,stroke:#6c7991,stroke-width:2px,color:#fff

    %% Style for Titles and Legend
    style title1 fill:#f9f9f9,stroke:none,color:#2d2d2d
    style title2 fill:#f9f9f9,stroke:none,color:#2d2d2d
    style title3 fill:#f9f9f9,stroke:none,color:#2d2d2d
    style Legend fill:#fafafa,stroke:#ddd,stroke-width:2px,color:#333

    %% Style subgraphs for better visual separation
    classDef default fill:#f8f9fc,stroke:#dde1eb,stroke-width:1px;
    class SG1,SG2,SG3,SG4,SG5,SG6,SG7 default;
```
