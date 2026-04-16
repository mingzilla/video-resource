# D. The Work Engine

- [12. Work queue over fixed cycles]
- [13. Long AFK tasks handled naturally by work queue]
- [14. DuckDB per-file lock, not global lock]
- [15. Stats table — per-response, not per-company]

---

## The Problem

You have 2000 companies to QA. Each Claude worker can handle 40. You can
run 20 workers. That's 800 per round. How do you process all 2000? And
what happens when George and Sam both submit jobs at the same time?

```text
2000 companies
     |
     v
+--worker-01---+  +--worker-02---+     +--worker-20---+
| 40 companies |  | 40 companies | ... | 40 companies |
+--------------+  +--------------+     +--------------+
     |                 |                     |
     v                 v                     v
  done in 5min      done in 8min         done in 6min
     |                 |                     |
     ?                 ?                     ?

Round 1 = 800. What about the other 1200?
Worker 01 finished 3 minutes ago. It's been sitting idle.
```

---

## Decision 12: Work queue over fixed cycles

> You thought: process in fixed cycles — 800, wait for all to finish, next 800.
> But actually: work queue — fast workers do more rounds, no idle time.

```text
FIXED CYCLES (rejected):

  Round 1                          Round 2
  +----+----+----+----+----+      +----+----+----+----+----+
  | W1 | W2 | W3 |....| W20|      | W1 | W2 | W3 |....| W20|
  +----+----+----+----+----+      +----+----+----+----+----+
  | 40 | 40 | 40 |    | 40 |      | 40 | 40 | 40 |    | 40 |
  +----+----+----+----+----+      +----+----+----+----+----+
    5m   8m   6m        7m           5m   9m   6m        7m
                        |                                |
                   WAIT for W2                      WAIT for W2
                   (3 min idle)                     (4 min idle)


WORK QUEUE (chosen):

  +--------------------------------------------------+
  |              DuckDB: unclaimed pool               |
  |  [co.1] [co.2] [co.3] ... [co.2000]              |
  +--------+-----------+-------------------+----------+
           |           |                   |
           v           v                   v
        +------+    +------+           +------+
        | W-01 |    | W-02 |    ...    | W-20 |
        +------+    +------+           +------+
           |           |                   |
       claim 40    claim 40            claim 40
       process     process             process
       write       write               write
           |           |                   |
       claim 40    claim 40            claim 40     <-- no waiting
       process     process             process
       write       write               write
           |           |                   |
       claim 40    (no more work)      claim 40
       process        exit             process
       write                           write
           |                               |
       (no more work)                  (no more work)
          exit                            exit

  Fast workers do 3 rounds. Slow workers do 2. Nobody waits.
```

- **Q:** how do we handle 2000+ companies when max 40 per worker and 20 max workers?
- **Options:** (a) fixed cycles — process 800, wait, process next 800, (b) work queue — each worker grabs next batch when done
- **Chose:** work queue backed by DuckDB. Workers loop: claim --> process --> write --> repeat.
- **Why:** fixed cycles waste time — fast workers idle waiting for slow ones. Work queue means fast workers do more rounds. No idle time, no artificial iteration boundaries.
- **Cascade:** forced the 3-table DuckDB design (input_records, output_records, processing_records)

---

## Decision 13: Long AFK tasks handled naturally

> You thought: reject requests over worker capacity.
> But actually: the queue just keeps looping. Same code handles 50 and 20,000.

```text
50 companies, 20 workers:

  Workers 1-2 each get 25       <-- most workers never start
  Workers 3-20: no work, exit

200 companies, 20 workers:

  Each worker gets ~10           <-- one round each
  All exit together

2000 companies, 20 workers:

  Each worker loops ~2.5 rounds  <-- fast ones do 3, slow do 2
  Same code, same queue

20000 companies, 20 workers:

  Each worker loops ~25 rounds   <-- still the same code
  Takes hours, but works
```

