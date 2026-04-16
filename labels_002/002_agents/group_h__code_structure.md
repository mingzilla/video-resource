# H. Code Structure

- [25. Zero shared code between systems]
- [26. Three files, not five — don't over-split]

---

## The Problem

System 1 (generate rules) and system 2 (QA companies) started in the same
`service.py` file. They share a server, share a port, and both call `claude -p`.
The natural instinct: extract shared code into utilities.

But these systems do completely different things. System 1 is a single Claude
call. System 2 is a DuckDB-backed work queue with concurrent workers, DNS
pre-filtering, and crash recovery. What they "share" is one line of code.

```text
System 1:                          System 2:
  3 files in                         5 files in
  1 Claude call                      upfront validation
  1 result out                       DNS pre-filter
  ~100 lines of code                 DuckDB (4 tables)
                                     N concurrent workers
                                     claim/process/write loop
                                     pause/resume
                                     auth mode selection
                                     ~1000 lines of code

  "Shared": both call claude -p
  That's one line.
```

---

## Decision 25: Zero shared code between systems

> You thought: share run_claude_batch() between systems.
> But actually: they do different things. Duplicate a one-liner, don't create a dependency.

```text
SHARED UTILS (rejected):

  src/m001_qa_server/
    main.py
    service_system1.py  ---+
    service_system2.py  ---+--> imports shared.py
    shared.py               |
      run_claude_batch()    |
      Config base class     |
      default file helpers  |

  Problem 1: system 2 needs auth_env parameter on run_claude_batch.
             Add it? Now system 1's import has a parameter it never uses.

  Problem 2: system 2 adds verbose logging to run_claude_batch.
             Change shared.py? Does it break system 1's output parsing?

  Problem 3: reading shared.py — is this system 1 or system 2 logic?
             Both. Neither. It's in-between.

  Every change to shared.py requires checking BOTH systems.
  For a one-liner.


INDEPENDENT (chosen):

  src/m001_qa_server/
    main.py                  <-- thin routes, imports both
    service_system1.py       <-- own config, own claude call, own defaults
    service_system2.py       <-- own config, own claude call, own defaults
    duckdb_manager.py        <-- system 2 only

  System 1 has its own _run_claude():
    async def _run_claude(prompt, model, cwd, timeout, auth_env):
        proc = await asyncio.create_subprocess_exec(
            "claude", "-p", prompt, ...)

  System 2 has its own run_claude_batch():
    async def run_claude_batch(prompt, model, cwd, timeout, verbose, auth_env):
        proc = await asyncio.create_subprocess_exec(
            "claude", "-p", prompt, ...)

  Same? Almost. Different params (verbose). Different logging.
  Different error handling. Evolving independently.

  Change system 2? Don't even open system 1's file.
```

- **Q:** two systems on one server. Share code?
- **Options:** (a) shared utils, (b) completely independent service files
- **Chose:** zero shared business logic. Each owns its config, claude runner, defaults.
- **Why:** sharing `run_claude_batch()` creates a dependency between unrelated systems. Duplicating one line is cheaper than maintaining a shared abstraction.
- **Cascade:** two config files, two service files, one thin main.py

---

## Decision 26: Three files, not five

> You thought: main.py + service.py + models.py + config.py + runner.py.
> But actually: three files. Config and models are small — always needed in context.

```text
FIVE FILES (rejected):

  src/m001_qa_server/
    main.py              <-- routes
    service.py           <-- business logic
    models.py            <-- KickOffRequest, TestRequest
    config.py            <-- System2Config
    claude_runner.py     <-- build_batch_prompt, run_claude_batch

  Reading the kick-off flow:
    1. Open main.py      --> sees req: KickOffRequest
    2. Open models.py    --> what fields does KickOffRequest have?
    3. Back to main.py   --> calls service.kick_off()
    4. Open service.py   --> reads config values
    5. Open config.py    --> what's max_records_per_worker?
    6. Back to service.py --> calls build_batch_prompt()
    7. Open claude_runner.py --> how does it build the prompt?
    8. Back to service.py

  7 file switches to understand one flow.
  For AI: 5 files to read = 5 × token cost to load context.


THREE FILES (chosen):

  src/m001_qa_server/
    main.py              <-- thin routes (one-liners)
    service_system2.py   <-- EVERYTHING: config, models, orchestration
    duckdb_manager.py    <-- only because it has genuine encapsulation
                             (asyncio.Lock, connection lifecycle)

  Reading the kick-off flow:
    1. Open service_system2.py
    2. Read top to bottom
    3. Done.

  When does a file deserve extraction?
  +--------------------------------------------------+
  | Has internal state nobody else needs to see?     |
  | (DuckDB manager: lock, connection lifecycle)     |
  |                                                  |
  | YES --> extract                                  |
  | NO  --> keep in service file                     |
  +--------------------------------------------------+

  Config class: 10 lines, always needed      --> stays in service
  Pydantic models: 15 lines, always needed   --> stays in service
  Claude runner: part of the orchestration   --> stays in service
  DuckDB manager: own lock, own lifecycle    --> extracted
```

- **Q:** how many Python files per system?
- **Options:** (a) 5 files (main, service, models, config, runner), (b) 3 files (main, service, manager if encapsulated)
- **Chose:** three max. Extract only genuinely self-encapsulated units.
- **Why:** every split creates "where does this go?" for the next developer or Claude instance. Config/models are small and always needed. Orchestration is one story.
- **Cascade:** created `python_ai_coding_rules.md` ruleset for future projects
