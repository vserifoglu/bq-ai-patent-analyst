# AI Patent Analyst: Application Diagrams

This file contains the architectural and workflow diagrams for the "AI Patent Analyst 2.0" project.

---

## Workflow Overview

This diagram illustrates the end-to-end data flow, from ingesting raw patent PDFs to generating the final AI-powered analysis.

```mermaid
graph TD
    subgraph "Input Source"
        A[fa:fa-file-pdf Patent PDFs in Cloud Storage]
    end

    subgraph "Multimodal Pioneer"
        B["Text Extraction<br>(ML.GENERATE_TEXT)"]
        C["Diagram Analysis<br>(ML.GENERATE_TEXT)"]
    end

    subgraph "Semantic Detective"
        D["Create Multimodal Embeddings<br>(ML.GENERATE_EMBEDDING)"]
        E[fa:fa-user User Query] --> F{Vector Search}
        D --> F
    end

    subgraph "AI Architect"
        G["Generate Summaries/Tables<br>(AI.GENERATE_TABLE)"]
        F --> G
        G --> H[fa:fa-file-alt Analyst Report]
    end

    A --> B
    A --> C
    B --> D
    C --> D

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px
```
