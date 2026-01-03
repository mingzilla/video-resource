## Tokenizers

**Tokenizer = Text <-> Numbers Converter**

```
[Tokenizer Role in Pipeline]
    |
    +-- ENCODING (text -> tokens -> numbers)
    |     |
    |     "Hello world" --> ["Hello", "Ġworld"] --> [15496, 1879] => Model input
    |           |        ↑ split                 ↑ map to numbers
    |           │
    |           └─ uses: tokenizer.json (rules + vocab); Ġ is space
    |
    +-- DECODING (numbers -> tokens -> text)
          |
          Model Output => [3492, 318] --> ["This", "Ġis"] --> "This is"
                                      ↑ map to tokens      ↑ join/clean

Encode:
- split: runs an algorithm to split text, this uses tokenizer.json
- map: converts tokens into numbers, this uses vocab.txt

Decode:
- map: converts numbers into tokens, this uses vocab.txt (reverse lookup)
- join: cleans and joins tokens into text, this uses tokenizer.json (decoder rules)
```

## **Tokenizer Components:**

```
[Tokenizer System]
    |
    +-- Algorithm (tokenizer.json)
    |     |
    |     +-- BPE (Byte-Pair Encoding)
    |     +-- WordPiece
    |     +-- SentencePiece
    |     +-- Unigram
    |
    +-- Vocabulary (vocab.txt or in tokenizer.json)
    |     |
    |     +-- List of all possible tokens
    |     +-- Mapping: token <-> ID
    |
    +-- Special Tokens
    |     |
    |     +-- [PAD], [UNK], [CLS], [SEP]
    |     +-- [BOS], [EOS] (begin/end of sequence)
    |
    +-- Config (tokenizer_config.json)
          |
          +-- Max length
          +-- Padding strategy
          +-- Truncation rules
```

## **Tokenizer in Different Formats:**

| Format          | Tokenizer Location                          | Notes                                    |
|-----------------|---------------------------------------------|------------------------------------------|
| **HuggingFace** | tokenizer.json + vocab.txt (separate files) | Loaded by transformers library           |
| **GGUF**        | Embedded in .gguf file (self-contained)     | llama.cpp embeds vocab during conversion |
| **ONNX**        | tokenizer.json + vocab.txt (separate files) | Must be distributed alongside model      |

## **GGUF Tokenizer Advantage:**

```
[GGUF File]
    |
    +-- Model Weights
    +-- Tokenizer Vocabulary (embedded)
    +-- Model Configuration
    |
    v
Single file = complete model + tokenizer
No separate tokenizer files needed!
This is why llama.cpp is so portable.
```

## **Example Flow:**

```
Input: "Hello world"
    |
    v
[Tokenizer.encode()]
    |
    +-- Lookup "Hello" in vocab --> ID: 15496
    +-- Lookup "world" in vocab --> ID: 1879
    |
    v
[15496, 1879]
    |
    v
[Model processes token IDs]
    |
    v
[Output embeddings or predictions]
```

### Example: **ONNX Structure:**

```
[ONNX Model Directory]
    |
    +-- tokenizer.json (tokenizer config)
    +-- vocab.txt (vocabulary file)
    |     |
    |     +-- token_id -> token_string mapping
    |     +-- e.g., 0: "[PAD]", 1: "[UNK]", 2: "the", ...
    |
    +-- config.json (model metadata)
    |
    +-- model.onnx (or model_quantized.onnx)
          |
          +-- Graph definition
          +-- Operators
          +-- Weights
```

### **vocab.txt File:**

```
[vocab.txt Purpose]
    |
    +-- Maps token IDs to text strings
    +-- Used during tokenization/detokenization
    +-- Format: one token per line (line number = token ID)
```

Example:

```text
[CLS]
[SEP]
[PAD]
[UNK]
[MASK]
the
of
and
to
in
...
```