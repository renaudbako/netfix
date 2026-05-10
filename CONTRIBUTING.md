# Contributing to NetFix

Thank you for taking the time to contribute to **NetFix**! 🎉  
All contributions — bug fixes, new checks, documentation improvements, or ideas — are welcome.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Coding Guidelines](#coding-guidelines)
- [Adding a New Diagnostic Check](#adding-a-new-diagnostic-check)
- [Commit Message Format](#commit-message-format)
- [Pull Request Checklist](#pull-request-checklist)

---

## Code of Conduct

Be respectful and constructive. This is an open project — everyone is welcome regardless of experience level.

---

## Getting Started

```bash
# 1. Fork the repository on GitHub, then clone your fork
git clone https://github.com/<your-username>/netfix.git
cd netfix

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Test your changes on at least one platform
python3 netfix.py        # Linux
python netfix.py         # Windows
```

---

## How to Contribute

| Type | Description |
|------|-------------|
| 🐛 Bug fix | Fix incorrect behavior, crashes, or wrong output |
| ✨ New check | Add a new diagnostic module to the menu |
| 📝 Docs | Improve README, inline comments, or docstrings |
| 🔧 Refactor | Clean up code without changing behavior |
| 🌐 Platform | Improve macOS support or untested Linux distros |

---

## Coding Guidelines

- **Python 3.6+ compatible** — no f-strings with `=` specifier, no walrus operator
- **Zero external dependencies** — standard library only (`subprocess`, `socket`, `platform`, etc.)
- **Single-file design** — all code stays in `netfix.py` unless a major architectural change is proposed and discussed via an issue first
- Use the existing helper functions (`ok()`, `warn()`, `fail()`, `fix()`, `info()`) for all output
- All commands that differ between Windows and Linux must branch on `IS_WINDOWS`
- Add a `timeout` to every `run_cmd()` call to prevent the script from hanging

---

## Adding a New Diagnostic Check

Follow this template when adding a new check function:

```python
def check_my_feature():
    section("N · My Feature Title")

    # Windows path
    if IS_WINDOWS:
        out, err, rc = run_cmd("windows-command", timeout=15)
        # ... parse and report

    # Linux path
    else:
        out, err, rc = run_cmd("linux-command", timeout=15)
        # ... parse and report

    if <problem_detected>:
        fail("Description of what went wrong.")
        fix("Exact command or step to resolve it.")
    else:
        ok("Everything looks good.")
```

Then add it to the **menu** in `main()`:
```python
# In the menu() call — add your option label
"Check my new feature",

# In the if/elif chain — add the handler
elif idx == N:  check_my_feature()
```

---

## Commit Message Format

Use a short prefix so the history stays readable:

```
Add: brief description of what was added
Fix: brief description of what was fixed
Docs: brief description of documentation change
Refactor: brief description of code cleanup
Test: brief description of test added
```

Examples:
```
Add: Wi-Fi signal strength check for Linux (iwconfig)
Fix: Gateway regex fails on multi-adapter Windows setups
Docs: Add macOS notes to README compatibility table
```

---

## Pull Request Checklist

Before opening a PR, confirm the following:

- [ ] Tested on **Linux** and/or **Windows** (state which in the PR description)
- [ ] No new external library dependencies introduced
- [ ] All new output goes through `ok()`, `warn()`, `fail()`, `fix()`, or `info()`
- [ ] Every `run_cmd()` call has a `timeout` argument
- [ ] The menu in `main()` is updated if a new check was added
- [ ] Code is readable and follows the existing style

---

Thank you for helping make NetFix better! 🚀
