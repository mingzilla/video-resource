---
name: private_skills__manage_project_links
description: Provision each project's link_from_lib.sh + link_from_lib.yaml, which symlink private_skills into its .claude/skills
---

## I/O

| role       | content (file_path/text/tool)                         | example                            |
|------------|-------------------------------------------------------|------------------------------------|
| input1     | `<project>/.claude/skills/link_from_lib.yaml`         | which skills that project takes    |
| input2     | `.operation/project_links/subscribers.txt`            | the target dirs                    |
| processing | Use `private_skills__manage_project_links` for input1 |                                    |
| output1    | `<project>/.claude/skills/`                           | linked; `.gitignore` block written |
| output2    | `<project>/.claude/skills/link_from_lib.sh`           | created from the template          |

## Actions

- [WHEN] setting up, or re-syncing after any yaml or template change, [RUN] `.operation/project_links/_all.sh`
- [WHEN] adding a project, [DO] add `<project>/.claude/skills` to `subscribers.txt`, run `_all.sh`, fill in the yaml it scaffolds, run `_all.sh` again
- [WHEN] a skill is renamed or removed, [DO] run `_all.sh` - it names every yaml still pointing at the old name
- [WHEN] changing what new projects start with, [DO] edit the `links` list in `templates/link_from_lib.yaml`

## Key files

| file                           | what it is                                   | you edit it?                    |
|--------------------------------|----------------------------------------------|---------------------------------|
| `templates/link_from_lib.sh`   | source of every project's `link_from_lib.sh` | yes - to change the entry       |
| `scripts/links_lib.sh`         | the shared functions; sourced, never run     | to change the behaviour         |
| `<project>/link_from_lib.sh`   | GENERATED - overwritten every run            | **never**                       |
| `<project>/link_from_lib.yaml` | the project's own data                       | yes - the only per-project file |

## Decisions

- [Structure, Generated] - `link_from_lib.sh` is a constant: rendered from `templates/` into every project and overwritten each run. Edit the template; an edit to a copy is lost.
- [Structure, Owned] - `link_from_lib.yaml` is the project's data: written once, then never touched. A default added later does not reach existing projects.
- [Safety, Target] - `links::provision` writes files, so it refuses a target that is not a `/.claude/skills` dir inside an existing project. Do not relax either check to make a path work.
- [Safety, Validate-first] - `links::sync` validates every name before it cleans, so a typo is a no-op and not a half-wiped dir. That is what makes `_all.sh` safe to run as a test.
- [Safety, One-owner] - one script owns one `DST`. Two scripts on one `DST` make the second clean delete the first's links.
- [Safety, Single-call] - `links::clean` runs once per `links::sync` call, so every source group goes in one call.
- [Safety, Empty] - an empty `links:` skips the sync rather than wiping. Both `roots` and `links` keys must still be present - a missing key is a typo, and reading it as empty would drop every link.
- [Symlink, Absolute] - roots are absolute and names never contain `/`. A relative target resolves against `DST`, and a `/` starts a new root.
- [Git, Machine-local] - the links are absolute paths into `private_skills`; never commit them. `.gitignore` is generated from the links actually present, so it cannot drift. Never untrack by hand.
- [Git, Tracked] - `.gitignore` does not apply to an already-tracked file. Untrack it once with `git rm --cached`; the script prints a `TRACKED` warning when it sees one.
- [Env, Root] - `PRIVATE_SKILLS_ROOT` overrides the library path, so moving the library is one env var, not one edit per project.
- [Env, Dependency] - needs `python3` + `pyyaml`. Linux-side only; the `.sh` does not run on bare Windows.
- [Robust, Last-line] - `_all.sh` reads the last `subscribers.txt` line even without a trailing newline. Plain `read` drops it in silence.
