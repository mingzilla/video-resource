# Tool-call analysis — 11274984 (v17 / no_leak / jack_1, deepseek arm)

Session `d635fd8e-a6d3-4415-8f54-5ab64aadf2a0` — **86 API calls, 100 tool calls** (Bash ×88, Read ×9, Glob ×1, Write ×1, Edit ×1), 14 absorbed into parallel batches, 76/86 cache-hit, ~3580s. Comparison cost ≈ **$22.26** (Opus-4.5-equivalent: fresh×$5/M + cache×$0.5/M + out×$25/M). `rounds` = `length(result.json)` = **24**.

> **Source correction.** The transcript is NOT in the output dir — it lives in the `claude -p` session store: `~/.claude/projects/-mnt-e-code-github-release-mvp-work--clean-context-investment-history/d635fd8e-….jsonl`. The prior `__old` report fed the parser `11274984__1A__output.jsonl` (a *data-output* file, `kind:"suppressed"/"round"`, zero `assistant`/`user` records) and so emitted 0 calls. The accelerator script is correct; it was pointed at the wrong file. `cli.json` is 0 bytes here and is not used.

## Root cause — the run had to build its own skill

`SKILL.md` was a **stub** (call 01 Read → 131 chars). With no working extractor shipped, the agent reverse-engineered the entire pipeline at runtime:

| Phase                                     | Calls | What happened                                                                                                                                                                                           |
|-------------------------------------------|-------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Orient                                    | 01–05 | Read the stub SKILL.md + instruction.md; discover the skill dir 3 different ways                                                                                                                        |
| Schema discovery                          | 06–12 | `.tables` / `DESCRIBE` / data_type & data_ref counts / 1D preview                                                                                                                                       |
| **Format inference from other companies** | 13–21 | `ls` output dir, then read **05252842 / 01003142 / 06212970** result.json + research_notes + plan.json to infer the expected output schema                                                              |
| Evidence gathering                        | 22–42 | per-data_ref queries (1B SH01/MR01/RESOL ×9, then 1A/1C/1F/1R/1I)                                                                                                                                       |
| **Author + debug the skill**              | 43–86 | mkdir; **Write SKILL.md (×2)**; **rewrite `extract.py` in full ×7** (calls 48, 54, 57, 61, 64, 69, 73); run it; re-read `result.json` ~9×; fix de-minimis threshold; debug a hashlib round-id collision |

Half the run (44 of 86 calls) is the agent writing and re-writing a 20 KB `extract.py` that should have shipped with the skill. The 7 full rewrites cost ≈ **47.6k output tokens (60% of all output)**, and each `cat > extract.py` busts the prompt cache — the next call re-bills the whole context fresh (the misses at 54/58/64/74 each re-bill ~80–140k fresh-in). That cache thrashing is why **Σ fresh = 3.77M** for a conversation whose live context never exceeds ~150k.

## How to read

| Column                  | Meaning                                                                                      |
|-------------------------|----------------------------------------------------------------------------------------------|
| In / Out (ch)           | tool-argument JSON size / tool-result size carried in context                                |
| Tool s                  | tool execution time (result ts − call ts)                                                    |
| Fresh / Cache / Out tok | uncached input / cache-read input / generated tokens (deepseek-served, labelled opus by CCR) |
| Waste                   | `N` ok · `P` partial · `Y` wasted, with reason                                               |

## Main agent — all 86 calls

