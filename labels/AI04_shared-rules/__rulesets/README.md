# How to use this

- Make sure project is a git repo
- Change `/mnt/e/code/github-release/video-resource/labels/AI04_shared-rules/__rulesets` in `_pull.sh`
- copy `_pull.sh` to the root directory of a git project, run it
- IDE ignore `__rulesets` directory

# Why

- AI tools may have permission issue if you refer to files outside of current directory
    - so you cannot refer to a central ruleset location
- You don't want to touch multiple versions of ruleset files
    - you only want to manage 1 version
- Git submodule, subtree, subprojects are painful to manage 
