## Record Too Long

```text
 source data                     clean data                 relevant data
 +------------------+            +----------+      200k     +------+
 |------------------| -> code -> |----------|  ->  LLM  ->  |------|
 |------------------|            |----------|               |------|
 +------------------+            +----------+               +------+
```

## Ultimate Solution

```text
 prompt
 +--------------------+
 | path + instruction |
 +--------------------+
                 |
 +------+        v            +------+
 |------|  ->  claude -p  ->  |------|
 |------|                     +------+
 |------|                     desired data
 |------|
 |------|
 |------|
 |------|
 +------+
 source data 500
```

Instruction:

- db path
- data trust tier, quality tier
- output schema