|  # | Type  | Purpose                               | In(ch) | Out(ch) | Tool s |         Fresh |      Cache rd |    Out tok | Waste                                         |
|---:|-------|---------------------------------------|-------:|--------:|-------:|--------------:|--------------:|-----------:|-----------------------------------------------|
| 01 | Read  | SKILL.md — **returns 131 ch (stub)**  |    126 |     131 |   11.8 |        16,507 |         1,024 |         91 | N — but this stub is the root cause           |
| 02 | Glob  | `**/*.md` in skills dir               |    115 |     159 |    0.0 |           256 |        17,408 |        144 | N                                             |
| 03 | Bash  | `ls -laR` skill dir                   |    124 |     197 |    0.1 |        17,949 |             0 |         76 | P — 3rd way to list the same dir              |
| 04 | Bash  | `find .claude`                        |    117 |      31 |    0.5 |           435 |        17,664 |        204 | P — redundant with 02/03                      |
| 05 | Read  | instruction.md                        |    101 |   2,821 |    0.0 |           479 |        17,920 |        118 | N                                             |
| 06 | Bash  | duckdb `.tables`                      |     86 |      24 |    0.6 |         1,599 |        18,432 |        203 | P — could batch w/ 07–08                      |
| 07 | Bash  | `DESCRIBE records`                    |     96 |     948 |    0.1 |           254 |        19,968 |        193 | P                                             |
| 08 | Bash  | data_type counts                      |    163 |     174 |    0.1 |         2,133 |        20,224 |         85 | P                                             |
| 09 | Bash  | data_ref counts                       |    170 |     272 |    0.1 |           254 |        22,272 |        169 | N                                             |
| 10 | Bash  | per-company data_ref/tier counts      |    255 |     662 |    0.1 |           376 |        22,528 |        188 | N                                             |
| 11 | Bash  | all-ref previews (LEFT 200)           |    269 |  13,699 |   12.1 |           692 |        23,040 |        137 | N                                             |
| 12 | Bash  | 1D previews (LEFT 500)                |    230 |  21,332 |    0.6 |         4,116 |        23,552 |        254 | N                                             |
| 13 | Bash  | `ls` output dir                       |     73 |     660 |   11.5 |        11,017 |        27,648 |         80 | N                                             |
| 14 | Bash  | `ls` 11274984 outputs                 |    162 |      26 |    0.0 |         1,081 |        37,888 |        101 | N                                             |
| 15 | Bash  | read **05252842** result.json         |    198 |     209 |    0.2 |           178 |        38,912 |        103 | Y — cross-company peek to infer output schema |
| 16 | Bash  | `ls` 01003142 result.json             |     87 |     107 |    0.0 |           105 |        39,168 |         69 | Y — cross-company                             |
| 17 | Read  | **01003142** result.json              |    166 |   5,805 |    0.0 |           486 |        38,912 |        101 | Y — cross-company                             |
| 18 | Read  | **01003142** research_notes.json      |    182 |   3,208 |    0.6 |         2,759 |        38,912 |        191 | Y — cross-company                             |
| 19 | Read  | **06212970** result.json              |    166 |     631 |   17.6 |         1,877 |        41,472 |        125 | Y — cross-company                             |
| 20 | Read  | **06212970** research_notes.json      |    168 |   7,684 |    0.0 |           715 |        43,008 |         89 | Y — cross-company                             |
| 21 | Read  | **01003142** plan.json                |    159 |     765 |    0.4 |         3,233 |        43,008 |        221 | Y — cross-company                             |
| 22 | Bash  | 1B full rows                          |    546 |     733 |   13.6 |         2,260 |        46,080 |        255 | P — 1B is the triage/large source             |
| 23 | Bash  | 1B rows (-json)                       |    230 |   2,012 |    0.1 |           441 |        48,384 |        109 | P — re-query of 22                            |
| 24 | Bash  | 1B SH01 filter                        |    908 |      31 |    0.1 |         1,488 |        48,128 |        296 | P                                             |
| 25 | Bash  | 1B SH01 filter (v2)                   |    893 |     616 |    0.1 |           266 |        49,664 |        294 | P                                             |
| 26 | Bash  | 1B SH01 filter (v3)                   |    652 |     616 |    0.1 |         1,266 |        49,152 |        231 | P — 4th 1B SH01 variant                       |
| 27 | Bash  | `cat /tmp/sh01_1b.json`               |     46 |     345 |    0.0 |        50,857 |             0 |         55 | P — cache miss, re-bills full ctx             |
| 28 | Bash  | 1B SH01 (v5)                          |    541 |   1,468 |   14.3 |        29,535 |        21,504 |        224 | P                                             |
| 29 | Bash  | 1B MR01 filter                        |    570 |     217 |   15.2 |         1,770 |        50,176 |        268 | P                                             |
| 30 | Bash  | 1B RESOLUTION filter                  |    586 |     822 |    0.1 |         1,119 |        51,200 |        213 | P                                             |
| 31 | Bash  | 1A rows                               |    613 |     252 |    0.1 |           574 |        52,224 |        217 | N                                             |
| 32 | Bash  | 1C rows                               |    522 |     191 |    0.1 |        53,114 |             0 |        202 | N (cache miss)                                |
| 33 | Bash  | 1F rows                               |    589 |     134 |    0.1 |        35,961 |        17,408 |        214 | N                                             |
| 34 | Bash  | 1F preview (LEFT 200)                 |    439 |     113 |    0.1 |           397 |        53,248 |        176 | P — re-query of 33                            |
| 35 | Bash  | 1F preview (v2)                       |    250 |   1,296 |    0.1 |           622 |        53,248 |        115 | P                                             |
| 36 | Bash  | `cat` 01003142 1A output.jsonl        |     98 |   2,219 |    0.4 |         1,230 |        53,248 |        231 | Y — cross-company peek                        |
| 37 | Bash  | 1R rows                               |    466 |      11 |   11.4 |        56,063 |             0 |        211 | N (cache miss)                                |
| 38 | Bash  | 1R rows (v2)                          |    220 |      31 |    0.1 |        55,252 |         1,024 |        105 | P — re-query of 37                            |
| 39 | Bash  | 1I rows                               |    611 |     377 |   12.0 |         1,103 |        55,296 |        282 | N                                             |
| 40 | Bash  | 1I preview (LEFT 300)                 |    453 |     616 |    0.1 |           499 |        56,320 |        175 | P — re-query of 39                            |
| 41 | Bash  | 1I rows (v3)                          |    583 |     287 |    0.1 |           868 |        56,320 |        215 | P                                             |
| 42 | Bash  | 1I `SELECT *`                         |    530 |   3,229 |    0.1 |         1,203 |        56,320 |        202 | P — full-row over-fetch                       |
| 43 | Bash  | mkdir skill dir                       |    124 |      31 |   14.3 |         1,459 |        57,344 |        323 | N — symptom of missing skill                  |
| 44 | Write | **author SKILL.md**                   |  4,002 |      96 |    0.0 |           776 |        58,368 |      1,092 | Y — skill should already exist                |
| 45 | Bash  | `cat >` SKILL.md (same content)       |  3,097 |      16 |   16.0 |         1,903 |        58,368 |        929 | Y — duplicate write of 44                     |
| 46 | Bash  | mega exploratory shell script (36 KB) | 35,899 |     597 |   59.6 |         1,056 |        60,160 |      8,115 | Y — 8.1k out tok of throwaway script          |
| 47 | Bash  | `pip list \| grep duck`               |     50 |      31 |    0.3 |        42,891 |        26,624 |        107 | N                                             |
| 48 | Bash  | **`cat > extract.py` (rewrite #1)**   | 28,263 |     768 |   57.8 |         1,050 |        68,608 |      6,829 | Y — authoring the extractor                   |
| 49 | Bash  | duckdb schema recheck                 |    186 |     237 |   14.8 |        57,206 |        19,456 |        108 | P — already known from 06–08                  |
| 50 | Bash  | python duckdb probe                   |    454 |     189 |    0.1 |         1,087 |        75,776 |        170 | P — script logic in heredoc                   |
| 51 | Bash  | shell var probe                       |    487 |     525 |   12.7 |           309 |        76,800 |        216 | P                                             |
| 52 | Bash  | read own result.json                  |    421 |   1,609 |   16.3 |           725 |        76,800 |        232 | N                                             |
| 53 | Bash  | 1D rows re-query                      |    394 |   3,000 |   13.2 |         1,749 |        76,800 |        206 | P — re-query of 12                            |
| 54 | Bash  | **`cat > extract.py` (rewrite #2)**   | 29,487 |     554 |   53.2 |        79,786 |             0 |      7,308 | Y — rewrite + full cache miss (80k fresh)     |
| 55 | Bash  | test extractor logic (heredoc)        |  3,130 |   2,718 |   15.2 |        76,021 |        11,264 |        990 | P                                             |
| 56 | Bash  | test extractor logic (heredoc)        |    799 |   6,047 |   13.8 |        67,103 |        22,528 |        641 | P                                             |
| 57 | Bash  | **`cat > extract.py` (rewrite #3)**   | 21,697 |     137 |   89.2 |        72,802 |        19,456 |      6,321 | Y — rewrite                                   |
| 58 | Bash  | read own result.json                  |    370 |     949 |    0.0 |        98,677 |             0 |        161 | P — re-read + cache miss (99k fresh)          |
| 59 | Bash  | test logic (heredoc)                  |  3,597 |   2,135 |   17.7 |        80,765 |        18,432 |      1,455 | P                                             |
| 60 | Bash  | test logic (heredoc)                  |  1,669 |   1,820 |   14.1 |         2,404 |        99,072 |        770 | P                                             |
| 61 | Bash  | **`cat > extract.py` (rewrite #4)**   | 20,712 |     108 |   72.0 |         1,493 |       101,376 |      6,748 | Y — rewrite                                   |
| 62 | Bash  | read own result.json                  |    370 |     999 |    0.0 |        86,142 |        23,552 |        161 | P                                             |
| 63 | Bash  | test logic (heredoc)                  |  3,414 |     896 |   16.2 |       109,242 |         1,024 |      1,376 | P                                             |
| 64 | Bash  | **`cat > extract.py` (rewrite #5)**   | 19,430 |     108 |  106.7 |       111,935 |             0 |      6,301 | Y — rewrite + cache miss (112k fresh)         |
| 65 | Bash  | read own result.json                  |    370 |     699 |    0.1 |       106,026 |        12,288 |        161 | P                                             |
| 66 | Bash  | test logic (heredoc)                  |  3,990 |   2,005 |   15.3 |        76,785 |        41,984 |      1,300 | P                                             |
| 67 | Bash  | test logic (heredoc)                  |  1,544 |   4,575 |   12.4 |         3,216 |       117,760 |        564 | P                                             |
| 68 | Bash  | test logic (heredoc)                  |    851 |     636 |    9.9 |        93,360 |        29,696 |        640 | P                                             |
| 69 | Bash  | **`cat > extract.py` (rewrite #6)**   | 19,916 |     108 |  173.0 |           259 |       123,648 |      5,947 | Y — rewrite                                   |
| 70 | Bash  | read own result.json                  |    370 |     949 |    0.1 |       112,524 |        17,408 |        161 | P                                             |
| 71 | Bash  | test logic (heredoc)                  |  4,384 |   2,104 |   65.7 |       113,073 |        17,408 |      1,505 | P                                             |
| 72 | Bash  | test logic (heredoc)                  |  1,737 |   1,545 |   35.3 |       119,635 |        13,312 |        770 | P                                             |
| 73 | Bash  | **`cat > extract.py` (rewrite #7)**   | 20,196 |     108 |  123.9 |       128,112 |         6,144 |      6,292 | Y — rewrite + near-full miss (128k fresh)     |
| 74 | Bash  | read own result.json                  |    370 |   1,049 |    0.1 |       140,626 |             0 |        161 | P — cache miss (141k fresh)                   |
| 75 | Bash  | test logic (heredoc)                  |    701 |     373 |   16.3 |       137,119 |         4,096 |        795 | P                                             |
| 76 | Edit  | edit extract.py (de-minimis)          |    412 |      96 |   13.9 |       142,142 |             0 |        361 | Y — debugging hand-written script             |
| 77 | Bash  | `sed` de-minimis 10000→1000           |    161 |      31 |    0.0 |        84,186 |        58,368 |         92 | Y — second threshold edit                     |
| 78 | Bash  | run extract.py                        |    449 |     108 |    0.1 |       134,472 |         8,192 |        175 | N                                             |
| 79 | Bash  | read own result.json                  |    370 |   1,199 |    0.0 |       142,931 |             0 |        161 | P — repeat verify                             |
| 80 | Bash  | read own result.json                  |    704 |     339 |    0.1 |       139,467 |         4,096 |        250 | P — repeat verify                             |
| 81 | Bash  | read own research_notes.json          |    893 |   1,868 |   14.3 |       136,798 |         7,168 |        509 | N                                             |
| 82 | Bash  | hashlib collision probe               |    602 |      39 |   12.2 |       144,408 |         1,024 |        583 | Y — debugging round-id hash                   |
| 83 | Bash  | `sed` hexdigest length fix            |    339 |      31 |   11.1 |       141,951 |         4,096 |        453 | Y — id-hash churn                             |
| 84 | Bash  | grep to check what sed did            |    339 |     191 |   12.8 |       132,182 |        14,336 |        534 | Y — recovery from blind sed                   |
| 85 | Bash  | run extract.py (final)                |    449 |     108 |   15.3 |       145,083 |         2,048 |        422 | N                                             |
| 86 | Bash  | read own result.json (final)          |    372 |   2,003 |    0.0 |       137,391 |        10,240 |        164 | N                                             |
|    |       | **Totals**                            |        |         |        | **3,770,716** | **2,817,024** | **79,791** | **Y ×22 / P ×34**                             |

## Sub-agents

None. `plan.json` routes every data_ref `main`/`triage`, and the run never spawned a sub-agent — it did everything inline, including authoring the skill.

## Run summary

| Company  | arm            | rounds | API calls | dur (s) | out tok | in tok | cache rd | cost ($) |
|----------|----------------|-------:|----------:|--------:|--------:|-------:|---------:|---------:|
| 11274984 | no_leak/jack_1 |     24 |        86 |    3580 |   79.8k |  3.77M |    2.82M |    22.26 |

| Company  | Run            | Rounds | Agents | API calls | Parallel | dur (s) | Fresh in | Cache read | Hit rate | Out tok | Waste Y/P | Tok-eq in |
|----------|----------------|-------:|-------:|----------:|---------:|--------:|---------:|-----------:|---------:|--------:|----------:|----------:|
| 11274984 | no_leak/jack_1 |     24 |      1 |        86 |       14 |    3580 |    3.77M |      2.82M |    76/86 |   79.8k |     22/34 |     4.05M |

```
Column definitions:

| Column | Definition |
|---|---|
| API calls | model round trips, main+sub summed (one turn = one API call, possibly several parallel tool calls) |
| rounds | length(result.json) — behaviour signal |
| in tok / Fresh in | uncached input tokens |
| cache rd / Cache read | cache-read input tokens |
| out tok | generated tokens |
| cost ($) | fresh×$5/M + cache×$0.5/M + out×$25/M — Opus-4.5-equivalent COMPARISON CURRENCY (deepseek real spend is on OpenRouter; cli.json USD is router-mispriced) |
| Agents | main + sub-agents |
| Parallel | sibling tool calls absorbed into shared API calls |
| Hit rate | API calls with cache_read>0 / total |
| Waste Y/P | counts of Y / P verdicts in the per-call table |
| Tok-eq in | Fresh + 0.1×Cache read |
```

## What to fix (highest leverage first)

| Fix                                                              | Calls eliminated | Why                                                                                                                                                                                                                         |
|------------------------------------------------------------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Ship a working `extract.py` + real `SKILL.md`** with the skill | ~44 (43–86)      | The entire back half is the agent authoring and debugging the extractor; 7 full rewrites = 47.6k out tok + the cache-miss re-bills that dominate the 3.77M fresh-in                                                         |
| **Define the output schema in SKILL.md**                         | 7 (15–21, 36)    | Removes the cross-company peeking (`no_leak` violation: it read 05252842/01003142/06212970 to infer format)                                                                                                                 |
| **Pin the data-ref query patterns** in the skill                 | ~10              | 1B SH01 was queried 5 ways (24–28); 1F/1I/1R each re-queried 2–4×                                                                                                                                                           |
| **Fix the binding doc**                                          | —                | `action__optimisation__list_tools.md` must say the transcript is at `~/.claude/projects/<slug>/<session_id>.jsonl`, not the `__1X__output.jsonl` data files — that mis-pointing is what produced the false "0 calls" report |
