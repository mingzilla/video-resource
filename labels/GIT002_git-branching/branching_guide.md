# Branching and Tagging Strategy

## Overview

This project uses a structured approach to create easily deployable builds through dedicated branches and corresponding tags.

## Branch Naming Convention

### Build Branches

```
build/YYYY-MM.NNN
```

**Examples:**

- `build/2025-08.001`
- `build/2025-08.002`
- `build/2025-09.001`

**Structure:**

- `build/` - Namespace prefix indicating this is a runnable build branch
- `YYYY-MM` - Year and month (ISO date format with hyphen)
- `.NNN` - Three-digit sequence number within that month

## Tag Naming Convention

### Build Tags

```
vbuild-YYYY-MM.NNN
```

**Examples:**

- `vbuild-2025-08.001`
- `vbuild-2025-08.002`
- `vbuild-2025-09.001`

**Structure:**

- `v` - Standard Git tag prefix
- `build-` - Indicates this tags a build branch
- `YYYY-MM.NNN` - Corresponds to branch name `build/YYYY-MM.NNN` (maintains 1:1 mapping)

## Key Principles

### Easy Deployment

Each build branch is designed to be immediately runnable:

```bash
git checkout build/2025-08.001
docker compose up -d
```

No configuration changes or additional setup required.

### Sequence Numbers Are Not Dates

The three-digit sequence (`.001`, `.002`, etc.) represents:

- **Build iterations within a month**
- **Not calendar dates**
- **Not tied to specific days**

This means:

- `build/2025-08.001` might be created on August 5th
- `build/2025-08.002` might be created on August 6th with significant changes
- The sequence indicates progression, not calendar dates

### Branch-Tag Relationship

Each build branch has a corresponding tag:

- Branch `build/2025-08.001` → Tag `vbuild-2025-08.001`
- The tag marks the final state of the build branch
- Tags provide permanent references even if branches are eventually cleaned up

## Usage Examples

### Creating a New Build

```bash
# Create and switch to new build branch
git checkout -b build/2025-08.003

# Make your changes, test, ensure docker compose works
# ...

# Tag the final state
git tag vbuild-2025-08.003

# Push both branch and tag
git push origin build/2025-08.003
git push origin vbuild-2025-08.003
```

### Using a Build

```bash
# Checkout specific build
git checkout build/2025-08.001

# Run the system
docker compose up -d
```

### Listing Available Builds

```bash
# List build branches
git branch -r | grep build/

# List build tags
git tag | grep vbuild-
```

## Design Decisions

| Decision                                    | Reason                                                                     |
|---------------------------------------------|----------------------------------------------------------------------------|
| `2025-08` not `2025_08`                     | Follows ISO 8601 date format standard                                      |
| `2025-08.001` not `2025.08.001`             | Hyphen for date, dot separates sequence - visually distinct                |
| `001` not `01`                              | Not a date concept - builds can be very different, creation dates may vary |
| Branch: `build/2025...` not `build-2025...` | Forward slash creates proper Git namespace                                 |
| Tag: `vbuild-2025...` not `vbuild/2025...`  | Tags use hyphens to avoid filesystem issues                                |
| Tag has `v` prefix                          | Standard Git convention for version tags                                   |