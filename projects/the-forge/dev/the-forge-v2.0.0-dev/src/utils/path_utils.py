"""
Path utilities for The Forge v2.0.0
"""

import os
from pathlib import Path
from typing import Tuple, List, Optional

class PathUtils:
    """Utility class for path handling and validation"""
    
    @staticmethod
    def validate_file_path(file_path: str, allowed_extensions: Optional[List[str]] = None) -> Tuple[bool, str]:
        """Validate if a file path exists and has correct extension"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return False, f"File does not exist: {file_path}"
            
            if not path.is_file():
                return False, f"Path is not a file: {file_path}"
            
            if allowed_extensions:
                if path.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
                    return False, f"File extension not allowed. Expected: {allowed_extensions}, got: {path.suffix}"
            
            return True, "File path is valid"
            
        except Exception as e:
            return False, f"Error validating file path: {str(e)}"
    
    @staticmethod
    def validate_directory_path(dir_path: str) -> Tuple[bool, str]:
        """Validate if a directory path exists and is writable"""
        try:
            path = Path(dir_path)
            
            if not path.exists():
                return False, f"Directory does not exist: {dir_path}"
            
            if not path.is_dir():
                return False, f"Path is not a directory: {dir_path}"
            
            # Check if directory is writable
            test_file = path / ".test_write"
            try:
                test_file.touch()
                test_file.unlink()
            except (OSError, PermissionError):
                return False, f"Directory is not writable: {dir_path}"
            
            return True, "Directory path is valid"
            
        except Exception as e:
            return False, f"Error validating directory path: {str(e)}"
    
    @staticmethod
    def generate_output_filename(input_path: str, operation: str, extension: Optional[str] = None) -> str:
        """Generate output filename based on input and operation"""
        input_path_obj = Path(input_path)
        
        if extension is None:
            if operation == "xsd-to-json":
                extension = ".json"
            elif operation == "json-to-xsd":
                extension = ".xsd"
            elif operation == "schema-to-excel":
                extension = ".xlsx"
            elif operation == "mapping":
                extension = "_mapping.xlsx"
            else:
                extension = ".output"
        
        # Create output filename
        stem = input_path_obj.stem
        if operation != "mapping":
            output_name = f"{stem}_{operation}{extension}"
        else:
            output_name = f"{stem}{extension}"
        
        return str(input_path_obj.parent / output_name)
    
    @staticmethod
    def ensure_directory_exists(dir_path: str) -> bool:
        """Ensure directory exists, create if it doesn't"""
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> Optional[int]:
        """Get file size in bytes"""
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return None
    
    @staticmethod
    def is_large_file(file_path: str, threshold_mb: int = 10) -> bool:
        """Check if file is larger than threshold"""
        size = PathUtils.get_file_size(file_path)
        if size is None:
            return False
        return size > (threshold_mb * 1024 * 1024)
    
    @staticmethod
    def get_relative_path(base_path: str, target_path: str) -> str:
        """Get relative path from base to target"""
        try:
            base = Path(base_path).resolve()
            target = Path(target_path).resolve()
            return str(target.relative_to(base))
        except Exception:
            return target_path
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Ensure filename is not empty
        if not filename:
            filename = "unnamed"
        
        return filename 