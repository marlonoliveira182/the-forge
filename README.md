# Prometheus Repository

This repository contains The Forge project and related development tools, organized into a clean, maintainable structure with all components consolidated under `projects/the-forge/`.

## Directory Structure

### Root Level
- **`projects/`** - All project components consolidated here
- **`.git/`** - Git repository data
- **`.gitignore`** - Git ignore patterns

### Project Structure (`projects/the-forge/`)
- **`archive/`** - Legacy and archived versions
- **`dev/`** - Development versions and experimental features
  - `the-forge-v1.0.0-dev/` - v1.0.0 development version
  - `the-forge-v1.1.0-dev/` - v1.1.0 development version  
  - `the-forge-v2.0.0-dev/` - v2.0.0 development version
  - `recent_dirs.json` - Development tracking
- **`docs/`** - Documentation and reference materials
- **`scripts/`** - Utility scripts and automation tools
  - `promote.py` - Promotion automation script
  - `dev-protection.py` - Development protection
  - `setup-dev-workflow.py` - Workflow setup
- **`microservices/`** - Complete microservices implementation
  - `README_MICROSERVICES.md` - Microservices documentation
  - `start_microservices.py` - Microservices startup script
  - `backup_ui/` - UI backup and reference
  - `tests/` - Microservices test suite
  - `outputs/` - Microservices output files
  - `api-gateway/` - API Gateway service
  - `converter-service/` - Schema conversion service
  - `excel-service/` - Excel generation service
  - `extraction-service/` - Field extraction service
  - `mapping-service/` - Path mapping service
- **`build/`** - Build artifacts and cache files
  - `.pytest_cache/` - Python test cache
- **`logs/`** - Application and test logs
  - `forge_api_server.log` - API server logs
  - `ui_simulation_test.log` - UI test logs
- **`pre/`** - Pre-release versions
- **`prd/`** - Product requirements and specifications

## Quick Start

### For Microservices Development
```bash
cd projects/the-forge/microservices
python start_microservices.py
```

### For Legacy Development
```bash
cd projects/the-forge/dev/the-forge-v1.1.0-dev
python the-forge.py
```

## Development Workflow

1. **All development** is now consolidated under `projects/the-forge/`
2. **Stable versions** are maintained in `projects/the-forge/archive/`
3. **Development versions** are in `projects/the-forge/dev/`
4. **Microservices** are in `projects/the-forge/microservices/`
5. **Documentation** is centralized in `projects/the-forge/docs/`
6. **Logs** are organized in `projects/the-forge/logs/`
7. **Build artifacts** are in `projects/the-forge/build/`

## Notes

- All components are now consolidated under `projects/the-forge/`
- No more scattered files in the root directory
- Clean separation of concerns within the project structure
- Maintains all existing functionality while improving organization 