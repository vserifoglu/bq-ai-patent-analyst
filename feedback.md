# Feedback: Prompt Handling in ML.GENERATE_TEXT

During our project, we identified a specific limitation in how the `ML.GENERATE_TEXT` function handles prompts, which can make dynamic prompting less intuitive.

---

### The Limitation

The function provides two ways to specify a prompt:

1.  **Static Prompt:** As a hardcoded string literal inside the settings `STRUCT`.
2.  **Dynamic Prompt:** As a column named `prompt` in the input table.

The limitation is that the `STRUCT` method is inflexible. It **does not accept a subquery or a query parameter** for the `prompt` value. It must be a literal string.

This forces a specific pattern for dynamic prompts: you must always construct the prompt text in a subquery or a Common Table Expression (CTE) *before* feeding the data into the `ML.GENERATE_TEXT` function. While this works, it's less direct than being able to use a parameter, which is a common practice in other BigQuery functions.

This rigidity adds a layer of complexity that could be simplified for a smoother user experience.