## Prompt V3 - Solve Missing Summaries

- remove the line break between MODEL and DESCRIPTION
- change DESCRIPTION to FULL_SUMMARY_DESCRIPTION (just in case that it treats description as another category label)
- add a rule `- FULL_SUMMARY_DESCRIPTION is 100% required` - note: this is not good enough
- add (optional) and (mandatory) to directly instruct a category - note: this solves problems

```text
Extract company information from the website content provided above.

OUTPUT FORMAT - Start immediately with the first category:

INDUSTRIES: (optional) <comma-separated list>
ACTIVITIES: (optional) <comma-separated list>
PRODUCTS: (optional) <comma-separated list>
MARKETS: (optional) <comma-separated list>
REGIONS: (optional) <comma-separated list>
MODEL: (optional) <B2B or B2C or B2B2C or SaaS or marketplace or other>
FULL_SUMMARY_DESCRIPTION: (mandatory) <2-3 sentence factual summary of what the company does>

RULES:
- Use ONLY explicit information from the website content above
- Do not add, infer, or guess anything not stated
- Skip any category with no information
- No preamble, no introduction, no explanations
- Start output immediately with first category
- FULL_SUMMARY_DESCRIPTION is 100% required

```

### Remaining Problems

- No description generated - e.g. 2%
- `FULL SUMMARY DESCRIPTION`, `FULL_SUMMARY DESCRIPTION`

### Examples

```text
INDUSTRIES: e-commerce, consulting, creative services, digital nomads, online sellers

ACTIVITIES: company formation, remote management, accounting, tax reporting, payroll administration

PRODUCTS: e-Residency Hub, multi-currency bank account, online tools, personal accountant, web-based accounting platform, debit card

MARKETS: EU, global (specifically mentioned countries include Estonia, Switzerland, Germany, Greece)

REGIONS: Europe, worldwide (with a focus on remote work and digital nomads)

MODEL: B2B

FULL SUMMARY DESCRIPTION:
E-Residency Hub is an online platform that provides fast and easy company formation services for individuals and businesses in the EU. It offers a range of tools and services, including accounting, tax reporting, and payroll administration, to support entrepreneurs and remote workers in setting up and running their companies from anywhere in the world.
```

```text
INDUSTRIES: gaming
ACTIVITIES: 
PRODUCTS: 
MARKETS: 
REGIONS: 
MODEL: B2B
FULL SUMMARY DESCRIPTION: Sherlock Games focuses on solving complex cases through detailed analysis. The company's expertise lies in tackling intricate problems.
```

```text
INDUSTRIES: book-keeping, accountancy, payroll, tax

ACTIVITIES: financial management, budgeting, forecasting, cash flow management, accounting system setup, debtors and creditors management, VAT registration and submissions, credit control, payroll management, HR advice

PRODUCTS: book-keeping services, accountancy services, payroll services, VAT services, self-assessment services

MARKETS: local businesses, individuals

REGIONS: Walton-on-Thames, UK

MODEL: B2B

FULL_SUMMARY DESCRIPTION: JIS Systems Ltd offers comprehensive book-keeping and accountancy services tailored to individual business needs. They provide flexible solutions for financial and operational requirements, ensuring businesses have a reliable partner for managing their finances.
```