# E. When Things Go Wrong

- [16. Pause and resume via DuckDB state]
- [17. Auto-respawn on check-progress — polling is self-healing]
- [18. POST /check-progress, not GET]

---

## The Problem

A 20,000 company job runs for hours. Workers process 40 companies each,
loop, process another 40. At any point: the server can crash, a worker
can die, or the Claude subscription can hit its rate limit. What do you
lose?

```text
Hour 0          Hour 2          Hour 4
  |               |               |
  v               v               v
  start           8,000 done      CRASH
  20 workers      still going     |
  running                         v
                                  ???

Without resilience:
  8,000 results = LOST
  Start over from company 1

With resilience:
  8,000 results = SAFE in DuckDB
  Resume from company 8,001
```

---

## Decision 16: Pause and resume via DuckDB state

> You thought: restart from scratch after a crash.
> But actually: DuckDB is the state. Resume = delete expired records, respawn workers.

```text
CSV APPROACH (rejected):

  Worker 1 writes:  intermediate/batch_001.csv  (40 rows)
  Worker 2 writes:  intermediate/batch_002.csv  (40 rows)
  Worker 3 writes:  intermediate/batch_003.csv  (writing...)
                                                    |
                                                  CRASH
                                                    |
  batch_001.csv  -- complete, on disk
  batch_002.csv  -- complete, on disk
  batch_003.csv  -- partial? corrupt? who knows?

  Resume: which batches are done? parse each CSV?
  Merge: concatenate CSVs, handle duplicate headers?
  Fragile.


DUCKDB APPROACH (chosen):

  +-------------------+    +--------------------+    +----------------------+
  | input_records     |    | output_records     |    | processing_records   |
  | (immutable)       |    | (append-only)      |    | (ephemeral)          |
  |                   |    |                    |    |                      |
  | co.1              |    | co.1  Valid        |    | co.121  ws_003       |
  | co.2              |    | co.2  FP           |    | co.122  ws_003       |
  | co.3              |    | co.3  Valid        |    | co.123  ws_003       |
  | ...               |    | ...                |    | ...     expires 3pm  |
  | co.20000          |    | co.120 Valid       |    | co.160  ws_003       |
  +-------------------+    +--------------------+    +----------------------+

  CRASH happens.

  On resume:
    1. DELETE FROM processing_records WHERE expires_at < NOW()
       (co.121-160 return to unclaimed pool)

    2. Unclaimed = input - output - processing
       = 20000 - 120 - 0
       = 19,880 remaining

    3. Respawn workers. They claim from 121 onwards.

  120 results: SAFE. Zero lost. Zero duplicated.
```

- **Q:** a 20,000 company job takes hours. What if the process dies?
- **Options:** (a) restart from scratch, (b) CSV checkpointing, (c) DuckDB as single source of truth
- **Chose:** DuckDB. input = immutable, output = append-only, processing = ephemeral.
- **Why:** CSV merge is fragile. DuckDB gives atomic writes, single-file state, and one query for progress.
- **Cascade:** `/continue` shares `_start_processing()` with `/kick-off`. Only difference: kick-off does setup first.

---

## Decision 17: Auto-respawn on check-progress

> You thought: user calls /continue when it looks stuck.
> But actually: check-progress detects dead workers and respawns automatically.

```text
THE STUCK JOB:

  Time 0:       20 workers running
  Time 30min:   19 workers done, 1 failed (rate limited)
  Time 31min:   Job marked DONE (all workers exited)

  But: 40 companies were in processing_records when the worker died.
       expires_at hasn't passed yet.

  Time 90min:   User polls /check-progress
                  |
                  v
                1. Recycle: DELETE WHERE expires_at < NOW()
                   (40 companies freed)
                  |
                  v
                2. Unclaimed = input - output - processing
                   = 40 remaining
                  |
                  v
                3. Workers dead? YES (task.done() = True)
                   Unclaimed > 0? YES
                  |
                  v
                4. RESPAWN workers
                   Workers claim the 40 companies
                   Process them
                   Job completes

  The user just polled for progress.
  The server fixed itself.
```

```text
WITHOUT auto-respawn:

  User sees:  "DONE - 1960/2000"
  User thinks: "why only 1960?"
  User reads docs: "call POST /continue"
  User calls /continue
  User polls again

  3 extra steps. Every time.


WITH auto-respawn:

  User sees:  "RUNNING - 1960/2000 ... 1970 ... 1980 ... 2000"
  User thinks: nothing. It's working.
```

- **Q:** what if all workers die but unclaimed rows remain?
- **Options:** (a) user manually calls /continue, (b) check-progress detects and respawns
- **Chose:** check-progress recycles expired processing_records and respawns if needed
- **Why:** the user is polling anyway. If "DONE but unclaimed > 0" or "RUNNING but no workers", it fixes itself.
- **Cascade:** check-progress became POST because it has side effects

---

## Decision 18: POST /check-progress, not GET

> You thought: GET /progress — it's just a read.
> But actually: it recycles records and respawns workers. POST — side effects exist.

```text
GET /progress (rejected):

  Client: GET /progress?request_id=abc
  Server: SELECT counts FROM duckdb
          return {completed: 1960, total: 2000}

  Pure read. No side effects. Correct HTTP semantics.
  But: 40 companies are stuck forever. Nobody recycles them.


POST /check-progress (chosen):

  Client: POST /check-progress?request_id=abc
  Server: 1. DELETE expired processing_records     <-- side effect
          2. Check: unclaimed > 0 and workers dead?
          3. If yes: RESPAWN workers               <-- side effect
          4. SELECT counts FROM duckdb
          return {completed: 1960, total: 2000, in_progress: 40}

  Not a read. An active health check.
  The name says it: CHECK progress, don't just READ it.
```

- **Q:** should progress checking be GET or POST?
- **Options:** (a) GET /progress, (b) POST /check-progress
- **Chose:** POST — recycles records and may respawn workers
- **Why:** side effects on a GET violates HTTP conventions. This is an active operation, not a passive read.
