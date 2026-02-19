## Pipeline Step 2 - Text Gen

```text
+-------------------+               +-------------------+               +-------------------+            +----------------------+
| 30k chars webtext | -[cleaning]-> | 15k chars webtext | -[gemma3.2]-> | 2k tokens summary | -[nomic]-> | full content vectors |
+-------------------+    | (1)      +-------------------+     | (2)     +-------------------+     | (3)  +----------------------+
         |               |- ~ 15hours         |               |- 3b 8k context                    |- 8k context - 8k ~= 4days
         |                                    |               |                                   |
 Archive_MonthYear.parquet            ~ 4k tokens     5k input, 2k output                      2k input
```

## Potential Prompt Template with Anti-Hallucination

```text
EXTRACT COMPANY INFORMATION FROM WEBSITE TEXT

RULES:
- Use ONLY information explicitly in the text below
- Do not add, infer, or guess anything
- If a category doesn't apply, skip it

TASK:
1. Extract 15-20 total labels across these categories:
 - industries: primary/secondary industries
 - activities: daily operations
 - products: specific products/services
 - markets: customer segments served
 - regions: geographic operations
 - model: B2B, B2C, SaaS, etc.
 - competencies: specialized skills/advantages

2. Write factual summary (max 500 tokens) from text only.

FORMAT:
industries: software, cybersecurity
activities: threat_monitoring, incident_response
products: firewall_system, intrusion_detection
markets: banks, government_agencies
regions: UK, Europe
model: B2B
competencies: real_time_analytics
SUMMARY: [factual summary here]

WEBSITE CONTENT:
{cleaned_webtext}

EXTRACT:
```

## Model Configuration Recommendations:

```text
# Example configuration for your LLM call:
generation_config = {
    "temperature": 0.0,
    "top_p": 0.95,  # Keep this narrow
    "top_k": 1,     # Most conservative - always pick highest probability token
    "max_tokens": 1000,  # Enough for labels + 500-token summary
    "do_sample": False,  # Disable sampling for deterministic output
    "repetition_penalty": 1.1,  # Mild penalty to avoid loops
}
```