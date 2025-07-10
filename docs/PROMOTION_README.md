# The Forge Environment Promotion Workflow

This document describes the environment promotion workflow for The Forge project, which follows a structured approach to move code between development, pre-production, and production environments.

## 🏗️ Environment Structure

```
the-forge/
├── dev/                    # Development environment
│   ├── the-forge-v1.0.0-dev/     # Historical versions
│   ├── the-forge-v1.1.0-dev/     # Current active development
│   └── ...
├── pre/                    # Pre-production environment
│   ├── the-forge-v1.1.0-pre/     # Testing versions
│   └── ...
└── prd/                    # Production environment
    ├── the-forge-v1.0.0/         # Stable releases
    └── ...
```

## 🔄 Promotion Workflow

### 1. Development (DEV)
- **Purpose**: Active development, new features, bug fixes
- **Location**: `/dev/`
- **Naming**: `the-forge-v<version>-dev`
- **Status**: Work in progress

### 2. Pre-Production (PRE)
- **Purpose**: Testing, validation, user acceptance testing
- **Location**: `/pre/`
- **Naming**: `the-forge-v<version>-pre`
- **Status**: Ready for testing

### 3. Production (PRD)
- **Purpose**: Stable, tested, ready for distribution
- **Location**: `/prd/`
- **Naming**: `the-forge-v<version>`
- **Status**: Released

## 🚀 Using the Promotion Script

The `promote.py` script automates the promotion process between environments.

### Basic Commands

```bash
# Check current status of all environments
python promote.py status

# List versions in each environment
python promote.py list-dev
python promote.py list-pre
python promote.py list-prd

# Promote from DEV to PRE (only latest version allowed)
python promote.py dev-to-pre v1.1.0-dev

# Promote from PRE to PRD (only latest version allowed)
python promote.py pre-to-prd v1.1.0-pre

# Sync all environments with latest production version
python promote.py sync-with-prd

# Force promotion (overwrite existing target)
python promote.py dev-to-pre v1.1.0-dev --force
```

### Workflow Examples

#### Example 1: Complete Promotion Cycle

```bash
# 1. Check current status
python promote.py status

# 2. Promote development version to pre-production
python promote.py dev-to-pre v1.1.0-dev

# 3. Test the pre-production version
# ... run tests, user acceptance testing ...

# 4. If tests pass, promote to production
python promote.py pre-to-prd v1.1.0-pre

# 5. Verify production deployment
python promote.py status
```

#### Example 2: Handling Conflicts

```bash
# If target version already exists, use --force
python promote.py dev-to-pre v1.1.0-dev --force
```

## 📋 Promotion Process Details

### What the Script Does

1. **Validation**: Checks if source version exists and target doesn't conflict
2. **Guard-Rails**: Ensures only the latest version can be promoted to prevent unstable versions from moving forward
3. **Copy**: Copies the entire version directory to the target environment
4. **Version Update**: Updates version references in:
   - `setup.py`
   - `README.md`
   - `the-forge.py` (if `__version__` is present)
5. **Logging**: Records the promotion action in `promotion_log.json`

### Version Naming Convention

- **DEV**: `the-forge-v1.1.0-dev`
- **PRE**: `the-forge-v1.1.0-pre`
- **PRD**: `the-forge-v1.1.0`

### Automatic Version Updates

The script automatically updates version references:

```python
# In setup.py
version="1.1.0-dev"  # → version="1.1.0-pre" → version="1.1.0"

# In README.md
# The Forge v1.1.0-dev  # → # The Forge v1.1.0-pre → # The Forge v1.1.0

# In the-forge.py
__version__ = '1.1.0-dev'  # → __version__ = '1.1.0-pre' → __version__ = '1.1.0'
```

## 📊 Monitoring and Logging

### Promotion Log

All promotions are logged in `promotion_log.json`:

```json
[
  {
    "timestamp": "2025-01-10T20:30:00",
    "source_version": "the-forge-v1.1.0-dev",
    "target_version": "the-forge-v1.1.0-pre",
    "source_env": "DEV",
    "target_env": "PRE",
    "promoted_by": "username"
  }
]
```

### Status Command

The `status` command provides a comprehensive overview:

```bash
python promote.py status
```

Output:
```
📊 The Forge Environment Status
==================================================

🔧 DEV Environment (8 versions):
   • the-forge-v1.0.0-dev (1.0.0-dev)
   • the-forge-v1.1.0-dev (1.1.0-dev)
   • ...

🧪 PRE Environment (1 versions):
   • the-forge-v1.1.0-pre (1.1.0-pre)

🚀 PRD Environment (1 versions):
   • the-forge-v1.0.0 (1.0.0)

==================================================
💡 Usage:
   python promote.py dev-to-pre <version>
   python promote.py pre-to-prd <version>
   python promote.py status
```

## 🔧 Best Practices

### 1. Development Workflow
- Always work in the `dev/` environment
- Create new versions for major features: `v1.2.0-dev`, `v1.3.0-dev`
- Keep historical versions for reference

### 2. Testing Workflow
- Promote to `pre/` when ready for testing
- Run comprehensive tests in pre-production
- Fix issues in `dev/` and re-promote if needed

### 3. Release Workflow
- Only promote to `prd/` after thorough testing
- Use semantic versioning for releases
- Keep production versions stable

### 4. Version Management
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Increment appropriately:
  - **PATCH**: Bug fixes (1.1.0 → 1.1.1)
  - **MINOR**: New features (1.1.0 → 1.2.0)
  - **MAJOR**: Breaking changes (1.1.0 → 2.0.0)

## 🚨 Troubleshooting

### Common Issues

1. **Target version already exists**
   ```bash
   # Use --force to overwrite
   python promote.py dev-to-pre v1.1.0-dev --force
   ```

2. **Source version not found**
   ```bash
   # Check available versions
   python promote.py list-dev
   ```

3. **Permission errors**
   ```bash
   # Ensure you have write permissions to the target directory
   ```

### Validation Checks

The script performs these validations:
- ✅ Source version exists
- ✅ Target version doesn't conflict (unless --force)
- ✅ Only the latest version can be promoted (guard-rail)
- ✅ Required directories exist
- ✅ Version files can be updated

## 📝 Example Workflow

Here's a complete example of developing a new feature:

```bash
# 1. Start development
cd dev/the-forge-v1.1.0-dev
# ... make changes ...

# 2. Ready for testing
python promote.py dev-to-pre v1.1.0-dev

# 3. Test in pre-production
cd pre/the-forge-v1.1.0-pre
# ... run tests ...

# 4. If tests pass, release to production
python promote.py pre-to-prd v1.1.0-pre

# 5. Verify release
python promote.py status
```

This workflow ensures code quality, proper testing, and stable releases while maintaining a clear history of all versions. 