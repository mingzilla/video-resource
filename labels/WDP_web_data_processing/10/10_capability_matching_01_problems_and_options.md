# Capability Matching

## Illustration of Problem

```text
                              +--------------+
                              |capabilities: |
                              |[             |
                              |  {
                              |    "tier1": "a", "tier2": "a1",, "tier3": [...], 
                              |    ...
                              |  }           |
                              |]             |
                              +--------------+
  10 million records                 |
          |                          v
  +---------------+           +--------------+         +----------+
  | webtext       |           | capabilities |         | matched  |
  | ~~            |           | - a          |         | - d      |
  | ~~            |           | - b          |  ====>  | - a      |
  |   capability  | --------> | - c          |         | - c      |
  | ~~~           |           | - d          |         |          |
  | ~~~~~         |           | - ...        |         |          |
  +---------------+           +--------------+         +----------+
```

---

## Potential Solutions

### Option 1 - Send ALL

```text
No Explanation - Bad
  +---------------+     +--------------+
  | webtext       |     | capabilities |
  | ~~            |     | - a          |
  | ~~            |  +  | - b          | + [prompt] ===> [LLM - Deepseek]
  |   capability  |     | - c          |
  | ~~~           |     | - d          |
  | ~~~~~         |     | - ...        |
  +---------------+     +--------------+

With Explanation - long, expensive
  +---------------+     +------------------+
  | webtext       |     | capabilities.csv |
  | ~~            |     | - a: ----        |
  | ~~            |  +  | - b: ----        | + [prompt] ===> [LLM - Deepseek]
  |   capability  |     | - c: ----        |
  | ~~~           |     | - d: ----        |
  | ~~~~~         |     | - ...            |
  +---------------+     +------------------+
```

Problem: tokens, slow, hard

---

### Option 2 - Extract + RAG

```text
                   +---------------+                    +--------------+         +----------+
 [Samples]|  ----> | webtext       |                    | capabilities |         | ranked   |
 ---------+        | ~~            |                    | - a: ----    |         | - d      |
                   | ~~            |                    | - b: ----    |  ====>  | - a      |
                   |   capability  | --> capability --> | - c: ----    |         | - c      |
                   | ~~~           | LLM           vss  | - d: ----    |         |          |
                   | ~~~~~         |                    | - ...        |         |          |
                   +---------------+                    +--------------+         +----------+

(1) samples        (2) extraction       (3) input       (4) taxonomy distinction
```

Result: not great
Problems: to be discussed

---

### Option 3 - Fine Tune Model

```text
                   +---------------+                +----------+
 [Samples]|  ----> | webtext       |                | matched  |
 ---------+        | ~~            |                | - d      |
                   | ~~            | --> [LLM] ===> | - a      |
                   |   capability  |   our model    | - c      |
                   | ~~~           |                |          |
                   | ~~~~~         |                |          |
                   +---------------+                +----------+
```

## Verification

```text
[webtext]      --+
[capabilities] --+   question: is it correct?
[prompt]       --+ ============================> [LLM] 
[result]       --+ 

- Try this with many good records
```
