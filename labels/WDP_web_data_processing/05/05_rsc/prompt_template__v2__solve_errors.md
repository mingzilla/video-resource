## Prompt V2 - Solve Errors

```text
Extract company information from the website content provided above.

OUTPUT FORMAT - Start immediately with the first category:

INDUSTRIES: <comma-separated list>
ACTIVITIES: <comma-separated list>
PRODUCTS: <comma-separated list>
MARKETS: <comma-separated list>
REGIONS: <comma-separated list>
MODEL: <B2B or B2C or B2B2C or SaaS or marketplace or other>

DESCRIPTION: <2-3 sentence factual summary of what the company does>

RULES:
- Use ONLY explicit information from the website content above
- Do not add, infer, or guess anything not stated
- Skip any category with no information
- No preamble, no introduction, no explanations
- Start output immediately with first category
```

### Previous Problems and Solution

| Problem                           | Solution                                                    |
|-----------------------------------|-------------------------------------------------------------|
| Always have prefix                | `OUTPUT FORMAT - Start immediately with the first category` |
| Labels not consistent             | Simple Consistent Structure                                 |
| Data Contamination                | No EXAMPLES! Use `<comma-separated list>`                   |

### Enhancement

| Enhancement         | Solution                                                                         |
|---------------------|----------------------------------------------------------------------------------|
| Simplify structure  | Critical for small models                                                        |
| `{cleaned_webtext}` | Use 2 User messages, put webtext as 1st message, consistent structure and length |

### Remaining Problems

- No description generated - e.g. 80%

## Example

```text
INDUSTRIES: digital marketing, online marketing
ACTIVITIES: campaign management, AI integration, data analysis, content creation, lead generation
PRODUCTS: not explicitly stated
MARKETS: not explicitly stated
REGIONS: United Kingdom (referenced by country code "+44")
MODEL: B2B
```