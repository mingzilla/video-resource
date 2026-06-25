# v032 — Brief: fix the per-source handshake/merge (sub-agent → ledger)

## Why this brief exists

A prior attempt to fix the handshake went down the wrong path: it added a
`merge_and_check.py` that ran **once at the end** as a batch finalizer (glob all
per-source files → assemble → coverage-gate → write finals). That has been
**reverted** (`SKILL.md`, `instruction.md` back to HEAD; the batch script
deleted). We restart from the clean baseline.

The batch approach is not merely suboptimal — it is **architecturally wrong** for
this skill, and stating why is the whole point of this brief.

## The actual defect (narrow and specific)

The baseline already implements the right architecture: a **sequential snowball
ledger**. `SKILL.md` step 2 today:

> "After each source completes, **the main agent appends its rounds to the
> cumulative ledger** (single-writer) **and forwards that growing ledger to the
> next source**."

So actions run **sequentially**, and each one's input is the
`result.json` + `notes.json` accumulated so far (the snowball). The merge is not a
finalize — it is **the step that produces the next action's input**.

The one thing that fails: the **per-source append is done by the main agent by
hand**, and that hand-merge silently dropped whole sources (Crisp's 1D, ~£8.2M;
Darktrace's 1D+1A). The handshake that breaks is "a source's result exists →
write it into `result.json`/`notes.json`," and it breaks **per source, during the
loop** — not at the end.

### Why a batch merge can never fix it

If the merge is deferred to "when everything returns," then source 2 runs against
an empty ledger, source 3 can't see 1 or 2, and every "use the ledger for
cross-source awareness/flagging" instruction is dead — there is nothing in the
ledger yet. A batch merge **deletes the reason the ledger exists**. The fix must
live at the moment of failure: **per source, inside the loop.**

## The fix in one line

Replace the **per-step hand-append** with a small deterministic Python merge,
called **every iteration**, right after the source produces its output and before
the loop advances. Everything else in the baseline stays.

## Corrected flow — and exactly where the new function goes

```text
## Flow — main: extract investment rounds (one company)
in:  COMPANY_NUMBER, db_path, output_dir
out: result.json + research_notes.json   (the snowball, complete after the last source merges)

[sequential]
|
|-- (step 0) — Build brief + plan                              [once, upfront — Phase 0]
|   |-- do:  action__build_company_brief · scripts/main__sub_agent__decision.py
|   |-- out: <CN>__brief.json (facts only) · <CN>__plan.json (per source: main | sub | triage)
|
|-- (step 1) — Classify pattern → trust-tier priority order
|   |-- in:  <CN>__brief.json (census + indexes)
|   |-- out: round-bearing sources, ordered (highest trust tier first)
|
|-- (for each round-bearing source, in trust-tier order): [sequential]   — the snowball loop
|   |
|   |-- (step 2a) — Extract ONE source → its OWN output file
|   |   |-- where: <CN>__plan.json routes inline(main) | one whole-source sub-agent(sub).
|   |   |           SAME Decide & emit either way; only the location changes.
|   |   |-- in:   action__extract__<ref> (+ mandatory reads: task_contract, round_definition,
|   |   |           output_protocol, aid) · <CN>__brief.json · db pointer (what to read, not raw rows)
|   |   |           · result.json + notes.json   ◀── THE SNOWBALL SO FAR (this source's input)
|   |   |-- out:  <CN>__<ref>__output.json  { rounds, suppressed_records, per_round_traces,
|   |   |           cross_source_flags }    (sub-agent writes it on the `sub` path;
|   |   |           the MAIN AGENT writes its own inline output the SAME way on the `main` path)
|   |
|   |-- (step 2b) — Merge + check THIS source into the snowball
|   |   |          ◀━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
|   |   |          ┃  NEW PYTHON FUNCTION:  scripts/action_output__merge_and_check.py        ┃
|   |   |          ┃  run by the MAIN AGENT, once per source, here.                          ┃
|   |   |          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
|   |   |-- in:    <CN>__<ref>__output.json · result.json + notes.json · <CN>__brief.json · CN · ref
|   |   |-- check: discovered  ==  emitted + suppressed in the output file
|   |   |           · discovered = the brief census `n` for this ref (`source_census[].n`, or
|   |   |             `allot_count_1D` for 1D) — the SAME denominator rule__output_protocol.md
|   |   |             already defines; it is raw count(*), NOT a deduped/unique-record count.
|   |   |           → this ONE source is fully accounted before it is allowed into the ledger
|   |   |-- merge: rounds → result.json ; suppression + traces + flags → notes.json
|   |   |-- out:   updated result.json + notes.json  → becomes the NEXT source's step-2a input
|   |   |-- WHY:   this replaces the MAIN AGENT's by-hand append — the step that silently
|   |   |           dropped Crisp's 1D and Darktrace's 1D+1A. Code does it now, per source.
|   |   |-- fail:  if the check fails (source short / file malformed), the source is NOT merged;
|   |   |           the main agent reprocesses THAT source, re-runs 2b, then advances. Local
|   |   |           loop-back per source — NOT a global end-of-run gate.
|   |   |-- term:  the loop-back TERMINATES via SUPPRESSION, not a smaller denominator: a leftover
|   |   |           raw record that is not a round (a folded tranche, a Q2/Q3 re-filing, a non-round)
|   |   |           is recorded in suppressed_records with a reason. account-for = emit OR suppress,
|   |   |           so emitted + suppressed == raw count is always reachable for a faithful source.
|
|-- (step 3) — Reconcile                                       [once, over the COMPLETE snowball]
    |-- in:   <CN>__brief.json + the complete ledger it already holds (result + notes)
    |-- do:   cross-tier dedup (Q1 supersedes Q2 on one event) · fold cross-source one-event
    |          groups · resolve the cross_source_flags step 2a raised  (over the compact ledger)
    |-- out:  final result.json + research_notes.json
```

The new function lives at **step 2b**, inside the per-source loop. Nowhere else.

## The new function — `scripts/action_output__merge_and_check.py`

| aspect | detail |
|---|---|
| **Name** | `action_output__merge_and_check.py` — operates on an **action's output**, not specifically a sub-agent's. The main agent calls it on its *own* inline output (`main` route) and on a sub-agent's file (`sub` route) identically. `sub_agent_output__` would be wrong. |
| **Called by** | the **main agent**, once per source, at step 2b. |
| **Inputs** | the source's `<CN>__<ref>__output.json`; the current `result.json` + `notes.json` (the snowball); `<CN>__brief.json` (for `discovered`); `CN`; `ref`. |
| **Check** | `discovered == emitted + suppressed` in the output file, where **`discovered` is the brief census count** (`source_census[].n`, or `allot_count_1D` for 1D) — the exact denominator `rule__output_protocol.md` already defines. This is **raw `count(*)`, NOT a unique/deduped-record count**; folded tranches and re-filing duplicates are *suppressed* (counted in `suppressed`), so a faithful source satisfies `==`. Per-source check at the moment the source returns — not a coverage gate over all sources. |
| **Termination** | the per-source loop-back terminates by **suppression**, never by shrinking the denominator: any leftover raw record that is not a round must land in `suppressed_records` with a reason. Switching to a "unique-record" denominator would make a correctly-suppressed source *fail* the `==` check — do not do it. |
| **Merge** | append `rounds` → `result.json`; `suppressed_records` + `per_round_traces` (re-indexed to global position) + `cross_source_flags` → `notes.json`; write this ref's `coverage` row (`discovered/emitted/suppressed/complete`) per `rule__output_protocol.md`. |
| **Output** | updated `result.json` + `notes.json` (the grown snowball) on success; non-zero + a reason on a failed check (source not merged). |
| **Idempotency** | a **guard, not a replace**: refuse to merge a `ref` that already has a `coverage` row (already merged). Because a failed check means the source was *never* merged, a retry is always a clean first append — full row-splice/replace is unneeded complexity. |

## Supporting changes required (small)

1. **`main` sources now write a per-source output file too.** Today a `main`
   source is processed inline and the agent appends from memory. For the code
   merge to read it, the `main` path must write `<CN>__<ref>__output.json` in the
   same shape a `sub` writes — then call step 2b. This unifies both routes through
   one reliable merge.
2. **File-name consistency (recommended, your call).** The baseline calls the
   per-source file `<CN>__<ref>__subagent.json`. Since `main` writes it too,
   rename to `<CN>__<ref>__output.json` for consistency with the function name.
   Ripple: `main__sub_agent__build_prompt.py`'s `OUT_FILE` (5th) arg, and the path
   the sub-agent is told to write.
3. **`SKILL.md` step 2 edit.** Replace "the main agent appends its rounds to the
   cumulative ledger (single-writer)" with "the main agent runs
   `action_output__merge_and_check.py` to fold the source into the ledger" — i.e.
   the append is now code, per source.
4. **`instruction.md`** mirrors the step-2 change (it currently restates the SOP).

## Out of scope for this brief (do NOT fold in)

- **Reconcile (step 3) is unchanged.** Cross-source dedup / one-event folding is
  an agent judgment over the compact ledger; it is a different operation from the
  per-source merge and is not what failed. Do not turn it into a code gate or a
  `main.json` directive system (that was part of the wrong path).
- **The structural leak** — `instruction.md` duplicating the SOP and `SKILL.md`
  pointing back at `instruction.md` (a circular import) — is a real, *separate*
  cleanup (skill = class, `main` action = entry point, one-way import). Decide its
  scope on its own; conflating it with the merge fix is part of what derailed the
  last attempt.

## Acceptance — how we know it's fixed

- A source's rounds appear in `result.json` **the moment that source is
  processed**, and are visible to the next source as ledger input (not at the end).
- Re-run Crisp: its 1D equity rounds survive into `result.json`.
- Re-run Darktrace: 1D (IPO) + 1A (charges) + acquisition all land; nothing is
  silently dropped.
- A short source fails its step-2b check and is reprocessed before the loop
  advances — it never reaches step 3 unaccounted.
- No batch/end-of-run merge anywhere; `action_output__merge_and_check.py` is
  invoked once per source, inside the loop.
