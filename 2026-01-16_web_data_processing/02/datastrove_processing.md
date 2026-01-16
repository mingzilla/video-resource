## FineWeb pipeline:

https://github.com/huggingface/datatrove/blob/main/examples/fineweb.py

### Uses

- GopherRepetitionFilter
- GopherQualityFilter
- C4QualityFilter
- FineWebQualityFilter

### Steps

1. **Raw Web Crawl** (Noisy, contains everything)
2. **→ Gopher Repetition Filter** (Removes obvious junk with repeating chars/words)
3. **→ Gopher Quality Filter** (Removes other low-quality documents based on stats)
4. **→ C4 Quality Filter** (Removes non-prose, boilerplate, non-natural language)
5. **→ FineWeb Filter** (Final, custom polish)
6. **→ Result**: A clean, prose-heavy corpus suitable for LLM training.

### Gopher Filter

- Gopher: the term comes from DeepMind's Gopher paper
- rejects: documents that are too short, have too many symbols, or consist mainly of lists or error messages

### C4 Filter - Colossal Clean Crawled Corpus

- C4: the term comes from Google's C4 dataset

| What it Rejects                                            | Example / Reason                                                                                                                               |
|:-----------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------|
| **Paragraphs without a closing punctuation mark**          | Sentences that don't end with `.`, `!`, or `?`. This filters out list fragments, headers, or broken text.                                      |
| **Lines containing "lorem ipsum" placeholder text**        | Common web design boilerplate.                                                                                                                 |
| **Lines that look like JavaScript code or error messages** | Contain `{`, `}`, `function()`, stack traces, etc.                                                                                             |
| **Lines with specific "bad words"**                        | The original list includes offensive words to filter unsavory content.                                                                         |
| **Pages with a high density of suspicious phrases**        | Phrases like "cookie policy", "terms of service", "please enable JavaScript" which indicate navigation menus or boilerplate, not main content. |
| **Non-English sentences**                                  | Using a language detection model.                                                                                                              |

---

## n-grams

```
Example Text:
"""
Welcome to our homepage. We offer great products.
Home Products About Us Contact Privacy Policy
Check out our new collection. Special discounts today.
Home Products About Us Contact Privacy Policy
Visit our store for more details.
Home Products About Us Contact Privacy Policy


Welcome to our homepage
        to our homepage We
           our homepage We offer
"""

So if we have 30 words in total, threshold is 3,
- it creates an array of `10 words`, 21 items -> does something similar to `creates Dict<string_text, num_count>` -> if num_count > 3 -> remove related text
- then it creates an array of `9 words`, 22 items -> does something similar to `creates Dict<string_text, num_count>` -> if num_count > 3 -> remove related text
- then it creates an array of `8 words`, 23 items -> does something similar to `creates Dict<string_text, num_count>` -> if num_count > 3 -> remove related text
```

Does n-gram represent:

- the 20 sequential arrays?
- the 20 sentences (join an array to get a sentence) ?
- the approach that uses n=10 to create sequential arrays to check repeated text?

When you say "use 10-grams to deduplicate paragraphs", you mean you use this approach to dedupe.

## "10-gram decontamination"

https://github.com/huggingface/datatrove/blob/main/src/datatrove/pipeline/decont/n_grams.py

This does not mean dedupe, it means using 10-gram to make sure data does not overfit models.
Overfit means the data results in a model memorises an answer.

---

## banned words

https://github.com/huggingface/datatrove/blob/main/src/datatrove/assets/soft_banned_words.txt

