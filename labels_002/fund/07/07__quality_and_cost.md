## CLI Headless Execution

```shell
claude -p "prompt.md" # 50k - 100k
| -- tools - calculation / web search / web fetch / reasoning / db / coding 
```

## Different Setup and Cost Quality Comparison

| Option | Harness      | Model             | Quality | Cost | Duration | What the quality number means                                                                                                                                          |
|--------|--------------|-------------------|---------|------|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A      | claude -p    | opus 4.7          | 90%     | 100  | 10       | Reference. Deep judgement, full investor recall, exact amounts                                                                                                         |
| B      | claude -p    | deepseek v4 flash | 85%     | 3    | 7        | Matches Opus on clean companies (Camlab identical, LCG close); over-includes borderline rows (Brandauer hurdle+bank); 11/20 investor recall; **notes-file index bugs** |
| C      | opencode run | deepseek v4 flash | 55%     | 3    | 5        | Collapses on high-volume companies (LCG 18 vs 26 rows, 1 investor); **fabricates literals even on simple ones** (Camlab)                                               |

## claude code + deepseek v4 flash

```text
   [claude code] -- [proxy] ------------------- [deepseek]
   [claude code] -- [proxy] -- [open router] -- [deepseek]
                      |
                      |- claude-code-router (usage - check logs)
```