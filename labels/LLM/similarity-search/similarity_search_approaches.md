## cosine_similarity and inner_product

What's the difference between cosine_similarity and inner_product?

- normalization
- performance
- truncation

## Normalized Vectors Explained

A vector is **normalized** when its magnitude (length) equals 1.

### Visual Representation

```
2D Space (easier to visualize):

         Y
         │
         │  [0.6, 0.8]  ← normalized (magnitude = 1)
         │    /
         │   /
         │  / length = 1
         │ /
         │/__________ X
         
         
         Y
         │
         │  [3, 4]  ← NOT normalized (magnitude = 5)
         │    /
         │   /
         │  / length = 5
         │ /
         │/__________ X
```

### How to Normalize

```
Original Vector:    [3, 4, 0]
Magnitude:          5

Normalized Vector:  [3/5, 4/5, 0/5] = [0.6, 0.8, 0]

Check:
magnitude = √(0.6² + 0.8² + 0²) 
          = √(0.36 + 0.64 + 0) 
          = √1 
          = 1  ✓
```

**Key Insight**: If all vectors have magnitude = 1, then `inner_product` and `cosine_similarity` produce identical rankings (but different absolute values).

```text
┌───────────────┬────────────────────────────────────┬─────────────────────────────────────────────┐
│ Feature       │ array_inner_product (Dot Product)  │ array_cosine_similarity (Cosine Similarity) │
├───────────────┼────────────────────────────────────┼─────────────────────────────────────────────┤
│ Calculation   │ A * B                              │ (A * B) / (||A|| * ||B||)                   │
│ Range         │ Unbounded                          │ -1 to 1                                     │
│ Measures      │ A mix of orientation and magnitude │ Purely orientation (direction)              │
│ Sensitive to? │ Vector Magnitude                   │ No                                          │
└───────────────┴────────────────────────────────────┴─────────────────────────────────────────────┘
```

---

## array_cosine_similarity and array_inner_product comparison

- Q: Is it right to say, regardless if we use array_cosine_similarity or array_inner_product, the ranking order is the same?
    - A: Almost, but NO - not always - based on calculation
- Q: Is it right to say that array_cosine_similarity is slower but safe?
    - A: YES

---

## Truncation

```text
when i use nomic-embed-text-v1_5 to do embedding, the returned float[] is 768d, if i only keep 128d and lose a little bit of precision, then basically i need to use array_cosine_similarity, right?
```

**YES, absolutely correct!**

When you truncate dimensions, you're changing the vector magnitudes, so you **must** use `ARRAY_COSINE_SIMILARITY`.

### Why Truncation Breaks Normalization

```
Original 768d vector (normalized):
[0.1, 0.2, 0.3, ..., 0.05]  (768 values)
magnitude = 1.0  ✓

Truncated 128d vector:
[0.1, 0.2, 0.3, ..., 0.05]  (only first 128 values)
magnitude = 0.6  ✗  NOT normalized anymore!
```

### Search Based on Truncated Data

For simplicity, use `array_cosine_similarity`. We cannot just normalize the query, because all records from the db are truncated.

```text
Database Records (ALL truncated to 128d):
├─→ Record 1: [0.1, 0.2, ...]  128 values, magnitude ≈ 0.6
├─→ Record 2: [0.3, 0.4, ...]  128 values, magnitude ≈ 0.7
└─→ Record 3: [0.5, 0.1, ...]  128 values, magnitude ≈ 0.5

Query Input (also truncated to 128d):
└─→ [0.2, 0.3, ...]  128 values, magnitude ≈ 0.6

Result: ALL vectors are unnormalized
└─→ MUST use ARRAY_COSINE_SIMILARITY
```