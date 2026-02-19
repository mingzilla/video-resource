# Capability Matching

## Illustration of Problem

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

### Solution 1 - Send ALL

```text
[webtext] + [capabilities] + [prompt] ===> [LLM - Deepseek]
```

Problem: tokens, slow, hard

### Solution 2 - Extract + RAG

```text
  +---------------+                    +--------------+         +----------+
  | webtext       |                    | capabilities |         | ranked   |
  | ~~            |                    | - a          |         | - d      |
  | ~~            |                    | - b          |  ====>  | - a      |
  |   capability  | --> capability --> | - c          |         | - c      |
  | ~~~           | LLM           vss  | - d          |         |          |
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
