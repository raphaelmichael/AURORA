"""
Aurora Sentinel - File Handler Utility
Robust file operations with context managers and backup functionality
"""

import os
import shutil
import json
import time
import logging
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager
from pathlib import Path


class FileHandler:
    """Robust file handling with context managers and backup functionality"""
    
    def __init__(self, backup_enabled: bool = True):
        self.backup_enabled = backup_enabled
        self.logger = logging.getLogger("Aurora_FileHandler")
        
    @contextmanager
    def safe_open(self, filepath: str, mode: str = 'r', encoding: str = 'utf-8', create_backup: bool = None):
        """
        Context manager for safe file operations with automatic backup
        """
        if create_backup is None:
            create_backup = self.backup_enabled and 'w' in mode and os.path.exists(filepath)
            
        backup_path = None
        if create_backup:
            backup_path = self._create_backup(filepath)
            
        file_obj = None
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            
            file_obj = open(filepath, mode, encoding=encoding)
            self.logger.debug(f"Opened file: {filepath} in mode: {mode}")
            yield file_obj
            
        except Exception as e:
            self.logger.error(f"Error with file {filepath}: {e}")
            
            # Restore backup if write operation failed
            if backup_path and 'w' in mode:
                try:
                    shutil.copy2(backup_path, filepath)
                    self.logger.info(f"Restored backup: {backup_path} -> {filepath}")
                except Exception as restore_error:
                    self.logger.error(f"Failed to restore backup: {restore_error}")
            raise
            
        finally:
            if file_obj:
                file_obj.close()
                self.logger.debug(f"Closed file: {filepath}")
                
    def _create_backup(self, filepath: str) -> str:
        """Creates a backup of the file"""
        if not os.path.exists(filepath):
            return None
            
        timestamp = int(time.time())
        backup_dir = os.path.join(os.path.dirname(filepath), '.aurora_backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        backup_filename = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            shutil.copy2(filepath, backup_path)
            self.logger.info(f"Created backup: {filepath} -> {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
            
    def read_file(self, filepath: str, encoding: str = 'utf-8') -> str:
        """Safely read text file content"""
        try:
            with self.safe_open(filepath, 'r', encoding=encoding, create_backup=False) as f:
                content = f.read()
            self.logger.debug(f"Read file: {filepath} ({len(content)} chars)")
            return content
        except Exception as e:
            self.logger.error(f"Failed to read file {filepath}: {e}")
            return ""
            
    def write_file(self, filepath: str, content: str, encoding: str = 'utf-8') -> bool:
        """Safely write content to file"""
        try:
            with self.safe_open(filepath, 'w', encoding=encoding) as f:
                f.write(content)
            self.logger.info(f"Wrote file: {filepath} ({len(content)} chars)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write file {filepath}: {e}")
            return False
            
    def append_file(self, filepath: str, content: str, encoding: str = 'utf-8') -> bool:
        """Safely append content to file"""
        try:
            with self.safe_open(filepath, 'a', encoding=encoding, create_backup=False) as f:
                f.write(content)
            self.logger.debug(f"Appended to file: {filepath} ({len(content)} chars)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to append to file {filepath}: {e}")
            return False
            
    def read_json(self, filepath: str) -> Dict[str, Any]:
        """Safely read JSON file"""
        try:
            with self.safe_open(filepath, 'r', create_backup=False) as f:
                data = json.load(f)
            self.logger.debug(f"Read JSON file: {filepath}")
            return data
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in file {filepath}: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Failed to read JSON file {filepath}: {e}")
            return {}
            
    def write_json(self, filepath: str, data: Dict[str, Any], indent: int = 4) -> bool:
        """Safely write data to JSON file"""
        try:
            with self.safe_open(filepath, 'w') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            self.logger.info(f"Wrote JSON file: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write JSON file {filepath}: {e}")
            return False
            
    def read_lines(self, filepath: str, encoding: str = 'utf-8') -> List[str]:
        """Safely read file as list of lines"""
        try:
            with self.safe_open(filepath, 'r', encoding=encoding, create_backup=False) as f:
                lines = f.readlines()
            self.logger.debug(f"Read lines from file: {filepath} ({len(lines)} lines)")
            return lines
        except Exception as e:
            self.logger.error(f"Failed to read lines from file {filepath}: {e}")
            return []
            
    def write_lines(self, filepath: str, lines: List[str], encoding: str = 'utf-8') -> bool:
        """Safely write list of lines to file"""
        try:
            with self.safe_open(filepath, 'w', encoding=encoding) as f:
                f.writelines(lines)
            self.logger.info(f"Wrote lines to file: {filepath} ({len(lines)} lines)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write lines to file {filepath}: {e}")
            return False
            
    def file_exists(self, filepath: str) -> bool:
        """Check if file exists"""
        return os.path.exists(filepath)
        
    def get_file_size(self, filepath: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(filepath)
        except Exception:
            return 0
            
    def delete_file(self, filepath: str, create_backup: bool = True) -> bool:
        """Safely delete file with optional backup"""
        if not os.path.exists(filepath):
            self.logger.warning(f"File does not exist: {filepath}")
            return False
            
        if create_backup:
            self._create_backup(filepath)
            
        try:
            os.remove(filepath)
            self.logger.info(f"Deleted file: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete file {filepath}: {e}")
            return False
            
    def cleanup_backups(self, max_age_days: int = 7) -> int:
        """Clean up old backup files"""
        cleaned_count = 0
        backup_dirs = []
        
        # Find all backup directories
        for root, dirs, files in os.walk('.'):
            if '.aurora_backups' in dirs:
                backup_dirs.append(os.path.join(root, '.aurora_backups'))
                
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 3600
        
        for backup_dir in backup_dirs:
            try:
                for filename in os.listdir(backup_dir):
                    filepath = os.path.join(backup_dir, filename)
                    if os.path.isfile(filepath):
                        file_age = current_time - os.path.getmtime(filepath)
                        if file_age > max_age_seconds:
                            os.remove(filepath)
                            cleaned_count += 1
                            self.logger.debug(f"Cleaned old backup: {filepath}")
            except Exception as e:
                self.logger.error(f"Error cleaning backup directory {backup_dir}: {e}")
                
        if cleaned_count > 0:
            self.logger.info(f"Cleaned {cleaned_count} old backup files")
            
        return cleaned_count