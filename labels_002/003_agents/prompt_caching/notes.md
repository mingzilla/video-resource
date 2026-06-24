# Rule: Prompt caching

> **Scope:** multi-call LLM solutions (`claude -p`, API, sub-agents)
> **Read once per session.** Do not re-read unless the user asks.

## How caching works

Caching reuses a **prefix** of the serialized request. Next call matches from byte 0 to first mismatch — everything after is billed fresh. One changed byte near the front forfeits the whole tail.

| Fact                                                          | Consequence                                       |
|---------------------------------------------------------------|---------------------------------------------------|
| Cache match stops at first differing token                    | early change kills large tail                     |
| Cache read is ~4–5× cheaper (3rd party) or ~1/10× (Anthropic) | miss pays full price                              |
| "Cache read" total = sum over every call                      | big number ≠ high hit rate; read per-call pattern |
| TTL short (~5 min on Anthropic)                               | sparse calls fall off cache                       |

**Why compounding matters:** Every request resends entire chat history. Caching is the only thing making stable prefix cheap.

| Force                 | Consequence                                                                                    |
|-----------------------|------------------------------------------------------------------------------------------------|
| Tool calls add rounds | each tool = extra round-trip → more requests → caching critical                                |
| Turns accumulate      | each later turn carries all prior turns → without caching, cost grows with conversation length |

Long session + broken cache = dominant cost.

## What breaks caching (killers)

| # | Killer               | Why                                                                    | Fix    |
|---|----------------------|------------------------------------------------------------------------|--------|
| 1 | **Prefix pollution** | per-message changing token near front (e.g., `cch=<hash>`)             | §Fix 1 |
| 2 | **Provider lottery** | router load-balances to random upstream (different cache stores)       | §Fix 2 |
| 3 | **Prompt drift**     | each call improvises prompt, or variable content interleaved in prefix | §Fix 3 |

```text
sub 1:  [cch=8fcf6][system][tools]["hi"]                       → provider caches this
sub 2:  [cch=9bc5c][system][tools]["hi"]["hey"]["hi again"]    → mismatch at the hash → match stops here
         ^^^^^^^^^^
```

## How to fix each killer

### Fix 1: Prefix pollution

`claude -p` stamps an attribution header on each message for non-Anthropic providers.

**Fix:** `export CLAUDE_CODE_ATTRIBUTION_HEADER=0` before the run.

```shell
function api::run_with_claude_p_pattern() {
    # CLAUDE_CODE_ATTRIBUTION_HEADER=0 is the load-bearing caching switch. claude prepends an
    # attribution block to the system prompt whose fingerprint is derived from the conversation, so
    # it shifts every turn. The first-party Anthropic API strips it; DeepSeek (a third-party provider)
    # does NOT, so the divergent first block defeats DeepSeek's automatic prefix cache on every turn.
    # =0 omits it -> stable prefix -> cache_read hits at $0.0028/M vs $0.14/M miss (50x). Same reason
    # as the v032 OpenRouter path, but here that one var is all we need — no ccr/provider-pin/session
    # stickiness. ANTHROPIC_SMALL_FAST_MODEL pins the background/haiku slot too (else it asks for a
    # claude-haiku-* name).
    CLAUDE_CODE_ATTRIBUTION_HEADER=0 \
    ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic \
    ANTHROPIC_AUTH_TOKEN="${DEEPSEEK_API_KEY}" \
    ANTHROPIC_MODEL=deepseek-v4-flash \
    ANTHROPIC_SMALL_FAST_MODEL=deepseek-v4-flash \
    claude -p "Reply with the single word: pong"
}
```

### Fix 2: Provider lottery

Each upstream has its own cache store. Random provider = guaranteed miss.

**Fix:** Pin one provider:

```
provider.order: [<slug>]
allow_fallbacks: false
```

### Fix 3: Prompt drift

No byte-identical prefix exists to match against.

**Fix:** Build prompt by code — fixed prefix, variables last.

Order from **most stable → most mutable**:

| Position       | Content                                                                     | Cacheable |
|----------------|-----------------------------------------------------------------------------|-----------|
| Front (prefix) | system prompt, tool schemas, output schema, rules, aids, brief (facts only) | yes       |
| End (suffix)   | per-call input rows, context snowball (cumulative result)                   | no        |

**Rules:**

- Schema first (consistent across calls)
- Split brief (stable) from snowball (mutating)
- Concatenate fragments in fixed order with `\n`
- Accuracy > caching — don't freeze wrong info for cache hit

## Design for the no-cache case

When caching is broken or absent, these levers shrink cost:

| Lever               | Action                                                                                                           |
|---------------------|------------------------------------------------------------------------------------------------------------------|
| Fewer turns         | batch independent reads into one call; fix retry churn                                                           |
| Smaller floor       | disallow unused tools; conditional `[WHEN]→[READ]`; select only needed DB columns                                |
| Stagger parallelism | two workers sharing prefix race: warm cache first, then second. Naive parallelism can cost more than sequential. |

**Design assumption:** Strong native caching (Opus) hides bloat — 1/10× price makes bulk look free. Design for cheap model / router (no-cache case). Lean, conditional, progressive disclosure wins. Caching = upside.

## How to verify

| Check            | How                                                                                                      |
|------------------|----------------------------------------------------------------------------------------------------------|
| Ground truth     | router/provider log (`cached_tokens`), not Claude's self-report                                          |
| Hit verification | `grep -oE '"cached_tokens":[0-9]+' <log>` — expect ≈ previous call's `prompt_tokens` from call #2 onward |
| Healthy pattern  | hits become H-dominant after call #1; scattered `..H..H.` = killer still live                            |
