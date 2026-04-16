# Decision Mapping — Classification QA

---

## Flow Diagram

```text
+-------------------------------+
|  A. Why Build This            |
|                               |
|  [1. Split the working app]   |
|  [2. Claude Code, not API]    |
|  [3. Two-system split]        |
+---------------+---------------+
                |
        "ok, how do we
         talk to Claude?"
                |
                v
+-------------------------------+
|  B. Prompt Design             |
|                               |
|  [4. Intention, not persona]  |
|  [5. Earn generalisations]    |
|  [6. File paths, not inline]  |
+---------------+---------------+
                |
        "ok, we have prompts.
         what happens before
         we start classifying?"
                |
                v
+-------------------------------+
|  C. Before Any Work Starts    |
|                               |
|  [7. Upfront verification]    |
|  [8. Dynamic schema]          |
|  [9. PK from data]            |
|  [10. Skip invalid websites]  |
|  [11. Track _source]          |
+---------------+---------------+
                |
        "ok, inputs validated.
         how do workers
         actually process?"
                |
                v
+-------------------------------+
|  D. The Work Engine           |
|                               |
|  [12. Work queue, not cycles] |
|  [13. AFK = same queue]       |
|  [14. Per-file DuckDB lock]   |
|  [15. Stats per-response]     |
+---------------+---------------+
                |
        "ok, what if
         something breaks?"
                |
                v
+-------------------------------+
|  E. When Things Go Wrong      |
|                               |
|  [16. Pause and resume]       |
|  [17. Auto-respawn on poll]   |
|  [18. POST not GET]           |
+---------------+---------------+
                |
        "ok, it works.
         who pays for it?"
                |
                v
+-------------------------------+
|  F. Paying For It             |
|                               |
|  [19. Subscription first]     |
|  [20. AFK = always API]       |
|  [21. Multi-user, per-file]   |
+---------------+---------------+
                |
        "ok, how do real
         users use this?"
                |
                v
+-------------------------------+
|  G. Making It Usable          |
|                               |
|  [22. /test = sync kick-off]  |
|  [23. Server defaults]        |
|  [24. Human-readable names]   |
+---------------+---------------+
                |
        "ok, how do we
         ship this?"
                |
                v
+-------------------------------+
|  H. Code Structure            |
|                               |
|  [25. Zero shared code]       |
|  [26. Three files, not five]  |
+---------------+---------------+
                |
                v
+-------------------------------+
|  I. Shipping It               |
|                               |
|  [27. Token without browser]  |
|  [28. Non-root in Docker]     |
+-------------------------------+
```
