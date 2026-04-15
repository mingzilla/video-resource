## Training LLM Models

1
Model training procedure:

```text
fineweb data + [model] => [base model]

[base model] + [QA] => [fine-tuned model]

[fine-tuned model v1] -> reinforcement -> [fine-tuned model v2]
```

2
Difference between base model and fine-tuned model:
e.g. what is 2+2?
- base model: "this is a maths task"
- fine-tuned model: "4"

3
- model input - tokens, not text 
- number of params - e.g. 1B - similar to a funnel with 1B sliders
- context window - input+output token count
- model - a funnel with sliders: it takes input tokens -> based on the sliders, decide the probability of the next token, sample the next token -> outputs the token
