# Training and Packging Output and What They Mean

## Training

### Output

```shell
/mnt/e/code/github-release/mvp$ work/llm_fine_tuning/scripts_sh/ex_001__train/run.sh
🦥 Unsloth: Will patch your computer to enable 2x faster free finetuning.
🦥 Unsloth Zoo will now patch everything to make training faster!
==((====))==  Unsloth 2026.3.4: Fast Llama patching. Transformers: 5.2.0.
   \\   /|    NVIDIA GeForce RTX 5090 Laptop GPU. Num GPUs = 1. Max memory: 23.889 GB. Platform: Linux.
O^O/ \_/ \    Torch: 2.10.0+cu128. CUDA: 12.0. CUDA Toolkit: 12.8. Triton: 3.6.0
\        /    Bfloat16 = TRUE. FA [Xformers = 0.0.35. FA2 = False]
 "-____-"     Free license: http://github.com/unslothai/unsloth
Unsloth: Fast downloading is enabled - ignore downloading bars which are red colored!
Loading weights: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 254/254 [00:01<00:00, 162.73it/s, Materializing param=model.norm.weight]
Unsloth: Will load unsloth/llama-3.2-3b-instruct-unsloth-bnb-4bit as a legacy tokenizer.
Unsloth 2026.3.4 patched 28 layers with 28 QKV layers, 28 O layers and 28 MLP layers.
Map: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 9/9 [00:00<00:00, 668.50 examples/s]
num_proc must be <= 9. Reducing num_proc to 9 for dataset of size 9.
[datasets.arrow_dataset|WARNING]num_proc must be <= 9. Reducing num_proc to 9 for dataset of size 9.
Unsloth: Tokenizing ["text"] (num_proc=9): 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 9/9 [00:02<00:00,  3.47 examples/s]
🦥 Unsloth: Padding-free auto-enabled, enabling faster training.
==((====))==  Unsloth - 2x faster free finetuning | Num GPUs used = 1
   \\   /|    Num examples = 9 | Num Epochs = 3 | Total steps = 6
O^O/ \_/ \    Batch size per device = 2 | Gradient accumulation steps = 4
\        /    Data Parallel GPUs = 1 | Total batch size (2 x 4 x 1) = 8
 "-____-"     Trainable parameters = 24,313,856 of 3,237,063,680 (0.75% trained)
{'loss': '2.659', 'grad_norm': '0.247', 'learning_rate': '0', 'epoch': '0.8'}
{'loss': '2.625', 'grad_norm': '0.3467', 'learning_rate': '4e-05', 'epoch': '1'}
{'loss': '2.657', 'grad_norm': '0.2615', 'learning_rate': '8e-05', 'epoch': '1.8'}
{'loss': '2.619', 'grad_norm': '0.2544', 'learning_rate': '0.00012', 'epoch': '2'}
{'loss': '2.631', 'grad_norm': '0.2939', 'learning_rate': '0.00016', 'epoch': '2.8'}
{'loss': '2.551', 'grad_norm': '0.3448', 'learning_rate': '0.0002', 'epoch': '3'}
{'train_runtime': '77.88', 'train_samples_per_second': '0.347', 'train_steps_per_second': '0.077', 'train_loss': '2.624', 'epoch': '3'}
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 6/6 [01:17<00:00, 12.98s/it]
```

### What happens during training

- Base model loaded in 4-bit quantisation (~3.2B params, ~2GB VRAM)
- LoRA applied — only **24M params trained (0.75%)**, the rest frozen
- 9 records × 3 epochs = 6 gradient steps (proof-of-concept run)
- Total time: ~77 seconds on RTX 5090

### Loss numbers (9-record test run)

```
epoch 1:  2.659 → 2.625
epoch 2:  2.657 → 2.619
epoch 3:  2.631 → 2.551  ← slight downward trend
```

| Loss range      | Meaning                                              |
|-----------------|------------------------------------------------------|
| ~2.6 (this run) | Model barely learning — expected with only 9 records |
| ~1.0–1.5        | Model starting to learn the pattern reliably         |
| < 1.0           | Good convergence — target for production training    |

Loss going down is the right direction. With 9 records there is almost no signal — the values will look very different with 1000 clean records. If loss does not decrease at all after 1000 records, the learning rate or LoRA rank likely needs tuning.

---

## Packaging

### Output

```shell
/mnt/e/code/github-release/mvp$ work/llm_fine_tuning/scripts_sh/ex_002__register_ollama/run.sh
2026-03-17 03:44:39,120 - __main__ - INFO - Found GGUF: /mnt/e/code/github-release/mvp/work/llm_fine_tuning/_output/ex_001__train/gguf_gguf/llama-3.2-3b-instruct.Q4_K_M.gguf
2026-03-17 03:44:39,120 - __main__ - INFO - $ /usr/bin/docker cp /mnt/e/code/github-release/mvp/work/llm_fine_tuning/_output/ex_001__train/gguf_gguf/llama-3.2-3b-instruct.Q4_K_M.gguf ollama-test:/tmp/llama-3.2-3b-instruct.Q4_K_M.gguf
Successfully copied 2.02GB to ollama-test:/tmp/llama-3.2-3b-instruct.Q4_K_M.gguf
2026-03-17 03:44:49,256 - __main__ - INFO - $ /usr/bin/docker cp /tmp/tmp8n72n9n9_Modelfile ollama-test:/tmp/Modelfile
Successfully copied 2.05kB to ollama-test:/tmp/Modelfile
2026-03-17 03:44:49,282 - __main__ - INFO - $ /usr/bin/docker exec ollama-test ollama create company-extractor:llama3.2-3b-v01 -f /tmp/Modelfile
gathering model components
copying file sha256:bd61246cdbd178c9caf15612a9bc2fc94e4e307841c1bb39d900b0990113270e 100%
parsing GGUF
using existing layer sha256:bd61246cdbd178c9caf15612a9bc2fc94e4e307841c1bb39d900b0990113270e
creating new layer sha256:4ebb2cc89ae63fb4bc8b37037f67b069f5ace79bb74e94f350b65ff57a857d43
writing manifest
success
2026-03-17 03:44:51,968 - __main__ - INFO - Done. Model 'company-extractor:llama3.2-3b-v01' is now available in ollama.
2026-03-17 03:44:51,968 - __main__ - INFO - Test with: docker exec ollama-test ollama run company-extractor:llama3.2-3b-v01
```

### What happens during packaging

- GGUF file (~2GB) copied into the ollama container at `/tmp/`
- Modelfile (containing `FROM` path + system prompt) copied into container
- `ollama create` runs inside the container — what it does line by line:

| Line                                  | Meaning                                                                                      |
|---------------------------------------|----------------------------------------------------------------------------------------------|
| `gathering model components`          | ollama reading the Modelfile and locating the GGUF                                           |
| `copying file sha256:bd61...`         | importing the GGUF weights into ollama's internal blob store                                 |
| `parsing GGUF`                        | ollama reading model metadata (architecture, vocab, context length) from the file            |
| `using existing layer sha256:bd61...` | weights blob already stored — not duplicated                                                 |
| `creating new layer sha256:4ebb...`   | new layer created for the system prompt (the only thing unique to this model)                |
| `writing manifest`                    | writing the model registry entry that maps `company-extractor:llama3.2-3b-v01` to its layers |
| `success`                             | model is registered and ready                                                                |

The GGUF is not stored twice — ollama uses content-addressed blobs (by sha256 hash). If you register a second model from the same GGUF, it reuses the existing blob and only creates a new manifest. Storage cost of re-registering is negligible.