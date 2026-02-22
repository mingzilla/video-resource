# Capability Matching

## Illustration of Problem

10 million records

```text
  +---------------+           +--------------+         +----------+
  | webtext       |           | capabilities |         | matched  |
  | ~~            |           | - a          |         | - d      |
  | ~~            |           | - b          |  ====>  | - a      |
  |   capability  | --------> | - c          |         | - c      |
  | ~~~           |           | - d          |         |          |
  | ~~~~~         |           | - ...        |         |          |
  +---------------+           +--------------+         +----------+
```

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
  +---------------+     +--------------+
  | webtext       |     | capabilities |
  | ~~            |     | - a: ----    |
  | ~~            |  +  | - b: ----    | + [prompt] ===> [LLM - Deepseek]
  |   capability  |     | - c: ----    |
  | ~~~           |     | - d: ----    |
  | ~~~~~         |     | - ...        |
  +---------------+     +--------------+
```

Problem: tokens, slow, hard

### Option 2 - Extract + RAG

```text
  +---------------+                    +--------------+         +----------+
  | webtext       |                    | capabilities |         | ranked   |
  | ~~            |                    | - a: ----    |         | - d      |
  | ~~            |                    | - b: ----    |  ====>  | - a      |
  |   capability  | --> capability --> | - c: ----    |         | - c      |
  | ~~~           | LLM           vss  | - d: ----    |         |          |
  | ~~~~~         |                    | - ...        |         |          |
  +---------------+                    +--------------+         +----------+

Problem: to be discussed
```

## Verification

```text
[webtext]      --+
[capabilities] --+   correct?
[prompt]       --+ ===========> [LLM] 
[result]       --+ 

- Try this with many good records
```
