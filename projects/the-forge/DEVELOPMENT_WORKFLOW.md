# The Forge - Development Workflow

## Overview

This project enforces a **dev-only** development workflow where all changes must be made exclusively in the `dev/` directory. This ensures:

- **Stability**: Production code in `archive/`, `pre/`, and `prd/` remains untouched
- **Version Control**: Clear separation between development and stable versions
- **Collaboration**: Multiple developers can work safely without conflicts

## Directory Structure

```
the-forge/
├── dev/                    # 🔧 DEVELOPMENT ONLY - All changes here
│   ├── src/               # Source code
│   ├── tests/             # Test files
│   ├── docs/              # Documentation
│   └── ...
├── archive/               # 📦 STABLE VERSIONS - Read-only
│   ├── the-forge-v1.0.0/
│   ├── the-forge-v1.1.0/
│   └── ...
├── pre/                   # 🚀 PRE-RELEASE - Read-only
├── prd/                   # 🏭 PRODUCTION - Read-only
└── scripts/               # 🔧 Workflow tools
    └── dev-protection.py  # Enforcement script
```

## Workflow Rules

### ✅ ALLOWED
- ✅ All development work in `dev/` directory
- ✅ Creating new features in `dev/src/`
- ✅ Writing tests in `dev/tests/`
- ✅ Documentation in `dev/docs/`
- ✅ Configuration files in `dev/`

### ❌ FORBIDDEN
- ❌ Direct changes to `archive/` files
- ❌ Direct changes to `pre/` files  
- ❌ Direct changes to `prd/` files
- ❌ Modifying stable versions directly

## Getting Started

### 1. Setup Protection
```bash
# Install git hooks to enforce dev-only changes
python scripts/dev-protection.py --setup-hooks
```

### 2. Create Development Branch
```bash
# Create a new development branch
python scripts/dev-protection.py --create-branch my-feature
```

### 3. Start Development
```bash
# Work exclusively in dev/ directory
cd dev/
# Make your changes...
```

### 4. Check for Violations
```bash
# Verify no changes outside dev/
python scripts/dev-protection.py --check
```

### 5. Promote to Archive
```bash
# When ready, promote to archive with version
python scripts/dev-protection.py --promote 1.2.0 --description "New feature X"
```

## Git Workflow

### Branch Strategy
- `main` - Protected, contains only stable code
- `dev-*` - Development branches for features
- `pre-*` - Pre-release branches
- `prd-*` - Production branches

### Commit Rules
1. **All commits must pass dev-only check**
2. **Use descriptive commit messages**
3. **Reference issue numbers when applicable**

### Pull Request Process
1. Create feature branch from `main`
2. Develop in `dev/` directory only
3. Run protection check: `python scripts/dev-protection.py --check`
4. Submit PR with clear description
5. Code review ensures dev-only compliance
6. Merge to `main` after approval

## Protection Mechanisms

### 1. Git Hooks
- **Pre-commit hook**: Automatically checks for violations
- **Pre-push hook**: Ensures no direct changes to stable directories

### 2. Script Validation
```bash
# Manual validation
python scripts/dev-protection.py --check
python scripts/dev-protection.py --validate
```

### 3. CI/CD Integration
- Automated checks in pipeline
- Block merges with violations
- Enforce branch protection rules

## Version Management

### Versioning Scheme
- **Major.Minor.Patch** (e.g., 1.2.3)
- **Pre-release**: 1.2.3-alpha, 1.2.3-beta
- **Development**: 1.2.3-dev

### Promotion Process
1. **Development** → `dev/` directory
2. **Archive** → `archive/the-forge-vX.Y.Z/`
3. **Pre-release** → `pre/the-forge-vX.Y.Z-pre/`
4. **Production** → `prd/the-forge-vX.Y.Z/`

### Promotion Commands
```bash
# Promote to archive
python scripts/dev-protection.py --promote 1.2.0

# With description
python scripts/dev-protection.py --promote 1.2.0 --description "Added new mapping feature"
```

## Troubleshooting

### Common Issues

#### "Changes detected outside dev/ directory"
**Solution**: Move all changes to `dev/` directory
```bash
# Check what files are changed
git status

# Move files to dev/ if needed
git mv file.py dev/src/
```

#### "Git hooks not working"
**Solution**: Reinstall hooks
```bash
python scripts/dev-protection.py --setup-hooks
```

#### "Cannot promote to archive"
**Solution**: Ensure you're on a dev branch
```bash
# Check current branch
git branch --show-current

# Create dev branch if needed
python scripts/dev-protection.py --create-branch my-feature
```

### Emergency Override
If absolutely necessary to modify stable code:
1. Create emergency branch
2. Document reason in commit message
3. Get approval from team lead
4. Use `--force` flag (not recommended)

## Best Practices

### Development
- ✅ Always work in `dev/` directory
- ✅ Use descriptive branch names
- ✅ Write tests for new features
- ✅ Update documentation
- ✅ Run protection checks before commits

### Collaboration
- ✅ Communicate changes in team chat
- ✅ Use pull requests for code review
- ✅ Tag team members for reviews
- ✅ Keep commits atomic and focused

### Quality Assurance
- ✅ Run tests before promoting
- ✅ Validate dev structure
- ✅ Check for violations
- ✅ Review documentation updates

## Tools Reference

### dev-protection.py Commands
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

### Git Commands
```bash
# Check status
git status

# Check for violations
python scripts/dev-protection.py --check

# Create feature branch
git checkout -b dev-feature-name

# Commit changes
git add dev/
git commit -m "Add new feature"

# Push to remote
git push origin dev-feature-name
```

## Support

For questions or issues with the development workflow:
1. Check this documentation
2. Run `python scripts/dev-protection.py --help`
3. Contact the development team
4. Create an issue in the project repository 