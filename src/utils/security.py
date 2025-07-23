#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security utilities for AI Video GPT

This module provides functions for secure handling of file paths and subprocess calls
to prevent command injection vulnerabilities.
"""

import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import List, Optional, Union


class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass


def validate_file_path(path: Union[str, Path], must_exist: bool = False, 
                      allowed_extensions: Optional[List[str]] = None) -> str:
    """
    Validates and sanitizes a file path to prevent directory traversal and injection attacks.
    
    Args:
        path: The file path to validate
        must_exist: If True, raises SecurityError if path doesn't exist
        allowed_extensions: List of allowed file extensions (e.g., ['.mp4', '.mp3'])
        
    Returns:
        Sanitized absolute path
        
    Raises:
        SecurityError: If path is invalid or potentially dangerous
    """
    if not path:
        raise SecurityError("Path cannot be empty")
    
    # Convert to string and normalize
    path_str = str(path).strip()
    
    # Check for dangerous characters and patterns
    dangerous_patterns = [
        r'\.\./',  # Directory traversal
        r'\.\.\*',  # Directory traversal
        r'[;&|`$]',  # Shell metacharacters
        r'[\r\n]',  # Line breaks
        r'[\x00-\x1f]',  # Control characters
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, path_str, re.IGNORECASE):
            raise SecurityError(f"Path contains dangerous pattern: {pattern}")
    
    # Resolve to absolute path and normalize
    try:
        abs_path = os.path.abspath(path_str)
        normalized_path = os.path.normpath(abs_path)
    except (OSError, ValueError) as e:
        raise SecurityError(f"Invalid path format: {e}")
    
    # Check if path tries to escape the working directory or common safe directories
    current_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Allow paths within the project or system temp directories
    allowed_prefixes = [
        current_dir,
        project_root,
        os.path.expanduser("~"),  # User home directory
        os.path.join(os.environ.get("TEMP", "/tmp")),  # Temp directory
    ]
    
    # On Windows, also allow common system paths
    if os.name == 'nt':
        allowed_prefixes.extend([
            r"C:\Windows\Temp",
            os.environ.get("TEMP", ""),
            os.environ.get("TMP", ""),
        ])
    
    path_is_safe = any(
        normalized_path.startswith(os.path.normpath(prefix)) 
        for prefix in allowed_prefixes if prefix
    )
    
    if not path_is_safe:
        raise SecurityError(f"Path is outside allowed directories: {normalized_path}")
    
    # Check file extension if specified
    if allowed_extensions:
        path_ext = os.path.splitext(normalized_path)[1].lower()
        if path_ext not in [ext.lower() for ext in allowed_extensions]:
            raise SecurityError(f"File extension {path_ext} not in allowed list: {allowed_extensions}")
    
    # Check if file exists if required
    if must_exist and not os.path.exists(normalized_path):
        raise SecurityError(f"File does not exist: {normalized_path}")
    
    return normalized_path


def validate_directory_path(path: Union[str, Path], create_if_not_exists: bool = False) -> str:
    """
    Validates and sanitizes a directory path.
    
    Args:
        path: The directory path to validate
        create_if_not_exists: If True, creates the directory if it doesn't exist
        
    Returns:
        Sanitized absolute directory path
        
    Raises:
        SecurityError: If path is invalid or potentially dangerous
    """
    validated_path = validate_file_path(path)
    
    if os.path.exists(validated_path) and not os.path.isdir(validated_path):
        raise SecurityError(f"Path exists but is not a directory: {validated_path}")
    
    if create_if_not_exists and not os.path.exists(validated_path):
        try:
            os.makedirs(validated_path, exist_ok=True)
        except OSError as e:
            raise SecurityError(f"Failed to create directory: {e}")
    
    return validated_path


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename by removing or replacing dangerous characters.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    if not filename:
        raise SecurityError("Filename cannot be empty")
    
    # Remove path components
    filename = os.path.basename(filename)
    
    # Replace dangerous characters with underscores
    dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(dangerous_chars, '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not too long (255 is typical filesystem limit)
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        max_name_length = 255 - len(ext)
        sanitized = name[:max_name_length] + ext
    
    if not sanitized:
        raise SecurityError("Filename becomes empty after sanitization")
    
    return sanitized


def build_ffmpeg_command(ffmpeg_path: str, input_files: List[str], output_file: str, 
                        additional_args: List[str] = None) -> List[str]:
    """
    Builds a secure FFmpeg command with validated inputs.
    
    Args:
        ffmpeg_path: Path to ffmpeg executable
        input_files: List of input file paths
        output_file: Output file path
        additional_args: Additional FFmpeg arguments
        
    Returns:
        List of command arguments suitable for subprocess
        
    Raises:
        SecurityError: If any input is invalid
    """
    # Validate FFmpeg executable
    ffmpeg_path = validate_file_path(ffmpeg_path, must_exist=True)
    
    # Validate input files
    validated_inputs = []
    for input_file in input_files:
        validated_inputs.append(validate_file_path(input_file, must_exist=True))
    
    # Validate output file path (directory must exist or be creatable)
    output_dir = os.path.dirname(output_file)
    if output_dir:
        validate_directory_path(output_dir, create_if_not_exists=True)
    validated_output = validate_file_path(output_file)
    
    # Build command
    command = [ffmpeg_path]
    
    # Add input files
    for input_file in validated_inputs:
        command.extend(['-i', input_file])
    
    # Add additional arguments if provided
    if additional_args:
        # Validate that additional args don't contain dangerous patterns
        for arg in additional_args:
            if isinstance(arg, str) and re.search(r'[;&|`$]', arg):
                raise SecurityError(f"Dangerous character in argument: {arg}")
        command.extend(additional_args)
    
    # Add output file
    command.append(validated_output)
    
    return command


def safe_subprocess_run(command: List[str], timeout: int = 300, **kwargs) -> subprocess.CompletedProcess:
    """
    Safely executes a subprocess command with security checks.
    
    Args:
        command: List of command arguments
        timeout: Command timeout in seconds
        **kwargs: Additional arguments for subprocess.run
        
    Returns:
        CompletedProcess instance
        
    Raises:
        SecurityError: If command is potentially dangerous
        subprocess.CalledProcessError: If command fails
        subprocess.TimeoutExpired: If command times out
    """
    if not command or not isinstance(command, list):
        raise SecurityError("Command must be a non-empty list")
    
    # Validate executable path
    executable = command[0]
    validate_file_path(executable, must_exist=True)
    
    # Check for shell metacharacters in arguments
    for arg in command[1:]:
        if isinstance(arg, str) and re.search(r'[;&|`$<>]', arg):
            raise SecurityError(f"Argument contains shell metacharacters: {arg}")
    
    # Set secure defaults
    secure_kwargs = {
        'shell': False,  # Never use shell=True
        'timeout': timeout,
        'capture_output': True,
        'text': True,
        'check': True,
    }
    
    # Override with user-provided kwargs
    secure_kwargs.update(kwargs)
    
    # Ensure shell is always False
    secure_kwargs['shell'] = False
    
    try:
        return subprocess.run(command, **secure_kwargs)
    except subprocess.CalledProcessError as e:
        raise SecurityError(f"Command failed: {e.stderr}")
    except subprocess.TimeoutExpired as e:
        raise SecurityError(f"Command timed out after {timeout} seconds")


def create_temp_file_list(file_paths: List[str], base_dir: str) -> str:
    """
    Creates a temporary file containing a list of files for FFmpeg concat.
    
    Args:
        file_paths: List of file paths to include
        base_dir: Base directory for the temporary file
        
    Returns:
        Path to the temporary file list
        
    Raises:
        SecurityError: If any path is invalid
    """
    # Validate base directory
    base_dir = validate_directory_path(base_dir, create_if_not_exists=True)
    
    # Validate all file paths
    validated_paths = []
    for file_path in file_paths:
        validated_paths.append(validate_file_path(file_path, must_exist=True))
    
    # Create temporary file
    import tempfile
    temp_fd, temp_path = tempfile.mkstemp(suffix='.txt', dir=base_dir, text=True)
    
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            for file_path in validated_paths:
                # Use forward slashes for FFmpeg compatibility and escape single quotes
                ffmpeg_path = file_path.replace('\\', '/').replace("'", "\\'")
                f.write(f"file '{ffmpeg_path}'\n")
        
        return temp_path
    except Exception as e:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise SecurityError(f"Failed to create temporary file list: {e}")


def cleanup_temp_files(*file_paths: str) -> None:
    """
    Safely removes temporary files.
    
    Args:
        *file_paths: Variable number of file paths to remove
    """
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                # Ensure it's a safe path before deletion
                validated_path = validate_file_path(file_path)
                os.unlink(validated_path)
        except (OSError, SecurityError) as e:
            # Log warning but don't raise exception for cleanup failures
            print(f"Warning: Could not remove temporary file {file_path}: {e}")


# Environment variable validation
def get_safe_env_path(env_var: str, default_command: str) -> str:
    """
    Safely gets an executable path from environment variable.
    
    Args:
        env_var: Environment variable name
        default_command: Default command name if env var not set
        
    Returns:
        Validated executable path
        
    Raises:
        SecurityError: If executable not found or invalid
    """
    # Get path from environment or use default
    executable = os.getenv(env_var, default_command)
    
    # If it's just a command name, try to find it in PATH
    if os.path.basename(executable) == executable:
        # Use shutil.which to find the executable in PATH
        import shutil
        found_path = shutil.which(executable)
        if not found_path:
            raise SecurityError(f"Executable '{executable}' not found in PATH")
        executable = found_path
    
    # Validate the path
    return validate_file_path(executable, must_exist=True)