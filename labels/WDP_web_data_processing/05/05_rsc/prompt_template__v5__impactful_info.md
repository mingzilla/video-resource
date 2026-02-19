## Prompt V5 - Additional Imparctful Info

Let's add `COMPANY_TRADING_NAME`, but where do we put it?

- Beginning?
- Before Summary?
- After Summary?

### Before Summary

```text
Extract company information from the website content provided above in British English.

OUTPUT FORMAT - Start immediately with the first category:

INDUSTRIES: (optional) <comma-separated list>
ACTIVITIES: (optional) <comma-separated list>
PRODUCTS: (optional) <comma-separated list>
MARKETS: (optional) <comma-separated list>
REGIONS: (optional) <comma-separated list>
MODEL: (optional) <B2B or B2C or B2B2C or SaaS or marketplace or other>
COMPANY_TRADING_NAME: (mandatory) <comma-separated list>
COMPANY_SUMMARY: (mandatory) <A 500 tokens factual summary of what the company does>

RULES:
- Use ONLY explicit information from the website content above
- Do not add, infer, or guess anything not stated
- Skip any category with no information
- No preamble, no introduction, no explanations
- Start output immediately with first category
- COMPANY_TRADING_NAME is required and return at most 3 names
- COMPANY_SUMMARY is 100% required
```

### After Summary

```text
Extract company information from the website content provided above in British English.

OUTPUT FORMAT - Start immediately with the first category:

INDUSTRIES: (optional) <comma-separated list>
ACTIVITIES: (optional) <comma-separated list>
PRODUCTS: (optional) <comma-separated list>
MARKETS: (optional) <comma-separated list>
REGIONS: (optional) <comma-separated list>
MODEL: (optional) <B2B or B2C or B2B2C or SaaS or marketplace or other>
COMPANY_SUMMARY: (mandatory) <A 500 tokens factual summary of what the company does>
COMPANY_TRADING_NAME: (mandatory) <comma-separated list>

RULES:
- Use ONLY explicit information from the website content above
- Do not add, infer, or guess anything not stated
- Skip any category with no information
- No preamble, no introduction, no explanations
- Start output immediately with first category
- COMPANY_SUMMARY is 100% required
- COMPANY_TRADING_NAME is required and return at most 3 names
```

