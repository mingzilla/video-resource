# Capability Matching

- Goal: Create Capability Matching
- Potential Solution
- Step1: Simplify JSON
- Step2: Test
- Step3: Analyse

## Goal: Create Capability Matching

Inputs:

- capabilities.json
- prompt.md

Expectation:

| CompanyNumber | Capabilities                           |
|---------------|----------------------------------------|
| 001           | Oxyfuel gas, Surface Preparation, ...  |
| 002           | Electron beam welding, Flattening, ... |

## Potential Solution

Example Template:

```text
{webtext}

Analyse the company's manufacturing capabilities from the website content above.

CAPABILITIES REFERENCE (use for matching):
{capabilities.json}

TASK:
Extract ALL manufacturing capabilities that match or relate to the CAPABILITIES REFERENCE above.

OUTPUT FORMAT - Start immediately with:

CAPABILITIES: <comma-separated list of at most 10 matched capabilities>

RULES:
- Use ONLY capabilities explicitly mentioned or clearly implied in the website content
- Match terms to the CAPABILITIES REFERENCE list above
- Include only the capability NAMES (right side of colons in reference)
- If no clear matches, return: CAPABILITIES: None
- No explanations, no preamble, no categories
- Start output immediately with "CAPABILITIES:"
```

```text
8k Context:
[text] - ? - need 16k chars ~= 4k tokens
[capabilities] - ?
[prompt] - 500 tokens
[output] - 100 tokens
```

---

## Step1: Simplify JSON

```text
Current Structure
|
|- Tier1
|  |
|  |- Tier2
|  |  +- Tier3 (leaf)
|  |
|  +- Tier2 (leaf)
|
+- Tier1


Problem:
- complex structure: may have 2 tiers, may have 3 tiers
- context: cannot use tier3 only
- no explanation
- context window: text too long
```

Proposal:

```text
parent: child1, child2, ...
```

Outcome:

- Script Generation
- example_prompt.md

---

## Step2: Test

- 1st Attempt: It does not work if using llama3.2:3b
- 2nd Attempt: How about other models? - Go with best models

### Plan

- Initial Test: Deepseek generates good result
- Plan:

```text
Have:
- deepseek generated result
- model generated result

Compare:
- deepseek generated result against summary to get an idea if we can trust deepseek, if unsure, consult the raw webtext
- compare deepseek and our models if we can trust deepseek
```

### Try different models - generate 200 rows - start from big model

| model                | process | count    |
|----------------------|---------|----------|
| deepseek             | manual  | 10 rows  |
| llama3.2:3b          | duckdb  | 300 rows |
| qwen2.5:14b-instruct | duckdb  | 300 rows |
| qwen2.5:32b          | duckdb  | 300 rows |

```text
CAPABILITIES: Digital prototyping, Process workflow design, Data analytics, In-process inspection technologies, Measurement Management Systems, Mechanical testing, Metrology, Non Destructive testing, Surface metrology, Temperature measurement and monitoring
CAPABILITIES: Digital prototyping, Process workflow design, Software design, Data analytics, Industrial IoT, Standards and policies related to digital engineering
CAPABILITIES: None
```

### Result

After verification, even Deepseek has bad results

---

## Step3: Analyse

Challenges:

- no explanation, hard to guess about these capabilities
- 3 tiers hierarchical structure labels can help better, but that's flattened into parent:child structure
- prompt context window restriction

Potential Solutions:

- Similarity Search
- Fine Tune Small Model