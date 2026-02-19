# Extract RAG

## How it works, What can go wrong

```text
                   +---------------+                    +--------------+         +----------+
 [Samples]|  ----> | webtext       |                    | capabilities |         | ranked   |
 ---------+        | ~~            |                    | - a          |         | - d      |
                   | ~~            |                    | - b          |  ====>  | - a      |
                   |   capability  | --> capability --> | - c          |         | - c      |
                   | ~~~           | LLM           vss  | - d          |         |          |
                   | ~~~~~         |                    | - ...        |         |          |
                   +---------------+                    +--------------+         +----------+

(1) samples        (2) extraction       (3) input       (4) taxonomy distinction
```

## Have I done it well or not?

### Sample Selection

```text
this is the requirement ---> find me 10 records ---> that SHOULD have results
```

[001__sample_data_for_vss.md](docs/001__sample_data_for_vss.md)

### Extraction

To discuss later

### Input

Try:

- capabilities
- product + capabilities
- full summary

### Taxonomy Distinction

```text
[json] -> [gen_text.csv] -> [capabilities.duckdb] -> [embeddings.duckdb]

[capabilities.json] <------- [dirty capabilities.json]
      |-- output: cleaned structure
      |
[capabilities.csv] <-------- [powerful online LLM] - Claude and Kimi, not ChatGPT
      |-- output: capability explanation
      |
[capabilities.duckdb]
      |-- output: capability explanation
      |
[capabilities_nomic_embedding__64d.duckdb] <----- [nomic-embed-text1.5]
      |-- output: embeddings
      |
    [END]
```

```text
[summary generation] --------> [LLM verify distinction]
- give it to claude            - what's not good
- generate descriptions        - re-gen
- make sure distinct
```

## Remaining Problems

- What does `capabilities` even mean? ---- Note: cannot provide examples for small models
- Taxonomy can be terrible or irrelevant
