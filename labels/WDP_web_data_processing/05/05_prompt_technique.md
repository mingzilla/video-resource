# Prompt Evolution for Small Models

## VersionS

- prompt_template__v1.md
- prompt_template__v2__solve_errors.md
- prompt_template__v3__solve_summaries.md
- prompt_template__v4__improve_summaries.md
- prompt_template__v5__impactful_info.md 

## Summary

| Rules                  | Bad                                         | Good                                                  | Impact                                                                |
|------------------------|---------------------------------------------|-------------------------------------------------------|-----------------------------------------------------------------------|
| Only use Supplied Text | not explicit about this rule                | "Use ONLY information explicitly in the text"         | Avoid LLM use own knowledge                                           |
| Avoid Examples         | "cybersecurity"                             | <placeholder>                                         | Avoid examples going into result - causing contamination              |
| Simple Structure       | (step1 format1, step2 format2) == bad       | 1 format                                              | Avoid reasoning complexity                                            |
| Consistent Length      | prompt + text                               | 1:text, 2:prompt                                      | Same length (prompt.length) closer to generation                      |
| Consistent Format      | summary, then labels                        | labels, then summary                                  | Consistent structure of summary based on labels                       |
| Categorise Label       | flat labels                                 | group by category                                     | Consistent and meaningful labels, which helps summary                 |
| Avoid disconnection    | Template + Rules - summary is 100% required | Template with Rules - (mandatory/optional)            | Closer to context, immediate influence, higher chance to have summary |
| Summary instructions   | 2-3 sentence factual summary                | A 500 tokens factual summary of what the company does | Explicit about token size, Be clear about WHAT summary                |
| Order of Influence     | trade name, then summary                    | summary, then trade name                              | If trade name is wrong, summary should not be impacted                |
