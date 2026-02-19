# Capability Matching

- Goal: Create Capability Matching
- Challenge
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

## Known Challenges

- no explanation, hard to guess about these capabilities
- 3 tiers hierarchical structure labels can help better, but that's flattened into parent:child structure
- prompt context window restriction

## Potential Solution - Similarity Search

But how?

- input: embed full text?
- vdb: embed each capability name? or name with explanation?
- output: how do we deal with output selection?

---

## Step1: Explanation

This is an unavoidable requirement:

- LLM Generation
- LLM verification
- embedding -> vdb

## Step2: Input

Options:

- 1 - full webtext
- 2 - summary
- 3 - new generation

Solution:

- new prompt-template.md
- verify structure
- extract text

