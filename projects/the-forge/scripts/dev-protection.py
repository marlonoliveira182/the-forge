#!/usr/bin/env python3
"""
Development Protection Script for The Forge

This script enforces that changes can only be made in the dev/ directory.
It provides hooks and utilities to maintain this workflow.
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from typing import List, Tuple

class DevProtection:
    def __init__(self, project_root: str | None = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.dev_dir = self.project_root / "dev"
        self.archive_dir = self.project_root / "archive"
        self.pre_dir = self.project_root / "pre"
        self.prd_dir = self.project_root / "prd"
        
    def check_dev_only_changes(self) -> Tuple[bool, List[str]]:
        """
        Check if there are any changes outside the dev directory.
        Returns (is_safe, list_of_violations)
        """
        violations = []
        
        # Get git status
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                print("Warning: Could not check git status")
                return True, []
                
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            for line in changed_files:
                if not line.strip():
                    continue
                    
                # Parse git status line (XY PATH)
                status = line[:2]
                file_path = line[3:]
                
                # Skip if file is in dev directory
                if file_path.startswith('dev/'):
                    continue
                    
                # Check if it's a tracked file that's been modified
                if status[0] in ['M', 'A', 'R', 'C']:
                    violations.append(f"{status}: {file_path}")
                    
        except Exception as e:
            print(f"Error checking git status: {e}")
            return True, []
            
        return len(violations) == 0, violations
    
    def create_dev_branch(self, branch_name: str | None = None) -> bool:
        """
        Create a new development branch from the current state.
        """
        if not branch_name:
            branch_name = f"dev-{os.getenv('USER', 'user')}-{int(time.time())}"
            
        try:
            # Create and switch to new branch
            subprocess.run(["git", "checkout", "-b", branch_name], cwd=self.project_root, check=True)
            print(f"Created development branch: {branch_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating branch: {e}")
            return False
    
    def promote_to_archive(self, version: str, description: str = "") -> bool:
        """
        Promote current dev state to archive with a new version.
        """
        try:
            # Ensure we're on a dev branch
            result = subprocess.run(["git", "branch", "--show-current"], 
                                  capture_output=True, text=True, cwd=self.project_root)
            current_branch = result.stdout.strip()
            
            if not current_branch.startswith('dev-'):
                print("Warning: Not on a development branch")
                
            # Create archive directory
            archive_path = self.archive_dir / f"the-forge-v{version}"
            archive_path.mkdir(exist_ok=True)
            
            # Copy current dev files to archive
            dev_files = list(self.dev_dir.rglob("*"))
            for file_path in dev_files:
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.dev_dir)
                    target_path = archive_path / relative_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, target_path)
            
            # Create version info
            version_info = {
                "version": version,
                "description": description,
                "branch": current_branch,
                "timestamp": str(Path().stat().st_mtime)
            }
            
            with open(archive_path / "version_info.json", "w") as f:
                import json
                json.dump(version_info, f, indent=2)
                
            print(f"Promoted to archive: the-forge-v{version}")
            return True
            
        except Exception as e:
            print(f"Error promoting to archive: {e}")
            return False
    
    def setup_git_hooks(self) -> bool:
        """
        Set up git hooks to enforce dev-only changes.
        """
        hooks_dir = self.project_root / ".git" / "hooks"
        pre_commit_hook = hooks_dir / "pre-commit"
        
        hook_content = '''#!/bin/sh
# Pre-commit hook to enforce dev-only changes

python scripts/dev-protection.py --check

if [ $? -ne 0 ]; then
    echo "ERROR: Changes detected outside dev/ directory!"
    echo "Please make all changes in the dev/ directory only."
    exit 1
fi
'''
        
        try:
            with open(pre_commit_hook, "w") as f:
                f.write(hook_content)
            
            # Make executable
            os.chmod(pre_commit_hook, 0o755)
            print("Git hooks installed successfully")
            return True
            
        except Exception as e:
            print(f"Error setting up git hooks: {e}")
            return False
    
    def validate_dev_structure(self) -> bool:
        """
        Validate that the dev directory has the proper structure.
        """
        required_dirs = ["src", "tests", "docs"]
        
        for dir_name in required_dirs:
            dir_path = self.dev_dir / dir_name
            if not dir_path.exists():
                print(f"Warning: Missing required directory: dev/{dir_name}")
                return False
                
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Development Protection for The Forge")
    parser.add_argument("--check", action="store_true", help="Check for violations")
    parser.add_argument("--setup-hooks", action="store_true", help="Set up git hooks")
    parser.add_argument("--create-branch", help="Create a new development branch")
    parser.add_argument("--promote", help="Promote current dev to archive with version")
    parser.add_argument("--description", help="Description for promotion")
    parser.add_argument("--validate", action="store_true", help="Validate dev structure")
    
    args = parser.parse_args()
    
    protection = DevProtection()
    
    if args.check:
        is_safe, violations = protection.check_dev_only_changes()
        if not is_safe:
            print("VIOLATIONS DETECTED:")
            for violation in violations:
                print(f"  {violation}")
            sys.exit(1)
        else:
            print("✓ No violations detected")
            
    elif args.setup_hooks:
        protection.setup_git_hooks()
        
    elif args.create_branch:
        protection.create_dev_branch(args.create_branch)
        
    elif args.promote:
        description = args.description or f"Promoted version {args.promote}"
        protection.promote_to_archive(args.promote, description)
        
    elif args.validate:
        if protection.validate_dev_structure():
            print("✓ Dev structure is valid")
        else:
            print("✗ Dev structure has issues")
            sys.exit(1)
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 