# Manufacturing Capability Extraction - Quality Evaluation

I have a system that extracts manufacturing capabilities from company web text.

## Files Provided

### 1. CSV File: Capability Definitions

Contains 361 manufacturing capability definitions in a **tree hierarchy** (Tier1 > Tier2 > Tier3).

**Important**: Only **leaf nodes** (the deepest/most specific tier) represent actual capabilities. Parent tiers are just category labels for context.

Example:

- `Machining > Milling > CNC Milling` → "CNC Milling" is the actual capability
- `Biotech > Fermentation` → "Fermentation" is the actual capability (no Tier3)

### 2. Markdown Files: Company Results

Each markdown file contains:

- **Company webtext**: Raw text scraped from company websites
- **Extracted capabilities**: Top 5 matched capabilities with rank (1=best match) and tier hierarchy

## Your Task

Evaluate whether the extracted capabilities (leaf nodes only) accurately reflect what each company does based on their webtext.

For each company, provide:

### Summary Table

| Company  | Rank 1 Capability (leaf node) | Correct? | Issue                        |
|----------|-------------------------------|----------|------------------------------|
| [Number] | [Full path to leaf]           | ✅/❌      | [Brief explanation if wrong] |

Example: `00012592 | Machining > Milling > CNC Milling | ✅ | -`

We just need such a table as the response. We don't need further explanation.