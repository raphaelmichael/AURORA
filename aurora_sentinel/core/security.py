"""
Aurora Sentinel - Security Module
Handles validation, error handling, and safe operations
"""

import ast
import signal
import sys
import time
import logging
import hashlib
import json
from typing import List, Dict, Any, Optional, Callable
from contextlib import contextmanager


class SecurityManager:
    """Manages security, validation and safe operations"""
    
    def __init__(self):
        self.logger = logging.getLogger("Aurora_Security")
        self.signal_handlers = {}
        self._setup_signal_handlers()
        
    def _setup_signal_handlers(self):
        """Sets up graceful signal handling"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            print(f"\n⏹️ Aurora: Recebido sinal de término. Finalizando graciosamente...")
            # Call registered cleanup functions
            for name, handler in self.signal_handlers.items():
                try:
                    handler()
                    self.logger.info(f"Cleanup handler '{name}' executed successfully")
                except Exception as e:
                    self.logger.error(f"Error in cleanup handler '{name}': {e}")
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def register_cleanup_handler(self, name: str, handler: Callable):
        """Registers a cleanup function to be called on shutdown"""
        self.signal_handlers[name] = handler
        self.logger.info(f"Registered cleanup handler: {name}")
        
    def validate_code_syntax(self, code: str) -> bool:
        """Validates Python code syntax using AST"""
        if not code or not code.strip():
            self.logger.warning("Empty code provided for validation")
            return False
            
        try:
            ast.parse(code)
            self.logger.debug("Code syntax validation passed")
            return True
        except SyntaxError as e:
            self.logger.error(f"Code syntax validation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error in code validation: {e}")
            return False
            
    def validate_json_data(self, data: str) -> bool:
        """Validates JSON data structure"""
        if not data:
            return False
            
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON validation failed: {e}")
            return False
            
    def sanitize_input(self, user_input: str, max_length: int = 1000) -> str:
        """Sanitizes user input for safety"""
        if not user_input:
            return ""
            
        # Remove dangerous characters and limit length
        sanitized = user_input.strip()[:max_length]
        
        # Remove potential code injection patterns
        dangerous_patterns = ['__import__', 'exec(', 'eval(', 'os.system', 'subprocess']
        for pattern in dangerous_patterns:
            if pattern in sanitized.lower():
                self.logger.warning(f"Dangerous pattern detected and removed: {pattern}")
                sanitized = sanitized.replace(pattern, "[FILTERED]")
                
        return sanitized
        
    def calculate_checksum(self, data: str) -> str:
        """Calculates SHA256 checksum for data integrity"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
        
    def verify_checksum(self, data: str, expected_checksum: str) -> bool:
        """Verifies data integrity using checksum"""
        actual_checksum = self.calculate_checksum(data)
        return actual_checksum == expected_checksum
        
    @contextmanager
    def safe_operation(self, operation_name: str):
        """Context manager for safe operations with error handling"""
        self.logger.info(f"Starting safe operation: {operation_name}")
        try:
            yield
            self.logger.info(f"Safe operation completed: {operation_name}")
        except Exception as e:
            self.logger.error(f"Error in safe operation '{operation_name}': {e}")
            raise
        finally:
            self.logger.debug(f"Safe operation cleanup: {operation_name}")
            
    def validate_file_path(self, file_path: str, allowed_extensions: List[str] = None) -> bool:
        """Validates file paths for security"""
        if not file_path:
            return False
            
        # Check for path traversal attempts
        if ".." in file_path or file_path.startswith("/"):
            self.logger.warning(f"Potentially dangerous file path: {file_path}")
            return False
            
        # Check file extension if specified
        if allowed_extensions:
            extension = file_path.split('.')[-1].lower()
            if extension not in [ext.lower() for ext in allowed_extensions]:
                self.logger.warning(f"File extension not allowed: {extension}")
                return False
                
        return True
        
    def create_backup_name(self, original_name: str) -> str:
        """Creates a safe backup filename"""
        timestamp = str(int(time.time()))
        name_parts = original_name.rsplit('.', 1)
        if len(name_parts) == 2:
            return f"{name_parts[0]}_backup_{timestamp}.{name_parts[1]}"
        else:
            return f"{original_name}_backup_{timestamp}"