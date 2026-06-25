
```
check__1D__does_it_code_or_read.py                             ← FILE (detector; classify only)
│
├── 1D__is_coding_attempt(name, code) -> bool                  ← WHAT  (the hook's API)
│     evidence = _1D__find_coding_attempt(...)
│     return evidence and _1D__coding_attempt__in_1d_scope(evidence, code)
│
├── _1D__find_coding_attempt(name, code) -> evidence|None      ← WHAT  (dispatcher over HOWs)
│     ├── _1D__find_coding_attempt__by_script_file()
│     ├── _1D__find_coding_attempt__by_regex()
│     ├── _1D__find_coding_attempt__by_split_index()
│     ├── _1D__find_coding_attempt__by_hardcode()
│     └── _1D__find_coding_attempt__by_block_ref()
│
└── _1D__coding_attempt__in_1d_scope(evidence, code) -> bool   ← helper (the live narrowing)
```