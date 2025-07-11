#!/usr/bin/env python3
"""
Setup script for The Forge dev-only workflow

This script initializes the development environment with proper structure
and protection mechanisms.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def setup_dev_structure(project_root: Path):
    """Create the proper dev directory structure."""
    dev_dir = project_root / "dev"
    
    # Create dev directory if it doesn't exist
    dev_dir.mkdir(exist_ok=True)
    
    # Create required subdirectories
    required_dirs = [
        "src",
        "tests", 
        "docs",
        "config",
        "scripts"
    ]
    
    for dir_name in required_dirs:
        dir_path = dev_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✓ Created directory: dev/{dir_name}")
    
    # Create basic files
    files_to_create = {
        "src/__init__.py": "",
        "tests/__init__.py": "",
        "docs/README.md": "# Development Documentation\n\nThis directory contains development documentation.",
        "config/settings.py": "# Development Configuration\n\n# Add your development settings here",
        "scripts/__init__.py": ""
    }
    
    for file_path, content in files_to_create.items():
        full_path = dev_dir / file_path
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
            print(f"✓ Created file: dev/{file_path}")

def setup_git_hooks(project_root: Path):
    """Set up git hooks for dev-only protection."""
    try:
        # Run the protection script directly
        result = subprocess.run(
            [sys.executable, "scripts/dev-protection.py", "--setup-hooks"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Git hooks installed successfully")
        else:
            print(f"✗ Failed to install git hooks: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error setting up git hooks: {e}")
        return False
    
    return True

def create_initial_commit(project_root: Path):
    """Create initial commit if repository is empty."""
    try:
        # Check if repository has commits
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0 and result.stdout.strip() == "0":
            # No commits yet, create initial commit
            subprocess.run(["git", "add", "."], cwd=project_root, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit: Setup dev-only workflow"],
                cwd=project_root,
                check=True
            )
            print("✓ Created initial commit")
        else:
            print("✓ Repository already has commits")
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating initial commit: {e}")
        return False
    
    return True

def setup_branch_protection(project_root: Path):
    """Set up branch protection for main branch."""
    try:
        # Create .gitattributes to mark stable directories as read-only
        gitattributes_content = """# Mark stable directories as read-only
archive/* -text
pre/* -text  
prd/* -text

# Allow development in dev directory
dev/* text
scripts/* text
"""
        
        gitattributes_path = project_root / ".gitattributes"
        with open(gitattributes_path, "w") as f:
            f.write(gitattributes_content)
        
        print("✓ Created .gitattributes for directory protection")
        
    except Exception as e:
        print(f"✗ Error setting up branch protection: {e}")
        return False
    
    return True

def create_dev_branch(project_root: Path):
    """Create initial development branch."""
    try:
        # Create and switch to dev branch
        subprocess.run(
            ["git", "checkout", "-b", "dev-initial"],
            cwd=project_root,
            check=True
        )
        print("✓ Created initial development branch: dev-initial")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating dev branch: {e}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🔧 Setting up The Forge dev-only workflow...")
    print("=" * 50)
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"Project root: {project_root}")
    
    # Step 1: Setup dev structure
    print("\n1. Setting up dev directory structure...")
    setup_dev_structure(project_root)
    
    # Step 2: Setup git hooks
    print("\n2. Setting up git hooks...")
    if not setup_git_hooks(project_root):
        print("⚠️  Git hooks setup failed, but continuing...")
    
    # Step 3: Setup branch protection
    print("\n3. Setting up branch protection...")
    setup_branch_protection(project_root)
    
    # Step 4: Create initial commit if needed
    print("\n4. Setting up initial commit...")
    create_initial_commit(project_root)
    
    # Step 5: Create dev branch
    print("\n5. Creating development branch...")
    create_dev_branch(project_root)
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Start developing in the dev/ directory")
    print("2. Run: python scripts/dev-protection.py --check")
    print("3. Read: DEVELOPMENT_WORKFLOW.md")
    print("\nHappy coding! 🚀")

if __name__ == "__main__":
    main() 