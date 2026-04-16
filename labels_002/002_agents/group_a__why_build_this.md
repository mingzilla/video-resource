# A. Why Build This

- [1. Why split a working app]
- [2. Why Claude Code, not a raw API call]
- [3. Two-system split — create rules first, then QA]

---

## The Problem

Alex built something that works. A React artifact inside Claude.ai that
classifies companies. He ran 650 through it. It cost £15. The results
look good. So why are we here?

```text
Alex's artifact:

  +------------------------------------------+
  |  claude.ai (browser)                     |
  |                                          |
  |  +------------------------------------+  |
  |  | React artifact                     |  |
  |  |                                    |  |
  |  | [upload CSV] --> [Sonnet + tools]  |  |
  |  |                   web search       |  |
  |  |                   file I/O         |  |
  |  |                   batch logic      |  |
  |  |                       |            |  |
  |  |                       v            |  |
  |  |               [results table]      |  |
  |  +------------------------------------+  |
  |                                          |
  +------------------------------------------+

  Works for 650 companies. Then:
    - Hit API rate limits at company 650
    - Can't run headless (needs browser)
    - Can't share with George/Sam
    - Can't run overnight
    - One user at a time
```

---

## Decision 1: Why split a working app

> You thought: scale the working artifact.
> But actually: the artifact was the bottleneck — prompts good, delivery bad.

```text
WHAT'S GOOD:                    WHAT'S THE BOTTLENECK:

  +------------------+            +---------------------------+
  | Prompts          |            | Delivery mechanism        |
  |                  |            |                           |
  | - P1 classifier  |            | - Runs in browser only    |
  | - P2 gen rules   |            | - One user at a time      |
  | - P3 rule gen    |            | - Rate limited at 650     |
  | - taxonomy       |            | - No headless mode        |
  |                  |            | - No resume after crash   |
  | KEEP THESE       |            | REPLACE THIS              |
  +------------------+            +---------------------------+

  Prompts -----> extract -----> new backend
  Artifact ----> discard
```

- **Q:** Alex had a working artifact. Why not just scale it?
- **Options:** (a) scale the artifact directly, (b) take it apart and rebuild
- **Chose:** take it apart — extract prompts, build a backend service
- **Why:** the artifact couldn't scale, couldn't run headless, couldn't be shared. The prompts were the value. The React/browser delivery was the constraint.
- **Cascade:** forced us to understand what the artifact did vs what claude.ai provided for free (web search, file I/O)

---

## Decision 2: Why Claude Code, not a raw API call

> You thought: call the Anthropic API directly.
> But actually: you need agentic tools — web search, file I/O, command execution.

```text
RAW API (what Alex's HTML test pages do):

  Python --> POST api.anthropic.com/v1/messages
                 |
                 v
              Sonnet
              (text in, text out)

              Can it search the web?     NO
              Can it read files?         NO
              Can it check Companies House?  NO
              Can it visit websites?     NO


CLAUDE CODE (what we chose):

  Python --> claude -p "..."
                 |
                 v
              Claude Code
              (Sonnet + tools)

              Web search?          YES (built in)
              Read/write files?    YES (built in)
              Run commands?        YES (built in)
              Visit websites?      YES (built in)


The QA task:
  For each company:
    1. Search company name + URL
    2. Visit homepage
    3. Check /about, /products
    4. Check Crunchbase/LinkedIn/Companies House
    5. Classify based on evidence

  This is agentic work. Raw API can't do it.
```

- **Q:** why not call the Anthropic API directly like Alex's HTML test pages?
- **Options:** (a) direct API calls, (b) Claude Code CLI
- **Chose:** Claude Code — wraps Sonnet with tools (web search, file I/O, commands)
- **Why:** QA requires researching each company's website. Raw Sonnet can't browse. Without Claude Code, we'd build a web scraping pipeline ourselves.
- **Constraint:** Claude Code is a CLI tool invoked as a subprocess. Requires subscription or API key.

---

## Decision 3: Two-system split

> You thought: one prompt does everything.
> But actually: system 1 generates rules, system 2 audits — different jobs, different prompts.

```text
ONE PROMPT (rejected):

  taxonomy + companies --> [one big prompt] --> results
                            |
                            contains:
                            - how to generate rules
                            - the rules themselves
                            - how to classify
                            - how to output

  Problem: changes to FinRegTech rules
  affect Defence rules. Everything tangled.


TWO SYSTEMS (chosen):

  System 1 (once per RTIC):

    taxonomy --------+
    general rules ---+---> CLAUDE ---> specific_rules.md
    P3 (instructions)+

  System 2 (per batch of companies):

    companies.csv --------+
    taxonomy -------------+
    general rules --------+---> CLAUDE ---> results.csv
    specific_rules.md ----+
    P1 (instructions) ----+

  System 1 output ---> System 2 input
                 (specific_rules.md)

  Change FinRegTech? Rerun system 1 for FinRegTech only.
  Defence rules untouched.
```

- **Q:** how should the prompt pipeline work?
- **Options:** (a) one combined prompt, (b) two-step: generate rules, then classify
- **Chose:** two systems — system 1 output becomes system 2 input
- **Why:** rules change per RTIC vertical. P1 and P2 stay the same. Only specific rules change. Alex refines the general system while domain experts produce vertical-specific rules.
- **Cascade:** Alex kept confusing which file was which — needed the input/output mapping table to make the split clear
