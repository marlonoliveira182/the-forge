# The Forge Promotion Workflow - Quick Reference

## 🚀 Essential Commands

```bash
# Check current status
python promote.py status

# Promote development to pre-production (only latest allowed)
python promote.py dev-to-pre v1.1.0-dev

# Promote pre-production to production (only latest allowed)
python promote.py pre-to-prd v1.1.0-pre

# Sync all environments with latest production
python promote.py sync-with-prd

# List versions in each environment
python promote.py list-dev
python promote.py list-pre
python promote.py list-prd

# Force promotion (overwrite existing)
python promote.py dev-to-pre v1.1.0-dev --force
```

## 📁 Directory Structure

```
the-forge/
├── dev/                    # Development (active work)
├── pre/                    # Pre-production (testing)
└── prd/                    # Production (stable releases)
```

## 🔄 Typical Workflow

1. **Develop** in `dev/the-forge-v1.1.0-dev/`
2. **Test** by promoting to `pre/the-forge-v1.1.0-pre/`
3. **Release** by promoting to `prd/the-forge-v1.1.0/`

## 📊 Current Status

```bash
python promote.py status
```

## 🎯 Version Naming

- **DEV**: `the-forge-v1.1.0-dev`
- **PRE**: `the-forge-v1.1.0-pre`
- **PRD**: `the-forge-v1.1.0`

## 📝 Logs

All promotions are logged in `promotion_log.json` 