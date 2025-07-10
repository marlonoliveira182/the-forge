#!/usr/bin/env python3
"""
The Forge Environment Promotion Script

This script automates the promotion process between development, pre-production, and production environments.

Usage:
    python promote.py dev-to-pre <dev-version> [--force]
    python promote.py pre-to-prd <pre-version> [--force]
    python promote.py list-dev
    python promote.py list-pre
    python promote.py list-prd
    python promote.py status

Examples:
    python promote.py dev-to-pre v1.1.0-dev
    python promote.py pre-to-prd v1.1.0-pre
    python promote.py list-dev
"""

import os
import sys
import shutil
import argparse
import json
from datetime import datetime
from pathlib import Path

class ForgePromoter:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.dev_dir = self.base_dir / "dev"
        self.pre_dir = self.base_dir / "pre"
        self.prd_dir = self.base_dir / "prd"
        
        # Ensure directories exist
        self.dev_dir.mkdir(exist_ok=True)
        self.pre_dir.mkdir(exist_ok=True)
        self.prd_dir.mkdir(exist_ok=True)
    
    def list_versions(self, env_dir, env_name):
        """List all versions in a specific environment."""
        if not env_dir.exists():
            print(f"No {env_name} directory found.")
            return []
        
        versions = []
        for item in env_dir.iterdir():
            if item.is_dir() and item.name.startswith("the-forge-"):
                versions.append(item.name)
        
        # Sort by semantic versioning instead of alphabetically
        return self.sort_by_semantic_version(versions)
    
    def sort_by_semantic_version(self, versions):
        """Sort versions by semantic versioning (MAJOR.MINOR.PATCH)."""
        def version_key(version_name):
            # Extract version from "the-forge-v1.2.3-dev" -> "1.2.3"
            version_part = version_name.replace("the-forge-v", "").replace("-dev", "").replace("-pre", "")
            try:
                # Split version into parts and convert to integers for proper sorting
                parts = version_part.split('.')
                # Ensure we have at least 3 parts (MAJOR.MINOR.PATCH)
                while len(parts) < 3:
                    parts.append('0')
                return [int(part) for part in parts[:3]]  # Only use first 3 parts
            except (ValueError, IndexError):
                # Fallback to string comparison if parsing fails
                return [0, 0, 0]
        
        return sorted(versions, key=version_key)
    
    def get_version_info(self, version_path):
        """Extract version information from a project."""
        setup_py = version_path / "setup.py"
        if setup_py.exists():
            try:
                with open(setup_py, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple version extraction
                    for line in content.split('\n'):
                        if 'version=' in line:
                            version = line.split('version=')[1].split(',')[0].strip().strip('"\'')
                            return version
            except Exception as e:
                print(f"Error reading version from {setup_py}: {e}")
        
        # Fallback: extract from directory name
        return version_path.name.replace("the-forge-", "")
    
    def validate_promotion(self, source_path, target_env, target_version):
        """Validate if promotion is safe."""
        if not source_path.exists():
            raise ValueError(f"Source version not found: {source_path}")
        
        target_path = self.base_dir / target_env / target_version
        if target_path.exists():
            return False, f"Target version already exists: {target_path}"
        
        # Guard-rail: Only allow latest versions to be promoted
        if target_env == "pre":
            # For DEV to PRE: Only allow the most recent dev version
            dev_versions = self.list_versions(self.dev_dir, "DEV")
            if dev_versions:
                latest_dev = dev_versions[-1]  # Get the latest version
                source_version_name = source_path.name
                if source_version_name != latest_dev:
                    return False, f"Only the latest development version can be promoted. Latest: {latest_dev}, Attempting: {source_version_name}"
        
        elif target_env == "prd":
            # For PRE to PRD: Only allow the most recent pre version
            pre_versions = self.list_versions(self.pre_dir, "PRE")
            if pre_versions:
                latest_pre = pre_versions[-1]  # Get the latest version
                source_version_name = source_path.name
                if source_version_name != latest_pre:
                    return False, f"Only the latest pre-production version can be promoted. Latest: {latest_pre}, Attempting: {source_version_name}"
        
        return True, "OK"
    
    def update_version_files(self, target_path, new_version):
        """Update version references in the promoted version."""
        files_to_update = [
            ("setup.py", "version=", f'version="{new_version}",'),
            ("README.md", "# The Forge v", f"# The Forge {new_version}"),
        ]
        
        for filename, search_pattern, replacement in files_to_update:
            file_path = target_path / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Update version references
                    if filename == "setup.py":
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'version=' in line:
                                lines[i] = replacement
                                break
                        content = '\n'.join(lines)
                    elif filename == "README.md":
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if line.startswith("# The Forge v"):
                                lines[i] = replacement
                                break
                        content = '\n'.join(lines)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                except Exception as e:
                    print(f"Warning: Could not update {filename}: {e}")
    
    def promote_dev_to_pre(self, dev_version, force=False):
        """Promote a development version to pre-production."""
        print(f"🔄 Promoting {dev_version} from DEV to PRE...")
        
        # Handle both full version names and short names
        if not dev_version.startswith("the-forge-"):
            dev_version = f"the-forge-{dev_version}"
        
        source_path = self.dev_dir / dev_version
        pre_version = dev_version.replace("-dev", "-pre")
        target_path = self.pre_dir / pre_version
        
        # Validation
        is_valid, message = self.validate_promotion(source_path, "pre", pre_version)
        if not is_valid:
            if not force:
                print(f"❌ Validation failed: {message}")
                print("Use --force to override.")
                return False
            else:
                print(f"⚠️  Warning: {message}")
        
        try:
            # Copy the version
            if target_path.exists():
                shutil.rmtree(target_path)
            
            shutil.copytree(source_path, target_path)
            print(f"✅ Copied {dev_version} to {pre_version}")
            
            # Update version files
            self.update_version_files(target_path, pre_version.replace("the-forge-", ""))
            print(f"✅ Updated version references to {pre_version}")
            
            # Create promotion log
            self.log_promotion(dev_version, pre_version, "DEV", "PRE")
            
            print(f"🎉 Successfully promoted {dev_version} to {pre_version}")
            return True
            
        except Exception as e:
            print(f"❌ Promotion failed: {e}")
            return False
    
    def promote_pre_to_prd(self, pre_version, force=False):
        """Promote a pre-production version to production."""
        print(f"🔄 Promoting {pre_version} from PRE to PRD...")
        
        # Handle both full version names and short names
        if not pre_version.startswith("the-forge-"):
            pre_version = f"the-forge-{pre_version}"
        
        source_path = self.pre_dir / pre_version
        prd_version = pre_version.replace("-pre", "")
        target_path = self.prd_dir / prd_version
        
        # Validation
        is_valid, message = self.validate_promotion(source_path, "prd", prd_version)
        if not is_valid:
            if not force:
                print(f"❌ Validation failed: {message}")
                print("Use --force to override.")
                return False
            else:
                print(f"⚠️  Warning: {message}")
        
        try:
            # Copy the version
            if target_path.exists():
                shutil.rmtree(target_path)
            
            shutil.copytree(source_path, target_path)
            print(f"✅ Copied {pre_version} to {prd_version}")
            
            # Update version files
            self.update_version_files(target_path, prd_version.replace("the-forge-", ""))
            print(f"✅ Updated version references to {prd_version}")
            
            # Create promotion log
            self.log_promotion(pre_version, prd_version, "PRE", "PRD")
            
            print(f"🎉 Successfully promoted {pre_version} to {prd_version}")
            return True
            
        except Exception as e:
            print(f"❌ Promotion failed: {e}")
            return False
    
    def log_promotion(self, source_version, target_version, source_env, target_env):
        """Log the promotion action."""
        log_file = self.base_dir / "promotion_log.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "source_version": source_version,
            "target_version": target_version,
            "source_env": source_env,
            "target_env": target_env,
            "promoted_by": os.getenv("USERNAME", "unknown")
        }
        
        try:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not log promotion: {e}")
    
    def sync_with_latest_prd(self):
        """Sync DEV and PRE environments with the latest production version."""
        print("🔄 Syncing environments with latest production version...")
        
        # Get the latest production version
        prd_versions = self.list_versions(self.prd_dir, "PRD")
        if not prd_versions:
            print("❌ No production versions found to sync from.")
            return False
        
        latest_prd = prd_versions[-1]  # Get the latest production version
        latest_prd_path = self.prd_dir / latest_prd
        
        print(f"📦 Latest production version: {latest_prd}")
        
        try:
            # Sync to PRE environment - replace existing pre version
            pre_versions = self.list_versions(self.pre_dir, "PRE")
            if pre_versions:
                # Remove existing pre version
                existing_pre = self.pre_dir / pre_versions[-1]
                if existing_pre.exists():
                    shutil.rmtree(existing_pre)
                    print(f"🗑️  Removed existing PRE version: {pre_versions[-1]}")
            
            # Create new pre version from latest production
            pre_version = latest_prd.replace("the-forge-", "the-forge-") + "-pre"
            pre_path = self.pre_dir / pre_version
            
            shutil.copytree(latest_prd_path, pre_path)
            self.update_version_files(pre_path, pre_version.replace("the-forge-", ""))
            print(f"✅ Synced PRE environment: {pre_version}")
            
            # Sync to DEV environment - replace existing latest dev version
            dev_versions = self.list_versions(self.dev_dir, "DEV")
            if dev_versions:
                # Remove existing latest dev version
                existing_dev = self.dev_dir / dev_versions[-1]
                if existing_dev.exists():
                    shutil.rmtree(existing_dev)
                    print(f"🗑️  Removed existing DEV version: {dev_versions[-1]}")
            
            # Create new dev version from latest production
            dev_version = latest_prd.replace("the-forge-", "the-forge-") + "-dev"
            dev_path = self.dev_dir / dev_version
            
            # Remove if exists
            if dev_path.exists():
                shutil.rmtree(dev_path)
                print(f"🗑️  Removed existing DEV version: {dev_version}")
            
            shutil.copytree(latest_prd_path, dev_path)
            self.update_version_files(dev_path, dev_version.replace("the-forge-", ""))
            print(f"✅ Synced DEV environment: {dev_version}")
            
            # Log the sync operation
            self.log_promotion(latest_prd, f"SYNC-{pre_version}", "PRD", "PRE")
            self.log_promotion(latest_prd, f"SYNC-{dev_version}", "PRD", "DEV")
            
            print(f"🎉 Successfully synced all environments with {latest_prd}")
            return True
            
        except Exception as e:
            print(f"❌ Sync failed: {e}")
            return False
    
    def show_status(self):
        """Show the current status of all environments."""
        print("📊 The Forge Environment Status")
        print("=" * 50)
        
        # DEV environment
        dev_versions = self.list_versions(self.dev_dir, "DEV")
        print(f"\n🔧 DEV Environment ({len(dev_versions)} versions):")
        for version in dev_versions:
            version_info = self.get_version_info(self.dev_dir / version)
            print(f"   • {version} ({version_info})")
        
        # PRE environment
        pre_versions = self.list_versions(self.pre_dir, "PRE")
        print(f"\n🧪 PRE Environment ({len(pre_versions)} versions):")
        for version in pre_versions:
            version_info = self.get_version_info(self.pre_dir / version)
            print(f"   • {version} ({version_info})")
        
        # PRD environment
        prd_versions = self.list_versions(self.prd_dir, "PRD")
        print(f"\n🚀 PRD Environment ({len(prd_versions)} versions):")
        for version in prd_versions:
            version_info = self.get_version_info(self.prd_dir / version)
            print(f"   • {version} ({version_info})")
        
        print("\n" + "=" * 50)
        print("💡 Usage:")
        print("   python promote.py dev-to-pre <version>")
        print("   python promote.py pre-to-prd <version>")
        print("   python promote.py sync-with-prd")
        print("   python promote.py status")

