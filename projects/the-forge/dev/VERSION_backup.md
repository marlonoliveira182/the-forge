# The Forge - Version Tracking

## Current Development Version: v2.0.0

### Previous Versions
- **v1.0.0** - Initial dev-only workflow setup with protection system
  - Dev-only protection system
  - Git hooks for automatic enforcement
  - Promotion workflow
  - Comprehensive documentation

### v2.0.0 Development Goals
- [ ] Add improvements based on user feedback
- [ ] Enhance workflow features
- [ ] Optimize performance
- [ ] Add new functionality

### Development Notes
- Working on branch: `dev-v2.0.0`
- All changes must be in `dev/` directory
- Use `python scripts/dev-protection.py --check` before commits
- Promote when ready: `python scripts/dev-protection.py --promote 2.0.0` 