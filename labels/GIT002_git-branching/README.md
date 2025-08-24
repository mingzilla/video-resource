## Core Principle - Design for Impatient People

```text
[Design for Impatient People]
|
|-- Q: Ming, how do I do / run this?
|   +-- A: max 3 sentences:
|       |-- 1 sentence: just docker compose up
|       |-- 2 sentences: to build: docker compose up file1; to run: docker compose up file2
|       +-- 3 sentences: think hard -> people won't listen
|    
|-- Branching Strategy
|   |-- repo - one project or many projects? 
|   |   |-- releases - will they be released at the same time?
|   |   |-- branches - branch by release
|   |   +-- projects - same release, one repo, one branch, one start command for all
|   |
|   +-- principle:
|       |-- Q: how do I do/run this for the August Version?
|       +-- A: swap to August branch, docker compose up
|
+-- Core Principle:
    |-- responsibility
    |   |-- Who is going to maintain this?
    |   +-- 2 months later, who can tell people how to use this? Me? Please don't ask me!
    |
    +-- anti-pattern
        |-- too many parameters, too many env vars
```
