# Git EOL Universal Settings

Git historically handled line endings differently across Windows, Linux, and macOS.

Config needed:

- Different Machines - Win/Linux/Mac
- Windows uses WSL/Powershell

## 1. All Platforms Configuration

### 1.1. Universal Commands (All Platforms - Win/Linux/Mac)

Run once per machine

```bash
git config --global core.autocrlf false
git config --global core.eol lf
```

### 1.2. Every Project Needs

`.gitattributes` file:

```
# Mandatory: Enables LF normalization for text files
* text=auto

# Mandatory: Protect binary files
*.png binary
*.jpg binary
*.jar binary
*.exe binary
*.dll binary
*.so binary
```

## 2. Check Your Existing Global Settings

```shell
# See all global Git settings
git config --global --list | grep -E "(autocrlf|eol)"

# Should show:
# core.autocrlf=false  
# core.eol=lf
```

```powershell
# See all global Git settings
git config --global --list | Select-String "(autocrlf|eol)"

# Should show:
# core.autocrlf=false  
# core.eol=lf
```

### Windows-Specific Notes

For Windows users:

- Tools (e.g., VS Code, Notepad++) should be configured to use LF for consistency.
    - **PyCharm** - Settings -> Editor -> Code Style -> General -> Line Separator: `Unix and macOS (\n)`
    - **VS Code** - Settings -> `"files.eol": "\n"`
- WSL/WSL2 already uses LF by default.

## 3. Fix existing code for consistency

After adding `.gitattributes` to existing projects:

```shell
git add --renormalize .
git commit -m "Normalize line endings"
```

- ✅ This fixes existing files to match the new EOL rules.
- ⚠️ Note: Run this after committing/stashing changes to avoid conflicts.

### Result

- ✅ Consistent LF line endings everywhere
- ✅ Works across Windows/WSL/Ubuntu/Mac
- ✅ No merge conflicts from line endings
- ✅ Automatic for your entire team
