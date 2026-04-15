# Understanding LLM Training

## Questions

1. Q1: How many R's does the word strawberry have?
    - Why is this a very difficult task?
2. Q2: Which answer for "3 * (3 + 2) = ?" is better?
    - A: The result is 15. First, 3 + 2 = 5. Then, 3 * 5 = 15
    - B: First, 3 + 2 = 5. Then, 3 * 5 = 15. So the result is 15
3. Q3: Why did models say they were from OpenAI?
4. Q4: How can we train a model to do tool calls?
5. Q5: Semantic vs Mathematical

## Influence: Token-by-Token Generation Process

```text
     Input Tokens: [An] [apple] [a] [day]
                      |
                      v
        +------------------------+
        |                        |
        |-(w: 0.72)----O---------| <-- Parameter "Slider" 1
        |........................| <-- Layer of computation
        |                        |
        |  --------O--(w: -1.21)-| <-- Parameter "Slider" 2
        |........................| <-- Layer of computation
        |                        |
        |  -----O--(w: 0.98)-----| <-- <-- ... (and ~1 billion more)
        |........................| <-- Layer of computation
                      |                                    
                      v                                    
        Probability Distribution for Next Token            
+----------------------------------------------------------+    
| a: 0.01 | ... | is: 0.1 | keeps: 0.8 | ... | zulu: 0.001 |
+----------------------------------------------------------+    
                      |                                    
                      v                                    
           Sampled Output Token: [keeps]
```

| Step | Input Tokens (equivalent of text below)   | Model Action 1: Calculates probabilities             | Model Action 2: Sampling      | Output Token | Full Sequence So Far                   |
|------|-------------------------------------------|------------------------------------------------------|-------------------------------|--------------|----------------------------------------|
| 1    | `[An, apple, a, day]`                     | `keeps`(72%), `helps`(15%), `tastes`(8%), others(5%) | **Samples**: selects `keeps`  | `keeps`      | "An apple a day keeps"                 |
| 2    | `[An, apple, a, day, keeps]`              | `the`(68%), `my`(12%), `you`(9%), others(11%)        | **Samples**: selects `the`    | `the`        | "An apple a day keeps the"             |
| 3    | `[An, apple, a, day, keeps, the]`         | `doctor`(81%), `dentist`(7%), `wolf`(5%), others(7%) | **Samples**: selects `doctor` | `doctor`     | "An apple a day keeps the doctor"      |
| 4    | `[An, apple, a, day, keeps, the, doctor]` | `away`(88%), `busy`(4%), `healthy`(3%), others(5%)   | **Samples**: selects `away`   | `away`       | "An apple a day keeps the doctor away" |

**Sampling Methods:**

- **Greedy**: Always pick highest probability (deterministic)
- **Temperature sampling**: Control randomness (lower = more deterministic)
- **Top-k/top-p**: Limit choices to most probable tokens

## Model Training Procedure

High-level summary of how modern instruction-following models are created. Here are the industry-standard names and details for those stages:

| # | Stage                                                      | Process                                                   | Output                  | Purpose & Description                                                                                                                                                                                                                                           |
|---|------------------------------------------------------------|-----------------------------------------------------------|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | **Pre-training**                                           | `[fineweb data] + [model] =>`                             | `[base model]`          | **Builds general world knowledge and language competency.** The model learns grammar, facts, reasoning abilities, and coding skills by predicting the next token on a massive, diverse dataset from the internet and books.                                     |
| 2 | **Supervised Fine-Tuning (SFT) - General/Verifiable/Tool** | `[General QA] 70% + [Tool-call QA] 30% + [base model] =>` | `[fine-tuned model v1]` | **Teaches the model to be a helpful assistant AND use tools.** Trains on mixed datasets: (1) General instruction-following for unverifiable tasks, (2) Tool-call examples for verifiable tasks. The model learns when to answer directly vs. when to use tools. |
| 3 | **Reinforcement Learning (RLHF - human feedback)**         | `[fine-tuned model v1] -> reinforcement =>`               | `[fine-tuned model v2]` | **Final alignment for helpfulness and safety.** Uses reinforcement learning with a reward model (trained on human preferences) to make the model's responses more helpful, harmless, and aligned with nuanced human values.                                     |

### Tool calls

- To add tool call ability, do step 2, include `[General QA] + [Tool-call QA]`, so that model knows some tasks call tools and some don't
- Example tool call dataset

```text
Prompt: "What is 2+2?"
Response: "<calculator>2+2</calculator>"

Prompt: "Weather in Paris?"
Response: "<weather_api>Paris</weather_api>"
```

## Core Concepts

### Difference Between Base Model and Fine-Tuned Model

|                  | What it is                  | Potential Answer for "What is 2+2?" | Goal of influences - Decides most likely next token |
|------------------|-----------------------------|-------------------------------------|-----------------------------------------------------|
| Base Model       | Completion Engine           | this is a maths task                | Based on Internet web text knowledge                |
| Fine-Tuned Model | Instruction-Following Agent | 4                                   | Based on fine-tuned preference                      |

### Terminologies

| Concept                  | Analogy                                                                                                               |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------|
| **Model Input**          | Tokens, not text                                                                                                      |
| **Number of Parameters** | e.g., 1B parameters - similar to a funnel with 1B sliders                                                             |
| **Context Window**       | Input + output token count                                                                                            |
| **Model Function**       | A funnel with sliders: Takes input tokens -> decides probability of next token -> samples next token -> outputs token |
