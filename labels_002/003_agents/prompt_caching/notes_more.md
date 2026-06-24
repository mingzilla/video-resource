### Optimise

What you do: Apply only the levers the measurement implicated; re-run; compare
File that does it: action__optimise__claude_p_cost.md
Gate applied: faithfulness gate: behaviour must match baseline, or be adjudicated against source data

#### prompt caching - openrouter

work/investment_data/_meta/_rules/rule__claude_p_openrouter_deepseek_setup.md

Prompt caching — two important settings to enable

1. For non-anthrophic, add env var `export CLAUDE_CODE_ATTRIBUTION_HEADER=0` when running `claude -p`. Otherwise, it prefixes `cch` to EACH message

```bash
export CLAUDE_CODE_ATTRIBUTION_HEADER=0
work/investment_data/_docs/v032_claude_p_skills/claude_p__deepseek__run.sh <company_number> <fresh_output_dir>
```

```text
Events:
  user: hi  - 1 msg sent
  claude: hey
  user: hi again - 3 msg sent (prefix before `hi` destroys prompt caching)

Problem:
  submission 1:  [cch=8fcf6][system prompt][tools]["hi"]
                                                            → provider caches all of this
  submission 2:  [cch=9bc5c][system prompt][tools]["hi"]["hey"]["hi again"]
                  ^^^^^^^^^^
                  mismatch at token ~40 → matching stops HERE
```

2. ccr: `~/.claude-code-router/config.json` - needs to set: `"order": ["atlas-cloud", ...], "allow_fallbacks": false`

#### Optimisation Discussion

From: work/investment_data/_meta/_rules/v032_claude_p_skills__17__token_optimisation.md

```text
[why that many turns] ------------- [tool calls, prompt caching]
[why no caching]      ------------- [auto sent to different providers]
[why tool is a problem] ----------- [you are right, tool is not a problem, it's caching]
[claude sends full history] ------- [yes, i can see it]
[how to lock provider]  ----------- [see instructions]
```

#### Optimisation Breakdown

- Exclude unused tools - Workflow,NotebookEdit,TodoWrite - so that tool schema is not included
- Reduce floor per call - reduce prompt size if possible, they build up
- Reduce turns - if prompt caching is not used then this is significant every turn
- Scripts - treated as blackbox - check execution history to see if it reads script content
- Actions - make sure it's conditionally loaded
- DB query - include only columns needed, exclude unused big column in the response
- Exclude Providers - if using openrouter, exclude providers that are: no prompt caching, high caching cost, low availability
- Prompt structure - put variable at the end
- (CLAUDE_TIMEOUT="60m", --max-turns 200) - allows long-running tasks (e.g. task killed and not finished at 30m), if your max is e.g. 120 turns, set to 200 to protect money

## Concurrency

- API is less likely to be the problem, `claude -p` ram usage can be - 30 claude_p with open router is fine
- Consider: WSL uses 1/2 machine RAM, leave 5GB overhead, have 1GB/claude_p

| Machine                      | WSL cap  | Safe concurrency `(cap−5)/1`         |
|------------------------------|----------|--------------------------------------|
| This (32 GB host)            | 15 GiB   | **~10**                              |
| Other (192 GB host, default) | ~96 GiB  | **~90**                              |
| Other, cap raised to ~170 GB | ~170 GiB | **~165** (leaves ~22 GB for Windows) |