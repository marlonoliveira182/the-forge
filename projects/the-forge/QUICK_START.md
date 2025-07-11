# The Forge - Quick Start Guide

## 🚀 Getting Started with Dev-Only Workflow

### What We've Set Up

✅ **Dev-Only Protection System**
- All changes must be made in `dev/` directory only
- Git hooks prevent commits with violations
- Automated validation scripts
- Clear workflow documentation

✅ **Directory Structure**
```
the-forge/
├── dev/                    # 🔧 DEVELOPMENT ONLY
│   ├── src/               # Source code
│   ├── tests/             # Test files  
│   ├── docs/              # Documentation
│   ├── config/            # Configuration
│   └── scripts/           # Dev scripts
├── archive/               # 📦 STABLE VERSIONS
├── pre/                   # 🚀 PRE-RELEASE
├── prd/                   # 🏭 PRODUCTION
└── scripts/               # 🔧 Workflow tools
```

### 🎯 How to Use

#### 1. Start Development
```bash
# You're already on dev-initial branch
# All work should be in dev/ directory
cd dev/
# Start coding...
```

#### 2. Check for Violations
```bash
# Before committing, always check
python scripts/dev-protection.py --check
```

#### 3. Commit Changes
```bash
# Only commit changes in dev/
git add dev/
git commit -m "Add new feature"
```

#### 4. Promote to Archive
```bash
# When ready to release
python scripts/dev-protection.py --promote 1.2.0 --description "New feature"
```

### 🛡️ Protection Features

- **Pre-commit hooks** - Automatically check for violations
- **Manual validation** - Run `python scripts/dev-protection.py --check`
- **Branch protection** - Stable directories are read-only
- **Promotion tools** - Safe version management

### 📚 Documentation

- `DEVELOPMENT_WORKFLOW.md` - Complete workflow guide
- `scripts/README.md` - Script documentation
- `scripts/dev-protection.py --help` - Command reference

### 🎉 You're Ready!

Your dev-only workflow is now active. All changes must be made in the `dev/` directory, and the system will automatically enforce this rule.

**Happy coding! 🚀** 