No capacity check. No cycling logic. No rejection. The queue doesn't care
about the total — each worker just keeps claiming until the pool is empty.

- **Q:** what happens when a user submits 2000 companies but max capacity is 20 x 40 = 800?
- **Options:** (a) reject above capacity, (b) cycle in rounds, (c) work queue handles it
- **Chose:** work queue handles it naturally
- **Why:** 2000 companies / 20 workers = ~2.5 rounds of 40 each. No special logic.

---

## Decision 14: DuckDB per-file lock, not global lock

> You thought: one global lock for all DuckDB access.
> But actually: George and Sam use separate files — per-file locks, zero cross-job contention.

```text
GLOBAL LOCK (rejected):

  George's job                Sam's job
       |                          |
       v                          v
  +----------+               +----------+
  | claim 40 |--+         +--| claim 40 |
  +----------+  |         |  +----------+
                v         v
           +------------------+
           |  SINGLE LOCK     |  <-- Sam waits for George's SQL
           |  (asyncio.Lock)  |      even though different .duckdb
           +------------------+
                    |
                    v
              one at a time


PER-FILE LOCK (chosen):

  George's job                Sam's job
       |                          |
       v                          v
  +----------+               +----------+
  | claim 40 |               | claim 40 |
  +----------+               +----------+
       |                          |
       v                          v
  +-----------+              +-----------+
  | LOCK: G   |              | LOCK: S   |  <-- independent locks
  | george.db |              | sam.db    |      zero contention
  +-----------+              +-----------+
       |                          |
       v                          v
  simultaneous                simultaneous
```

- **Q:** how do we handle concurrent workers writing to the same DuckDB file?
- **Options:** (a) single global asyncio.Lock, (b) dict of locks keyed by db_path, (c) retry-with-sleep
- **Chose:** per-file lock dict. Each DuckDB file gets its own asyncio.Lock.
- **Why:** global lock blocks unrelated jobs. Retry-with-sleep is hacky. Per-file lock = proper FIFO queuing, held for microseconds (SQL only), released before the Claude call.
- **Cascade:** DuckDBManager encapsulates all access — justified its own file

---

## Decision 15: Stats table — per-response, not per-company

> You thought: track costs per company.
> But actually: it's per worker response (40 companies = 1 stats row). JS aggregates.

```text
PER-COMPANY (rejected):

  output_records:
  | Company_Number | Verdict | ... | tokens | cost  |
  |----------------|---------|-----|--------|-------|
  | 09688671       | Valid   | ... | ???    | ???   |  <-- how do you split
  | 11689731       | FP      | ... | ???    | ???   |      60k tokens across
  | 08458210       | Valid   | ... | ???    | ???   |      40 companies?
  ...40 rows from one Claude call


PER-RESPONSE (chosen):

  output_records:                          stats:
  | Company_Number | Verdict | ... |       | workspace   | tokens_in | tokens_out | cost  | count |
  |----------------|---------|-----|       |-------------|-----------|------------|-------|-------|
  | 09688671       | Valid   | ... |       | ws_001      | 58000     | 3200       | $0.12 | 40    |
  | 11689731       | FP      | ... |       | ws_002      | 61000     | 3400       | $0.13 | 40    |
  | 08458210       | Valid   | ... |       | ws_003      | 55000     | 2900       | $0.11 | 40    |
  ...                                     ...

  One Claude call = one stats row. Clean. JS sums for totals.
```

- **Q:** how do we track token usage and cost?
- **Options:** (a) aggregate in state.json, (b) per-company in output_records, (c) per-worker-response in separate table
- **Chose:** separate stats table, one row per successful Claude response. Append-only.
- **Why:** a Claude worker processes 40 companies in one call. The stats are per-call, not per-company. Can't split 60k tokens across 40 rows meaningfully.
- **Cascade:** `auth_method` column tracks subscription vs API for capacity planning
