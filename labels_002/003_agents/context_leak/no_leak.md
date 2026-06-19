```text
[clean_context_root]               # No CLAUDE.md instruction allowed
|
|-- [project] (seals the leak)     # WHAT - Tasker (deepseek) root, Tasker may read all files here, DO NOT add content about how to edit content inside
|   |                              # No CLAUDE.md instruction allowed
|   |                              # Anything Tasker may use is NOT ALLOWED to be put outside of this folder 
|   | 
|   |-- .claude/skills/<name>.md   # SKILL used by tasker
|   |-- scripts, instruction.md    # Tasker runs with this
|
|-- [project__post_processing]     # WHAT - everything used to edit and use `[project]`
|   |                              # Has CLAUDE.md - toolbox/actions for: worker, reviewer, supervisor
|   |
|   |-- _meta/                     # WHAT - What CLAUDE.md uses, used for running [project]
|   |   |-- _actions/              # Reusable actions we use to run for the project
|   |
|   |-- _meta__edit/               # WHAT - Used when editing `[project]`
|   |   |-- _rules/                # Rules used for editing `[project]`, including lesson learnt
|   |   |-- _tests/                # Test code to run against project
|   |
|   |-- CLAUDE.md                  # Router in `[project__post_processing]`
```