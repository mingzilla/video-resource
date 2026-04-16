# G. Making It Usable

- [22. Test endpoint — same pipeline, synchronous]
- [23. Server defaults — avoid uploading the same files repeatedly]
- [24. Naming things for humans — batch_size → max_records_per_worker]

---

## The Problem

The system works. Workers process companies, DuckDB tracks state, results
come back. But the people using it aren't engineers. Alex is refining prompts.
George is QA-ing FinRegTech. Sam is working on Defence. They don't care
about async job lifecycles or config internals. They need:

- Quick feedback when testing prompt changes
- Minimal file uploads per request
- Config they can read without a README

```text
Alex's workflow:

  1. Edit prompt
  2. Test on 2 companies
  3. Check results
  4. Edit prompt again
  5. Test on 2 companies
  6. ...repeat 20 times...
  7. Happy? Run 500 companies overnight.

  Steps 2-3 need to be FAST.
  If each test requires: kick-off → poll → poll → poll → results
  that's 5 HTTP calls and 30 seconds of polling friction.
  × 20 iterations = 10 minutes wasted on plumbing.


George's workflow:

  1. Upload taxonomy, specific rules, companies CSV
  2. Also upload general rules and prompt (same as last time)
  3. Also upload general rules and prompt (same as last time)
  4. Also upload general rules and prompt (same as last time)
  5. Upload the WRONG general rules file
  6. Get confused about which file is which
```

---

## Decision 22: Test endpoint — same pipeline, synchronous

> You thought: test by running kick-off + polling in a script.
> But actually: /test = same pipeline, synchronous. One call, one result. Same code path.

```text
KICK-OFF + POLL (rejected for testing):

  Alex edits prompt.

  POST /kick-off  --> {request_id: "20260402_100000"}
  POST /check-progress?request_id=20260402_100000  --> {status: RUNNING}
  ...wait 5 seconds...
  POST /check-progress?request_id=20260402_100000  --> {status: RUNNING}
  ...wait 5 seconds...
  POST /check-progress?request_id=20260402_100000  --> {status: DONE}
  GET /results?request_id=20260402_100000  --> {csv: "..."}

  5 HTTP calls. 10+ seconds of polling. For 1 company.
  × 20 prompt iterations = painful.


/TEST (chosen):

  Alex edits prompt.

  POST /test {count: 1}  --> {csv: "Company_Number,Verdict,...\n09688671,Valid,..."}

  1 HTTP call. Same pipeline:
    upfront validation --> DNS pre-filter --> worker --> result

  Same code:
    kick_off calls: _setup_job() --> create_task(_start_processing())
    test calls:     _setup_job() --> await _start_processing()
                                     ^^^^^
                                     one word different

  Want to test concurrent workers?
    POST /test {count: 2, instances: 2}
    --> 2 workers, each processes 1 company
    --> tests concurrency through the real pipeline
```

- **Q:** how do you test the async flow?
- **Options:** (a) kick-off + poll loop, (b) dedicated /test endpoint
- **Chose:** /test — same pipeline, synchronous. One call, one result.
- **Why:** prompt tuning needs fast iteration. No polling friction. If /test works, /kick-off works — same code.
- **Cascade:** accepts `count` and `instances` params for concurrent testing

---

## Decision 23: Server defaults — stop uploading the same files

> You thought: upload 5 files every time.
> But actually: P1 and P2 rarely change. Server defaults — users upload only 3 files.

```text
EVERY TIME (rejected):

  Request requires:
  +--------------------+--------------------------------------------+
  | taxonomy.md        | changes per vertical          (REQUIRED)   |
  | specific_rules.md  | changes per vertical          (REQUIRED)   |
  | companies.csv      | changes per request           (REQUIRED)   |
  | general_rules.md   | same for months               (REQUIRED)   |
  | prompt.md          | same for months               (REQUIRED)   |
  +--------------------+--------------------------------------------+

  George uploads 5 files.
  George uploads 5 files again. Same general rules. Same prompt.
  George uploads 5 files. Accidentally uses old general rules.
  George uploads 5 files. Puts the prompt in the general rules box.
  George gives up.


SERVER DEFAULTS (chosen):

  First time:
    Upload all 5 files. Server validates. Saves P1 + P2 as defaults.

  Every time after:
  +--------------------+--------------------------------------------+
  | taxonomy.md        | changes per vertical          (REQUIRED)   |
  | specific_rules.md  | changes per vertical          (REQUIRED)   |
  | companies.csv      | changes per request           (REQUIRED)   |
  | general_rules.md   | "using server default"        (OPTIONAL)   |
  | prompt.md          | "using server default"        (OPTIONAL)   |
  +--------------------+--------------------------------------------+

  George uploads 3 files. Done.

  If Alex updates the prompt:
    1. Upload new prompt in the optional box
    2. Server validates
    3. Server saves as new default
    4. Everyone gets the updated prompt automatically

  GET /defaults --> {"general_rules": true, "prompt": true}
  UI shows: "using server default" on optional fields
```

- **Q:** users confuse general rules, specific rules, and prompt. Wrong files uploaded constantly.
- **Options:** (a) 5 required uploads, (b) server-side defaults for stable files
- **Chose:** P1 and P2 stored as server defaults. 3 required uploads per request.
- **Why:** P1 and P2 rarely change. Default removes the most confusing uploads. Re-upload overwrites after validation.
- **Cascade:** GET /defaults endpoint. First time requires all 5.

---

## Decision 24: Naming things for humans

> You thought: batch_size: 40 — is that max or default?
> But actually: max_records_per_worker: 40. The name IS the documentation.

```text
BEFORE:

  run_system2.json:
  {
    "batch_size": 40,          <-- max? default? per what?
    "max_concurrent": 3,       <-- 3 what? batches? workers? jobs?
    "max_companies": 500       <-- this one is ok actually
  }

  Alex: "what's batch_size?"
  Ming: "companies per Claude invocation"
  Alex: "is that the max or the default?"
  Ming: "...the max. default is 20. that's not in the config."
  Alex: "where's the default?"
  Ming: "hardcoded."


AFTER:

  run_system2.json:
  {
    "max_records_per_worker": 40,       <-- max, per worker. obvious.
    "default_records_per_worker": 10,   <-- default. obvious.
    "max_worker_count": 20,             <-- max workers. obvious.
    "default_worker_count": 3,          <-- default. obvious.
    "max_companies": 500
  }

  User can override defaults (capped at max):

  POST /kick-off {
    records_per_worker: 20,    <-- "I want 20 per worker" (capped at 40)
    worker_count: 5            <-- "I want 5 workers" (capped at 20)
  }

  The names ARE the documentation.
  No README needed for the config file.
```

- **Q:** config names mean nothing to users
- **Options:** (a) keep technical names + document, (b) rename to what they mean
- **Chose:** `max_records_per_worker`, `default_records_per_worker`, `max_worker_count`, `default_worker_count`
- **Why:** "batch_size: 40" is ambiguous. "max_records_per_worker: 40" is self-documenting. Naming clarified the architecture: records belong to workers, not abstract "batches."
