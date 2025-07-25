# The Forge - Scripts Directory

This directory contains scripts for managing the dev-only workflow.

## Scripts

### `dev-protection.py`
Main protection script that enforces dev-only changes.

**Usage:**
```bash
# Check for violations
python scripts/dev-protection.py --check

# Setup git hooks
python scripts/dev-protection.py --setup-hooks

# Create development branch
python scripts/dev-protection.py --create-branch feature-name

# Promote to archive
python scripts/dev-protection.py --promote 1.2.0 --description "Description"

# Validate dev structure
python scripts/dev-protection.py --validate
```

### `setup-dev-workflow.py`
Setup script to initialize the dev-only workflow.

**Usage:**
```bash
# Run complete setup
python scripts/setup-dev-workflow.py
```

## Workflow Enforcement

These scripts work together to enforce the dev-only development workflow:

1. **Pre-commit hooks** - Automatically check for violations
2. **Manual validation** - Run checks before important operations
3. **Branch protection** - Prevent direct changes to stable code
4. **Promotion tools** - Safely move code from dev to stable versions

## Integration

The scripts integrate with:
- Git hooks for automatic enforcement
- CI/CD pipelines for continuous validation
- Development tools for manual checks
- Documentation for workflow guidance

For more information, see `DEVELOPMENT_WORKFLOW.md` in the project root. 