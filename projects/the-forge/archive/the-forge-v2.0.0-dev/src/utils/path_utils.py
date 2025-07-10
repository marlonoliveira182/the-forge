"""
Path Utilities Module

Handles path operations and file management:
- Path normalization
- File existence checks
- Directory creation
- File extension handling
"""

import os
import re
from typing import List, Optional, Tuple
from pathlib import Path


class PathUtils:
    """
    Utility class for path operations and file management.
    
    Provides methods for:
    - Path normalization and validation
    - File existence and permission checks
    - Directory creation and management
    - File extension handling
    """
    
    def __init__(self):
        self.supported_extensions = {'.xsd', '.xml', '.json', '.xlsx'}
    
    def normalize_path(self, path: str) -> str:
        """
        Normalize a file path.
        
        Args:
            path: Path to normalize
            
        Returns:
            Normalized path string
        """
        if not path:
            return ""
        
        # Convert to absolute path and normalize separators
        normalized = os.path.normpath(os.path.abspath(path))
        
        return normalized
    
    def ensure_directory_exists(self, directory_path: str) -> bool:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception:
            return False
    
    def get_file_extension(self, file_path: str) -> str:
        """
        Get the file extension from a path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File extension (including the dot)
        """
        return os.path.splitext(file_path)[1].lower()
    
    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if a file has a supported extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file has supported extension
        """
        extension = self.get_file_extension(file_path)
        return extension in self.supported_extensions
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists and is readable.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file exists and is readable
        """
        return os.path.isfile(file_path) and os.access(file_path, os.R_OK)
    
    def directory_exists(self, directory_path: str) -> bool:
        """
        Check if a directory exists and is accessible.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            True if directory exists and is accessible
        """
        return os.path.isdir(directory_path) and os.access(directory_path, os.R_OK)
    
    def get_base_filename(self, file_path: str) -> str:
        """
        Get the base filename without extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Base filename without extension
        """
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        
        # Remove common suffixes
        base_name = re.sub(r'[_-](source|target)$', '', base_name, flags=re.IGNORECASE)
        
        return base_name.lower()
    
    def create_output_path(
        self,
        input_path: str,
        output_directory: str,
        suffix: str = "",
        extension: str = ".xlsx"
    ) -> str:
        """
        Create an output path based on input file.
        
        Args:
            input_path: Path to input file
            output_directory: Output directory
            suffix: Suffix to add to filename
            extension: Output file extension
            
        Returns:
            Output file path
        """
        base_name = self.get_base_filename(input_path)
        filename = f"{base_name}{suffix}{extension}"
        return os.path.join(output_directory, filename)
    
    def validate_file_path(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Validate a file path.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not file_path:
            errors.append("File path is empty")
            return False, errors
        
        if not os.path.exists(file_path):
            errors.append(f"File does not exist: {file_path}")
            return False, errors
        
        if not os.path.isfile(file_path):
            errors.append(f"Path is not a file: {file_path}")
            return False, errors
        
        if not os.access(file_path, os.R_OK):
            errors.append(f"File is not readable: {file_path}")
            return False, errors
        
        if not self.is_supported_file(file_path):
            errors.append(f"Unsupported file type: {self.get_file_extension(file_path)}")
            return False, errors
        
        return True, errors
    
    def validate_directory_path(self, directory_path: str) -> Tuple[bool, List[str]]:
        """
        Validate a directory path.
        
        Args:
            directory_path: Path to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not directory_path:
            errors.append("Directory path is empty")
            return False, errors
        
        if not os.path.exists(directory_path):
            errors.append(f"Directory does not exist: {directory_path}")
            return False, errors
        
        if not os.path.isdir(directory_path):
            errors.append(f"Path is not a directory: {directory_path}")
            return False, errors
        
        if not os.access(directory_path, os.R_OK | os.W_OK):
            errors.append(f"Directory is not accessible: {directory_path}")
            return False, errors
        
        return True, errors
    
    def get_relative_path(self, base_path: str, target_path: str) -> str:
        """
        Get relative path from base to target.
        
        Args:
            base_path: Base directory path
            target_path: Target file path
            
        Returns:
            Relative path string
        """
        try:
            return os.path.relpath(target_path, base_path)
        except ValueError:
            return target_path
    
    def split_path_components(self, path: str) -> List[str]:
        """
        Split a path into its components.
        
        Args:
            path: Path to split
            
        Returns:
            List of path components
        """
        return [component for component in path.split(os.sep) if component]
    
    def join_path_components(self, components: List[str]) -> str:
        """
        Join path components into a path string.
        
        Args:
            components: List of path components
            
        Returns:
            Joined path string
        """
        return os.path.join(*components)
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File size in bytes, or None if error
        """
        try:
            return os.path.getsize(file_path)
        except OSError:
            return None
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get comprehensive file information.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        info = {
            'path': file_path,
            'exists': False,
            'size': None,
            'extension': '',
            'base_name': '',
            'directory': '',
            'is_supported': False
        }
        
        if os.path.exists(file_path):
            info['exists'] = True
            info['size'] = self.get_file_size(file_path)
            info['extension'] = self.get_file_extension(file_path)
            info['base_name'] = self.get_base_filename(file_path)
            info['directory'] = os.path.dirname(file_path)
            info['is_supported'] = self.is_supported_file(file_path)
        
        return info 