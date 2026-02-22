Extract company information from the website content provided above in British English.

OUTPUT FORMAT - Start immediately with the first category:

INDUSTRIES: (optional - comma-separated list of sectors as nouns)
ACTIVITIES: (optional - comma-separated list of business activities: what the company does commercially for customers)
PRODUCTS: (optional - comma-separated list of physical or digital goods offered)
SERVICES: (optional - comma-separated list of intangible services offered)
MARKETS: (optional - comma-separated list of customer types or buyer segments they sell to)
REGIONS: (optional - countries or continents level about where customers are located)
MODEL: (optional - B2B/B2C/B2B2C/SaaS/marketplace/other)
COMPANY_SUMMARY: (required - 500 token factual summary of what the company does)
COMPANY_TRADING_NAME: (required - comma-separated list, max 3 names)
IS_MANUFACTURING: (required - true if website specifically mentions goods production, reselling should be false)
MANUFACTURING_PROCESSES: (optional - Comma-separated process names ONLY. NO descriptions, NO explanations. 50-100 tokens max.)
TECHNICAL_CAPABILITIES: (optional - Named technologies, certifications, proprietary methods. NO equipment model numbers, NO dimensional specs, NO quantities. 50-100 tokens max.)

RULES:
- Use ONLY explicit information from the website content above
- Do not add, infer, or guess anything not stated
- Skip any category with no information
- No preamble, no introduction, no explanations
- Start output immediately with first category
- COMPANY_SUMMARY is 100% required
- COMPANY_TRADING_NAME is required and return at most 3 names
- For MANUFACTURING_PROCESSES and TECHNICAL_CAPABILITIES: Use standard terminology and avoid listing duplicate or synonymous terms
