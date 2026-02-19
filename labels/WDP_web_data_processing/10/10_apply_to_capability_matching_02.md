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

## Solution 1 - Send ALL

```text
[webtext] + [capabilities] + [prompt] ===> [LLM - Deepseek]
```

Problem: tokens, slow, hard
