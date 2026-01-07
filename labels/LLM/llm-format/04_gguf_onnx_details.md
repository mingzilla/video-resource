## C# Research Summary

### HuggingFace models, GGUF models, ONNX models

- HuggingFace models are created as the base
- HF models may be converted into GGUF models and/or ONNX models
- GGUF models are for llama.cpp - LlamaSharp uses this
- ONNX models are universal - Requires a runtime for different platforms (so model and runtime are just like Java jar and JRE)

### GGUF models

As what I showed you last time, it works, but it's slow because it can only embed items one by one
I have checked the source code (LLamaEmbedder). It doesn't seem to have a method that performs batch embedding.

https://github.com/SciSharp/LLamaSharp/issues/889

- This is a request to implement batch processing.
- It's closed as complete and this is implemented https://github.com/SciSharp/LLamaSharp/pull/902
- 902 says "This rewrite does not support batching, it's still just one string at a time."

This concludes that LlamaSharp is not likely the right tool to create a duckdb file with embedding for each company.

### ONNX models

I cannot get this to work with GPU. This is because:

- It requires cuda toolkit 12 and cuDNN 9 in order to be able to use GPU
- I have cuda toolkit 13 installed, and I cannot successfully uninstall it
- Note: run `nvidia-smi` to check CUDA version

Conclusion:

- since I can't downgrade cuda toolkit, I cannot successfully complete the proof of concept
- I feel nervous about taking this approach because it can easily have a "I works on my machine" issue