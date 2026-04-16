# F. Paying For It

- [19. Subscription-first, API fallback]
- [20. AFK mode — large requests always use API]
- [21. Multi-user — independent jobs with global worker cap]

---

## The Problem

Claude Code can run on a subscription (Max plan, fixed monthly cost) or
via API (pay per token). The team wants to test without committing to API
costs. But subscriptions have rate limits. And 4 engineers will use this
simultaneously.

```text
Subscription (Max plan):
  + Already paid for
  + Unlimited within rate limits
  - Rate limits hit at scale
  - One account = one rate limit bucket

API:
  + No rate limits (practically)
  + Scales to any volume
  - Pay per token
  - 20,000 companies × $0.003 = $60 per run

The team:
  George:  "I want to test 20 companies quickly"
  Sam:     "I want to run 500 overnight"
  Harini:  "I want to run 50 right now"
  Josh:    "I want to test my new taxonomy"

  All at the same time. One subscription. One API budget.
```

---

## Decision 19: Subscription-first, API fallback

> You thought: always use the API — it's simpler.
> But actually: subscriptions are already paid for. Test the token first, API is fallback.

```text
ALWAYS API (rejected):

  Every request --> ANTHROPIC_API_KEY --> pay per token

  George tests 20 companies: $0.06
  Sam tests 20 companies: $0.06
  Both just testing. Both paying.
  Subscription sitting unused.


SUBSCRIPTION FIRST (chosen):

  Per request:

  +-----------------------------------------+
  | For each token in claude_oauth_tokens:  |
  |   1. export CLAUDE_CODE_OAUTH_TOKEN     |
  |   2. claude -p "respond with: ok"       |  <-- test, costs ~nothing
  |   3. Works? --> use this token. STOP.   |
  |   4. Rate limited? --> try next token.  |
  +-----------------------------------------+
           |                    |
      token works          all failed
           |                    |
           v                    v
    use subscription     use ANTHROPIC_API_KEY
    (free)               (pay per token)


  Config supports multiple subscriptions:

  "claude_oauth_tokens": [
    "sk-token-george-account",
    "sk-token-company-account"
  ]

  Two subscriptions = double the rate limit pool.
  Token rotation per-request, not per-worker.
```

- **Q:** subscription or API?
- **Options:** (a) always API, (b) always subscription, (c) subscription first, API fallback
- **Chose:** test tokens per-request. All rate limited? Fall back to API.
- **Why:** subscriptions are already paid for. Testing costs ~nothing. API money only when genuinely needed.
- **Cascade:** token array supports pooling. Rotation is per-request to avoid concurrent env var mutation.

---

## Decision 20: AFK mode — large requests always use API

> You thought: auto-switch to API mid-execution.
> But actually: two modes — ≤100 = subscription (user watches), >100 = API (user walks away).

```text
AUTO-FALLBACK (rejected):

  Worker 1: processing with subscription token
  Worker 2: processing with subscription token
  ...
  Worker 5: RATE LIMITED
    --> switch to API key mid-run?
    --> env var is process-global
    --> Worker 1 picks up API key too?
    --> Which workers use which auth?
    --> What if Worker 3 was mid-request?

  Complex. Race conditions. Partial billing confusion.


TWO MODES (chosen):

  +----------------------------+    +----------------------------+
  | INTERACTIVE (<=100)        |    | AFK (>100)                 |
  |                            |    |                            |
  | Auth: subscription token   |    | Auth: always API key       |
  | User: watching             |    | User: gone, comes back     |
  | Cost: free                 |    | Cost: $X.XX shown upfront  |
  | Rate limited mid-run?      |    | Rate limited?              |
  |   --> task ends            |    |   --> shouldn't happen     |
  |   --> "X/Y completed"      |    |                            |
  |   --> user decides:        |    | UI shows:                  |
  |       resume / download /  |    |   estimated cost           |
  |       tick "use API"       |    |   estimated time           |
  +----------------------------+    +----------------------------+

  User submits 50 companies:
    --> subscription. Free. If rate limited, resume later.

  User submits 500 companies:
    --> API. $1.50. Walk away. Come back tomorrow.

  Threshold (100) is configurable.
```

- **Q:** subscription can get rate limited mid-run. For 2000 companies, what happens?
- **Options:** (a) auto-fallback during execution, (b) interactive/AFK split
- **Chose:** two modes. Interactive = subscription + user watches. AFK = API + user walks away.
- **Why:** mid-execution switching is complex. Two modes: interactive is simple (task ends if rate limited), AFK is simple (API, no limits). No auto-fallback.
- **Cascade:** UI shows different flows per mode. Threshold is configurable.

---

## Decision 21: Multi-user — independent jobs, global worker cap

> You thought: queue users — one job at a time.
> But actually: per-file DuckDB = independent jobs. Cap workers globally, not jobs.

```text
QUEUE (rejected):

  George: POST /kick-off  --> RUNNING
  Sam:    POST /kick-off  --> 409 "A job is already running"
  Sam:    waits...
  Sam:    waits...
  George: done.
  Sam:    POST /kick-off  --> RUNNING

  Unacceptable. Sam has work to do.


INDEPENDENT JOBS (chosen):

  George: POST /kick-off  --> request_id: 20260402_100000
  Sam:    POST /kick-off  --> request_id: 20260402_100005

  Each gets its own:
  +--------------------------------------------+
  |  runs/__server/rtic_qa_tool/               |
  |                                            |
  |  20260402_100000/          <-- George      |
  |    results.duckdb          <-- own DB      |
  |    instance_workspace_*/   <-- own workers |
  |                                            |
  |  20260402_100005/          <-- Sam         |
  |    results.duckdb          <-- own DB      |
  |    instance_workspace_*/   <-- own workers |
  +--------------------------------------------+

  DuckDB per-file locks:
    George's lock: only George's workers queue here
    Sam's lock:    only Sam's workers queue here
    Zero contention between them.

  Global cap:
    max_worker_count: 20 (shared)
    George uses 12 workers, Sam uses 8
    Total: 20. At capacity.
    Josh: "workers at capacity, job will queue"

  UI shows:
    +---------------------------+
    | Active workers: 20 / 20   |
    | George: 12 (RUNNING)      |
    | Sam: 8 (RUNNING)          |
    | Josh: queued              |
    +---------------------------+
```

- **Q:** 4 RTIC engineers, all using the tool. How to handle concurrent users?
- **Options:** (a) queue — one at a time, (b) independent jobs with shared worker pool
- **Chose:** each request gets its own DuckDB. Jobs are independent. Workers capped globally.
- **Why:** telling George to wait for Sam is unacceptable. Per-file locks mean zero contention.
- **Cascade:** UI needs a job list showing all active jobs and global worker count
