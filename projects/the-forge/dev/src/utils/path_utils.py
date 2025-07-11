"""
Path utilities for handling file paths and extensions.
"""

import os
from pathlib import Path
from typing import Optional, Tuple


class PathUtils:
    """Utility class for path operations."""
    
    @staticmethod
    def get_file_extension(filepath: str) -> str:
        """Get file extension in lowercase."""
        return os.path.splitext(filepath)[1].lower()
    
    @staticmethod
    def is_xsd_file(filepath: str) -> bool:
        """Check if file is an XSD file."""
        return PathUtils.get_file_extension(filepath) == '.xsd'
    
    @staticmethod
    def is_json_file(filepath: str) -> bool:
        """Check if file is a JSON file."""
        return PathUtils.get_file_extension(filepath) == '.json'
    
    @staticmethod
    def is_schema_file(filepath: str) -> bool:
        """Check if file is a schema file (XSD or JSON)."""
        ext = PathUtils.get_file_extension(filepath)
        return ext in ['.xsd', '.json']
    
    @staticmethod
    def get_filename_without_extension(filepath: str) -> str:
        """Get filename without extension."""
        return os.path.splitext(os.path.basename(filepath))[0]
    
    @staticmethod
    def get_directory(filepath: str) -> str:
        """Get directory path from filepath."""
        return os.path.dirname(filepath)
    
    @staticmethod
    def ensure_directory_exists(directory: str) -> None:
        """Ensure directory exists, create if it doesn't."""
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def is_file_readable(filepath: str) -> bool:
        """Check if file exists and is readable."""
        return os.path.isfile(filepath) and os.access(filepath, os.R_OK)
    
    @staticmethod
    def is_directory_writable(directory: str) -> bool:
        """Check if directory exists and is writable."""
        return os.path.isdir(directory) and os.access(directory, os.W_OK)
    
    @staticmethod
    def get_relative_path(filepath: str, base_path: str) -> str:
        """Get relative path from base path."""
        try:
            return os.path.relpath(filepath, base_path)
        except ValueError:
            return filepath
    
    @staticmethod
    def normalize_path(filepath: str) -> str:
        """Normalize file path."""
        return os.path.normpath(filepath)
    
    @staticmethod
    def join_paths(*paths: str) -> str:
        """Join path components."""
        return os.path.join(*paths)
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """Get a safe filename by removing invalid characters."""
        import re
        # Remove or replace invalid characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        safe_name = safe_name.strip('. ')
        return safe_name or 'unnamed'
    
    @staticmethod
    def generate_output_filename(source_path: str, operation: str, 
                               target_path: Optional[str] = None) -> str:
        """Generate output filename based on source and operation."""
        source_name = PathUtils.get_filename_without_extension(source_path)
        
        if target_path:
            target_name = PathUtils.get_filename_without_extension(target_path)
            return f"{operation}_{source_name}_to_{target_name}.xlsx"
        else:
            return f"{operation}_{source_name}.xlsx"
    
    @staticmethod
    def validate_file_path(filepath: str, expected_extensions: Optional[list] = None) -> Tuple[bool, str]:
        """Validate file path and return (is_valid, error_message)."""
        if not filepath:
            return False, "File path is empty"
        
        if not PathUtils.is_file_readable(filepath):
            return False, f"File does not exist or is not readable: {filepath}"
        
        if expected_extensions:
            ext = PathUtils.get_file_extension(filepath)
            if ext not in expected_extensions:
                return False, f"File has unsupported extension {ext}. Expected: {', '.join(expected_extensions)}"
        
        return True, ""
    
    @staticmethod
    def validate_directory_path(directory: str) -> Tuple[bool, str]:
        """Validate directory path and return (is_valid, error_message)."""
        if not directory:
            return False, "Directory path is empty"
        
        if not os.path.exists(directory):
            try:
                PathUtils.ensure_directory_exists(directory)
                return True, ""
            except Exception as e:
                return False, f"Cannot create directory {directory}: {str(e)}"
        
        if not PathUtils.is_directory_writable(directory):
            return False, f"Directory is not writable: {directory}"
        
        return True, "" 