## Prompt and Model

```text
                   +---------------+
 [Samples]|  ----> | webtext       |
 ---------+        | ~~            |
                   | ~~            |
                   |   capability  | + [prompt_template.md] --> capability
                   | ~~~           |                        LLM
                   | ~~~~~         |
                   +---------------+
```

| Aspect                  | Qwen 14b        | Qwen 32b     | Llama 3.2:3b |
|-------------------------|-----------------|--------------|--------------|
| **Speed**               | Faster          | Slower       | Fastest      |
| **Format compliance**   | Good            | Better       | Poor         |
| **Category separation** | Mixed           | Better       | Poor         |
| **Inference control**   | Some leakage    | Less leakage | High leakage |
| **Summary quality**     | Good            | Good         | Mixed        |
| **Overall**             | ⚠️ **Marginal** | ✅ **Best**   | ❌ **Avoid**  |


## Reasons and Options

Cost: HTTP, Hire, Local

