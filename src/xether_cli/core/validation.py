import os
import re
from pathlib import Path
from typing import Optional

class ValidationError(Exception):
    """Raised when input validation fails"""
    pass

def validate_file_path(file_path: str, must_exist: bool = True, must_be_file: bool = True) -> Path:
    """Validate a file path
    
    Args:
        file_path: Path to validate
        must_exist: Whether the path must exist
        must_be_file: Whether the path must be a file (not directory)
    
    Returns:
        Path object if valid
    
    Raises:
        ValidationError: If validation fails
    """
    if not file_path or not file_path.strip():
        raise ValidationError("File path cannot be empty")
    
    try:
        path = Path(file_path).expanduser().resolve()
    except Exception as e:
        raise ValidationError(f"Invalid file path: {e}")
    
    if must_exist and not path.exists():
        raise ValidationError(f"Path does not exist: {path}")
    
    if must_be_file and path.exists() and not path.is_file():
        raise ValidationError(f"Path is not a file: {path}")
    
    # Check for suspicious paths - only if path exists to avoid issues with new files
    if path.exists() and any(part in ('..', '.') for part in path.parts):
        raise ValidationError(f"Path contains relative navigation: {file_path}")
    
    return path

def validate_directory_path(dir_path: str, must_exist: bool = True, create_if_missing: bool = False) -> Path:
    """Validate a directory path
    
    Args:
        dir_path: Directory path to validate
        must_exist: Whether the directory must exist
        create_if_missing: Create directory if it doesn't exist
    
    Returns:
        Path object if valid
    
    Raises:
        ValidationError: If validation fails
    """
    if not dir_path or not dir_path.strip():
        raise ValidationError("Directory path cannot be empty")
    
    try:
        path = Path(dir_path).expanduser().resolve()
    except Exception as e:
        raise ValidationError(f"Invalid directory path: {e}")
    
    if must_exist and not path.exists():
        if create_if_missing:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValidationError(f"Cannot create directory {path}: {e}")
        else:
            raise ValidationError(f"Directory does not exist: {path}")
    
    if path.exists() and not path.is_dir():
        raise ValidationError(f"Path is not a directory: {path}")
    
    return path

def validate_email(email: str) -> str:
    """Validate email format
    
    Args:
        email: Email address to validate
    
    Returns:
        Email if valid
    
    Raises:
        ValidationError: If email is invalid
    """
    if not email or not email.strip():
        raise ValidationError("Email cannot be empty")
    
    email = email.strip()
    # Basic email validation - more comprehensive regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError(f"Invalid email format: {email}")
    
    # Additional checks
    if '..' in email:
        raise ValidationError(f"Invalid email format: {email}")
    
    if email.startswith('.') or email.endswith('.'):
        raise ValidationError(f"Invalid email format: {email}")
    
    return email

def validate_project_id(project_id: str) -> int:
    """Validate project ID
    
    Args:
        project_id: Project ID to validate
    
    Returns:
        Project ID as integer if valid
    
    Raises:
        ValidationError: If project ID is invalid
    """
    if not project_id or not project_id.strip():
        raise ValidationError("Project ID cannot be empty")
    
    try:
        project_id_int = int(project_id)
        if project_id_int <= 0:
            raise ValidationError("Project ID must be positive")
        return project_id_int
    except ValueError:
        raise ValidationError(f"Project ID must be a number: {project_id}")

def validate_resource_id(resource_id: str, resource_type: str = "resource") -> str:
    """Validate a generic resource ID
    
    Args:
        resource_id: Resource ID to validate
        resource_type: Type of resource for error messages
    
    Returns:
        Resource ID if valid
    
    Raises:
        ValidationError: If resource ID is invalid
    """
    if not resource_id or not resource_id.strip():
        raise ValidationError(f"{resource_type} ID cannot be empty")
    
    # Basic validation - no whitespace, reasonable length
    resource_id = resource_id.strip()
    if any(char.isspace() for char in resource_id):
        raise ValidationError(f"{resource_type} ID cannot contain whitespace")
    
    if len(resource_id) > 100:
        raise ValidationError(f"{resource_type} ID too long (max 100 characters)")
    
    return resource_id

def validate_dataset_name(name: Optional[str] = None) -> Optional[str]:
    """Validate dataset name
    
    Args:
        name: Dataset name to validate
    
    Returns:
        Dataset name if valid
    
    Raises:
        ValidationError: If dataset name is invalid
    """
    if name is None:
        return None
    
    name = name.strip()
    if not name:
        raise ValidationError("Dataset name cannot be empty")
    
    if len(name) > 255:
        raise ValidationError("Dataset name too long (max 255 characters)")
    
    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
    if any(char in name for char in invalid_chars):
        raise ValidationError(f"Dataset name contains invalid characters: {invalid_chars}")
    
    return name
