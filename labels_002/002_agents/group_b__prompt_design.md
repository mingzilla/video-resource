# B. Prompt Design

- [4. Persona vs intention framing]
- [5. Earn your generalisations — don't extract from 1 example]
- [6. File-based prompt passing — paths not inline content]

---

## The Problem

Alex spent days in a Claude session refining prompts. He came back with
3 prompt files, a combined file, HTML test pages, and a session summary.
The prompts scored 56-59 out of 60. But the scores were given by the
Claude session that wrote them.

How do you take someone else's prompt work, verify it makes sense, and
make it fit a scalable backend?

```text
What Alex delivered:

  prompt_1_qa_classifier_v3.2.md        <-- 371 lines
  prompt_2_general_rules_layer_v3.2.md  <-- 134 lines
  prompt_3_rtic_rules_generator_v3.2.md <-- 134 lines
  rtic_qa_prompts_v3.2.md               <-- all 3 combined (662 lines)
  session_summary.md                    <-- decisions and scores
  emerging_domains_run.html             <-- browser test
  prompt3_real_test.html                <-- browser test

  Questions:
  - Which file does what?
  - Are the scores trustworthy?
  - What needs to change for a backend?
  - What's the persona section actually doing?
```

---

## Decision 4: Persona vs intention framing

> You thought: "You are a senior analyst who..."
> But actually: state what the thing IS — intention beats roleplay.

```text
PERSONA (Alex's P3 section 8):

  "You are a senior FinRegTech analyst with deep
   knowledge of compliance software markets. Your
   classifications will be used by TDC's data team
   to identify false positives before RTIC publication.
   The primary failure mode is confusing regulated
   fintechs with RegTech vendors."


What it's actually doing:

  +------------------------------------------+
  | "senior FinRegTech analyst with deep     |  --> CONTEXT
  |  knowledge of compliance software"       |      what the RTIC is about
  +------------------------------------------+
  | "classifications used by TDC's data      |  --> INTENTION
  |  team to identify false positives"       |      why accuracy matters
  +------------------------------------------+
  | "primary failure mode is confusing       |  --> GUARDRAIL
  |  regulated fintechs with RegTech"        |      what not to get wrong
  +------------------------------------------+

  Three different things wrapped in roleplay.


INTENTION (chosen):

  "This RTIC covers compliance software sold to
   financial institutions. Results are used to identify
   false positives before publication — a false positive
   inflates sector headcount and has caused lost deals.
   The most common mistake: classifying a regulated
   fintech as a RegTech vendor."

  Same information. No pretending to be someone.
  Clearer. More verifiable.
```

- **Q:** should the system use roleplay framing ("you are an analyst")?
- **Options:** (a) persona framing, (b) intention framing — state what the thing IS
- **Chose:** intention — context, intention, and guardrail stated directly
- **Why:** the persona mixed three concerns. Separating them is clearer and verifiable. "You are an analyst" adds nothing that "this RTIC covers X" doesn't.
- **Cascade:** specific rules file structure changed — no persona section, content folded into context/intention/guardrail fields

---

## Decision 5: Earn your generalisations

> You thought: generalise from one RTIC example.
> But actually: Claude graded its own homework. Do 10 first, then extract the pattern.

```text
WHAT ALEX DID:

  1 RTIC (FinRegTech)
       |
       v
  Claude session
  "make it generic!"
       |
       v
  P2 "general rules"     scored 56/60
  P3 "rule generator"    scored 57/60

  Who scored it? The same Claude session that wrote it.


THE RISK:

  FinRegTech rules:
    R1: Primary activity test          <-- genuinely general
    R2: Regulated != provider          <-- genuinely general
    R3: Corporate group handling       <-- genuinely general
    R4: Website mismatch               <-- genuinely general
    ...
    R9: Evidence requirements          <-- genuinely general

  After 10 RTICs:
    R10: ???                           <-- unknown
    R11: ???                           <-- unknown
    R12: ???                           <-- unknown

  The rules aren't wrong.
  They're incomplete.
  You can't know what's missing from 1 example.


WHAT WE CHOSE:

  Step 1: Use current P2 as-is           (it's a good start)
  Step 2: Do 10 RTICs manually           (Defence, ESG, Tax, ...)
  Step 3: Extract common patterns        (now you've earned it)
  Step 4: THEN formalise the split       (general vs specific)

  Until step 3, system 2 combines general + specific in one pass.
```

- **Q:** Alex derived general rules from one RTIC. Valid?
- **Options:** (a) accept as-is, (b) require 10+ RTICs first
- **Chose:** use P2 as starting point, acknowledge it's incomplete. Real general rules emerge after 10 RTICs.
- **Why:** Claude graded its own homework. Rules aren't wrong but derived from one example. Rules 10-12 will emerge from verticals nobody anticipated.
- **Cascade:** system 2 combines general + specific for now. Formal split comes later.

---

## Decision 6: File-based prompt passing

> You thought: inline everything in the -p argument.
> But actually: 40k chars. Write files, pass paths. 500 chars regardless of input size.

```text
INLINE (original code):

  claude -p "You are a company classification tool.

  ## Instructions
  [371 lines of P1]

  ## Taxonomy
  [34 lines of taxonomy]

  ## Classification Rules
  [134 lines of P2]

  ## Companies to Classify
  Companynumber,Companyname,Website
  09688671,SUM AND SUBSTANCE LTD,sumsub.com
  11689731,CRASSULA LTD,crassula.io
  ...40 more rows...

  ## Output
  Write the result CSV to: /path/to/output.csv"

  Total: ~40,000 characters in one -p argument


FILE-BASED (chosen):

  1. Write files to disk:
     input/prompt.md           <-- P1
     input/rules.md            <-- P2
     input/taxonomy.md
     input/specific_rules.md
     input/companies.csv

  2. Pass a short instruction:

  claude -p "Read these files:
  - /app/runs/.../input/prompt.md
  - /app/runs/.../input/rules.md
  - /app/runs/.../input/taxonomy.md
  - /app/runs/.../input/specific_rules.md
  - /app/runs/.../batch_001/companies_slice.csv

  Follow the instructions in the prompt file.
  Write output to: /app/runs/.../batch_001/result.csv"

  Total: ~500 characters. Always.
  Regardless of prompt size, taxonomy size, or company count.
```

- **Q:** the code inlined everything into one `-p` argument. 40k+ chars.
- **Options:** (a) keep inlining, (b) write files, pass paths
- **Chose:** write to disk, reference by path. `-p` stays ~500 chars.
- **Why:** practical limits on -p size. Also enables token reuse — Claude Code can cache file reads across sub-agents when shared files don't change between batches.
- **Cascade:** backend writes all inputs to `input/` on kick-off, references by absolute path