def main():
    parser = argparse.ArgumentParser(
        description="The Forge Environment Promotion Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python promote.py dev-to-pre v1.1.0-dev
  python promote.py pre-to-prd v1.1.0-pre
  python promote.py status
  python promote.py list-dev
        """
    )
    
    parser.add_argument("action", choices=[
        "dev-to-pre", "pre-to-prd", "sync-with-prd", "list-dev", "list-pre", "list-prd", "status"
    ], help="Action to perform")
    
    parser.add_argument("version", nargs="?", help="Version to promote (e.g., v1.1.0-dev)")
    parser.add_argument("--force", action="store_true", help="Force promotion even if target exists")
    
    args = parser.parse_args()
    
    promoter = ForgePromoter()
    
    if args.action == "dev-to-pre":
        if not args.version:
            print("❌ Error: Version is required for dev-to-pre action")
            sys.exit(1)
        success = promoter.promote_dev_to_pre(args.version, args.force)
        sys.exit(0 if success else 1)
    
    elif args.action == "pre-to-prd":
        if not args.version:
            print("❌ Error: Version is required for pre-to-prd action")
            sys.exit(1)
        success = promoter.promote_pre_to_prd(args.version, args.force)
        sys.exit(0 if success else 1)
    
    elif args.action == "list-dev":
        versions = promoter.list_versions(promoter.dev_dir, "DEV")
        print("🔧 DEV Environment versions:")
        for version in versions:
            version_info = promoter.get_version_info(promoter.dev_dir / version)
            print(f"   • {version} ({version_info})")
    
    elif args.action == "list-pre":
        versions = promoter.list_versions(promoter.pre_dir, "PRE")
        print("🧪 PRE Environment versions:")
        for version in versions:
            version_info = promoter.get_version_info(promoter.pre_dir / version)
            print(f"   • {version} ({version_info})")
    
    elif args.action == "list-prd":
        versions = promoter.list_versions(promoter.prd_dir, "PRD")
        print("🚀 PRD Environment versions:")
        for version in versions:
            version_info = promoter.get_version_info(promoter.prd_dir / version)
            print(f"   • {version} ({version_info})")
    
    elif args.action == "sync-with-prd":
        success = promoter.sync_with_latest_prd()
        sys.exit(0 if success else 1)
    
    elif args.action == "status":
        promoter.show_status()

if __name__ == "__main__":
    main() 