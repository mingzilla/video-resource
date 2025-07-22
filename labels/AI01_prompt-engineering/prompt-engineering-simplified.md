# Prompting Techniques - Simplified Guide

## 0. Summary

| **Aspect**       | **Description**                                |
|------------------|------------------------------------------------|
| **What it is**   | 5 core techniques for optimizing LLM responses |
| **Primary use**  | Choose right technique, evaluate results       |
| **Target users** | Anyone using LLMs who needs reliable results   |

## 1. Techniques

### 1.1. Technique Selection

| **Technique**              | **When to Use**                 | **Example**                          |
|----------------------------|---------------------------------|--------------------------------------|
| **Zero-Shot**              | Simple, direct tasks            | "Classify sentiment: 'I love this!'" |
| **Few-Shot**               | Pattern recognition, formatting | Show 2-3 examples, then ask          |
| **Chain of Thought (CoT)** | Step-by-step reasoning needed   | "Let's think step by step:"          |
| **Tree of Thoughts (ToT)** | Multiple approaches needed      | "Let's explore different paths:"     |
| **ReAct**                  | External tools/research needed  | Reasoning + Action loops             |

### 1.2. Quick Decision Tree

```
[What type of task?]
├── Simple/Direct → Zero-Shot
├── Pattern-based → Few-Shot  
├── Reasoning required → CoT
├── Complex problem → ToT
└── Need external data → ReAct
```

## 2. Evaluation

```
[Correct Technique?]
├── Result: Accuracy, Speed, Consistency
└── Consideration: Comparison, Edge Cases  
```

### 2.1. Correct Technique Applied?

| **Check**            | **Question**                                   |
|----------------------|------------------------------------------------|
| **Task Match**       | Does technique fit the problem type?           |
| **Complexity Match** | Is technique appropriate for difficulty level? |
| **Model Capability** | Can your LLM handle this technique?            |

### 2.2. Results Measurement

| **Metric**      | **How to Check**                    | **Target**       |
|-----------------|-------------------------------------|------------------|
| **Accuracy**    | Correct vs incorrect responses      | 80%+             |
| **Speed**       | Response time and iterations needed | Fast as possible |
| **Consistency** | Same input → similar output         | 85%+             |

### 2.3. Considerations

#### 2.3.1. Comparison Testing

```
Test Process:
1. Try simpler technique first (Zero-Shot)
2. If poor results → upgrade technique
3. Compare results side-by-side
4. Choose best performer
```

#### 2.3.2. Edge Case Validation

| **Edge Case Type**      | **Test Method**          |
|-------------------------|--------------------------|
| **Unusual inputs**      | Try 3-5 weird examples   |
| **Boundary conditions** | Test limits and extremes |
| **Ambiguous cases**     | Check unclear scenarios  |

## 3. Quick Implementation

### 3.1. Technique Templates

```markdown
# Zero-Shot

[Task instruction] + [Input]

# Few-Shot

[Example 1] + [Example 2] + [New input]

# Chain of Thought

[Task] + "Let's think step by step:"

# Tree of Thoughts

[Task] + "Let's explore multiple approaches:"

# ReAct

[Task] + [External tool access] + [Reasoning loop]
```

### 3.2. Evaluation Checklist

- [ ] **Technique matches task complexity**
- [ ] **Results meet accuracy targets (80%+)**
- [ ] **Speed is acceptable for use case**
- [ ] **Consistency across similar inputs (85%+)**
- [ ] **Tested against simpler alternatives**
- [ ] **Edge cases handled properly**

---

**Bottom Line**: Pick the simplest technique that gives you good results. Test it. If it fails, try the next level up.