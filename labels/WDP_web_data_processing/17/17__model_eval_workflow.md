# Model Evaluation Workflow

## Table of Contents

- [Overview](#overview)
- [Tool Setup](#tool-setup)
- [6-Step Evaluation Process](#6-step-evaluation-process)
- [INCLUDE_WEBTEXT Toggle](#include_webtext-toggle)

---

## Overview

```text
[test data]
    |
    +-- [extract labels] --> [quality check]
    |
    +-- [vss match] --> [rank] --> [evaluate]
```

- Reusable workflow for evaluating any new model before production
- Uses `tool001__model_eval` to generate markdown output for manual review
- Different from WDP/12 (quality vs speed comparison) — this is the evaluation procedure

---

## Tool Setup

```text
1. Update config
   work/__pipelines/tool001__model_eval/001__generate_summaries/show_summary__config.json

2. Run extract script
   work/__pipelines/tool001__model_eval/_output__md__extract.sh <CompanyNumber> ...

3. Review output
   work/__pipelines/tool001__model_eval/_output_md/
```

| Config field                | Purpose                 |
|-----------------------------|-------------------------|
| `llm_model`                 | Model under evaluation  |
| `text_max_chars_to_be_used` | Input size (e.g. 16000) |
| `llm_max_tokens`            | Output token limit      |
| `use_one_user_message`      | Prompt format           |

### Example

```text
prompt__007__qwen2dot5_32b__prompt_v2
|-- 00047169.md
|-- 00075176.md
|-- 00112453.md
|-- ...
```

---

## 6-Step Evaluation Process

```text
[1] test data     -- select sample records targeting capabilities vss
    |
[2] extract       -- run tool001 with model under test, get labels
    |
[3] quality       -- LLM: verify accuracy of extracted labels vs webtext
    |
[4] vss           -- vector search: ranked related capabilities
    |
[5] rank          -- LLM: evaluate ranked capability results
    |
[6] other fields  -- LLM: evaluate remaining fields (industries, activities, etc.)
```

- Use 10 representative company records as test data
- Same test records across all models for fair comparison
- Manual review of `_output_md/` at each step

---

## INCLUDE_WEBTEXT Toggle

| Value   | When to use                                   |
|---------|-----------------------------------------------|
| `true`  | Webtext not yet supplied to model (e.g. Kimi) |
| `false` | Webtext already in model context              |

```text
INCLUDE_WEBTEXT=true  --> output includes webtext + summary
INCLUDE_WEBTEXT=false --> output includes summary only
```
