# v032 — Fix: per-source handshake/merge (sub-agent → ledger)

## The defect

Baseline already has the right architecture: **sequential snowball ledger**. Each source's input is the accumulated `result.json` + `notes.json` from all previous sources.

**The failure:** per-source append is done by the main agent **by hand**, and the hand-merge silently dropped whole sources (Crisp's 1D, Darktrace's 1D+1A).

**Wrong path (reverted):** batch merge at the end. This breaks the ledger — source 2 runs against empty ledger, source 3 can't see 1 or 2. The fix must be **per source, inside the loop.**

## The fix

Replace the **per-step hand-append** with a deterministic Python merge, called **every iteration**, right after the source produces output and before the loop advances.

## Corrected flow

```mermaid
sequenceDiagram
    participant Main as Main Agent
    participant Sub as Sub-Agent (optional)
    participant Brief as <CN>__brief.json
    participant Plan as <CN>__plan.json
    participant Out as <CN>__<ref>__output.json
    participant Ledger as result.json + notes.json
    participant Merge as action_output__merge_and_check.py
    Note over Main: Step 0: Build brief + plan
    Main ->> Brief: write
    Main ->> Plan: write
    Note over Main: Step 1: Classify pattern → trust-tier order

    loop For each source (sequential)
        Note over Main: Step 2a: Extract ONE source
        alt main route
            Main ->> Main: process inline
        else sub route
            Main ->> Sub: invoke
            Sub -->> Main: output
        end
        Main ->> Out: write <CN>__<ref>__output.json
        Note over Main: Step 2b: Merge + check THIS source
        Main ->> Merge: invoke with Out + Ledger + Brief
        Merge ->> Merge: check discovered == emitted + suppressed
        alt check passes
            Merge ->> Ledger: append rounds → result.json
            Merge ->> Ledger: append suppressed + traces → notes.json
            Ledger -->> Main: updated snowball
        else check fails
            Merge -->> Main: non-zero + reason
            Main ->> Main: reprocess THIS source
            Main ->> Merge: re-run 2b
        end
    end

    Note over Main: Step 3: Reconcile (unchanged)
    Main ->> Ledger: final result.json + research_notes.json
```

## The new function: `scripts/action_output__merge_and_check.py`

| Aspect      | Detail                                                                                                    |
|-------------|-----------------------------------------------------------------------------------------------------------|
| Called by   | Main agent, once per source, at step 2b                                                                   |
| Inputs      | `<CN>__<ref>__output.json`, `result.json`, `notes.json`, `<CN>__brief.json`, `CN`, `ref`                  |
| Check       | `discovered == emitted + suppressed` — `discovered` = brief census count                                  |
| Merge       | `rounds` → `result.json`; `suppressed_records` + `per_round_traces` + `cross_source_flags` → `notes.json` |
| Output      | Updated `result.json` + `notes.json` on success; non-zero + reason on failure                             |
| Idempotency | Guard: refuse to merge a `ref` that already has a `coverage` row                                          |

## Supporting changes

1. **`main` sources now write per-source output file too** — same shape as `sub`
2. **Rename** `<CN>__<ref>__subagent.json` → `<CN>__<ref>__output.json`
3. **`SKILL.md` step 2** — replace hand-append with `action_output__merge_and_check.py`
4. **`instruction.md`** — mirror step 2 change

## Out of scope

- Step 3 (Reconcile) — unchanged
- Structural leak (`instruction.md` duplicating SOP) — separate cleanup

## Acceptance

- [ ] Source's rounds appear in `result.json` immediately after processing (visible to next source)
- [ ] Crisp: 1D equity rounds survive
- [ ] Darktrace: 1D (IPO) + 1A (charges) + acquisition all land
- [ ] Short source fails check and is reprocessed before loop advances
- [ ] No batch/end-of-run merge — `action_output__merge_and_check.py` invoked once per source, inside loop
