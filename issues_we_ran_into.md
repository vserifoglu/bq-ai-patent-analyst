# Appendix: Building a Resilient Extraction Pipeline

During the initial data extraction from all 403 PDFs, we observed that a small subset of records failed to process correctly. This is a common, real-world challenge when working with large-scale AI models.

---

### The Problem: Two Types of Failures

Our analysis showed two types of errors:
1.  **Rate Limiting**: A few requests to the AI model were rejected due to high traffic, resulting in a completely `null` output.
2.  **Token Limits**: For some complex patents, the AI's JSON response was longer than the default output limit, causing the JSON to be cut off and un-parsable.

---

### The Solution: A Targeted "Fix-Up" Query

To ensure a 100% complete and accurate dataset, we implemented a second "fix-up" query.

This query intelligently targets **only the failed rows** from the first run. It then re-sends these documents to the AI model with an **increased `max_output_tokens` limit**.

This two-step process (a main run followed by a targeted fix-up run) is a robust and efficient strategy. It allows us to leverage the speed of parallel processing on the main dataset while guaranteeing the quality and completeness of the final result by correcting for common API-related failures.