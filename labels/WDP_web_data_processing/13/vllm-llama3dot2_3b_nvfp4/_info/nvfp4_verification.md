# NVFP4 Verification Guide

## Making use of NVFP4

**Requirement**

```text
+---------------------------+
|  Blackwell GPU            |
|  [vLLM]----[nvfp4-model]  |
+---------------------------+
```

**When:**
Use this when you need to confirm FP4 is active. Typically needed when

- vLLM upgrade
- model change
- or hardware change

**What this does:**

The script does not emit a pass/fail verdict. You read the kernel table it produces and
look for specific entries explained below. This is intentional: kernel names can change
between CUTLASS/vLLM versions, and a name-matching script would give false negatives
silently. The table gives you the ground truth; this doc tells you what it means.

---

## Commands

### Quick verification — ~2 min (start here)

```bash
./run_cmd.sh check-fp4-kernels
```

Stops vLLM, runs one inference under Nsight Systems, prints the CUDA kernel table,
restarts vLLM. Nsys is installed inside the container automatically if not present.
See the **Read the output** section below for what to look for.

#### Clean Verification

```shell
docker compose down
docker compose up -d
# wait until docker desktop to show that the container is green and healthy, then
./run_cmd.sh check-fp4-kernels
```

## Read the output

You will see a table like this (truncated for readability):

```
 Time (%)  Total Time (ns)  Instances  ...  Name
 --------  ---------------  ---------  ...  ----
     27.6        165035521        112   ...  void cutlass::device_kernel<GemmUniversal<...
     18.5        110481400       2912   ...  void cutlass::device_kernel<GemmUniversal<...
      7.1         42308042       3024   ...  void cutlass::Kernel<GemmQuantNv<MmaMultistage<...
      6.3         37483852       6048   ...  triton_scale_swizzle
      ...
```

### What confirms FP4

**`GemmQuantNv`** — present in row 3 above.

Full name: `cutlass::gemm::kernel::GemmQuantNv<cutlass::gemm::threadblock::MmaMultistage<...>>`

This is the CUTLASS GEMM kernel with NVIDIA quantization. On Blackwell hardware with an
FP4 model loaded under `quantization=fp_quant`, this kernel dispatches to Blackwell's FP4
tensor cores. It is not present in a bfloat16 or int8 inference run.

**`triton_scale_swizzle`** — present in row 4 above.

FP4 weights are stored with per-block scale factors. This Triton kernel loads and reorders
(swizzles) those scale factors into the memory layout required by the FP4 tensor core
instructions before each GemmQuantNv call. It is structurally tied to GemmQuantNv: its
instance count is always exactly 2× GemmQuantNv (one pass per input tensor, one per weight).

If both kernels are present, FP4 is executing at the hardware level.

### Expected counts (as a sanity check)

For Llama-3.2-3B (28 transformer layers), with one inference call and a warmup call:

- `GemmQuantNv`: ~3000 instances (28 layers × 7 projections Q/K/V/O/gate/up/down × steps)
- `triton_scale_swizzle`: ~6000 instances (always 2× GemmQuantNv)

A very different count (e.g. single digits) would suggest the profile only captured part of
the inference. Rerun and check the nsys profile covers the full generate() call.

### If neither kernel appears

FP4 is likely not executing. Check:

1. `quantization=fp_quant` is set in the vLLM serve command (see `run_cmd.sh`)
2. The model directory contains an NVFP4 checkpoint (not a standard bfloat16 one)
3. The GPU supports FP4 tensor cores (Blackwell = RTX 50xx / PRO 4000 Blackwell or newer)

If those are all correct but the kernels are still absent, CUTLASS or vLLM may have
changed the kernel names. Look through the full table for any kernel that appears only
under `fp_quant` and not under a baseline bfloat16 run — that is your new FP4 indicator.

---

## Deep verification: hardware counter (ncu)

There is another wey to verify this, which uses ncu to measure `sm__ops_path_tensor_op_type_fp4.sum`
— a raw GPU hardware counter that counts FP4 tensor operations directly.
It does not depend on kernel names at all, making it more robust than the kernel trace approach.

### Why this is not currently an option

ncu must run on the same OS as the GPU driver — it reads hardware counters through the
kernel. WSL breaks this:

```
Windows + NVIDIA driver
  └── WSL
        └── Docker + vLLM + ncu → GPU counters ✗  (blocked by WSL)

Native Linux + NVIDIA driver
  └── Docker + vLLM + ncu → GPU counters ✓
```

The current setup is Windows + WSL + Docker.
Getting a native Linux + NVIDIA driver working has been attempted (Ubuntu + RTX) and failed.
Until that is solved, this verification method is not usable.
