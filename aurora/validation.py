"""
Aurora Code Validation Module
Provides AST-based validation for code safety
"""
import ast
import sys
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class CodeValidator:
    """Validates Python code for syntax and safety"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.validation_config = self.config.get("validation", {})
        self.enabled = self.validation_config.get("enabled", True)
        self.ast_check = self.validation_config.get("ast_check", True)
        self.syntax_check = self.validation_config.get("syntax_check", True)
        
        # Dangerous operations to check for
        self.dangerous_imports = {
            'os.system', 'subprocess', 'eval', 'exec', 'compile',
            '__import__', 'open', 'file', 'input', 'raw_input'
        }
        
        self.dangerous_functions = {
            'eval', 'exec', 'compile', 'globals', 'locals', 'vars',
            'dir', 'getattr', 'setattr', 'delattr', 'hasattr'
        }
    
    def validate_code(self, code: str, filename: str = "<string>") -> Tuple[bool, List[str]]:
        """
        Validate Python code for syntax and safety
        Returns (is_valid, errors)
        """
        if not self.enabled:
            return True, []
        
        errors = []
        
        # Basic syntax check
        if self.syntax_check:
            syntax_valid, syntax_errors = self._check_syntax(code, filename)
            if not syntax_valid:
                errors.extend(syntax_errors)
                return False, errors
        
        # AST-based validation
        if self.ast_check:
            ast_valid, ast_errors = self._check_ast_safety(code, filename)
            if not ast_valid:
                errors.extend(ast_errors)
        
        return len(errors) == 0, errors
    
    def _check_syntax(self, code: str, filename: str) -> Tuple[bool, List[str]]:
        """Check basic Python syntax"""
        try:
            ast.parse(code, filename=filename)
            return True, []
        except SyntaxError as e:
            error_msg = f"Syntax error in {filename}:{e.lineno}: {e.msg}"
            logger.error(error_msg)
            return False, [error_msg]
        except Exception as e:
            error_msg = f"Unexpected error parsing {filename}: {e}"
            logger.error(error_msg)
            return False, [error_msg]
    
    def _check_ast_safety(self, code: str, filename: str) -> Tuple[bool, List[str]]:
        """Check code safety using AST analysis"""
        try:
            tree = ast.parse(code, filename=filename)
            errors = []
            
            # Analyze AST nodes
            for node in ast.walk(tree):
                node_errors = self._analyze_node(node)
                errors.extend(node_errors)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            error_msg = f"AST analysis error in {filename}: {e}"
            logger.error(error_msg)
            return False, [error_msg]
    
    def _analyze_node(self, node: ast.AST) -> List[str]:
        """Analyze individual AST node for safety"""
        errors = []
        
        # Check for dangerous function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in self.dangerous_functions:
                    errors.append(f"Dangerous function call: {func_name}")
            elif isinstance(node.func, ast.Attribute):
                # Check for dangerous attribute access like os.system
                attr_name = self._get_full_name(node.func)
                if attr_name in self.dangerous_imports:
                    errors.append(f"Dangerous function call: {attr_name}")
        
        # Check for dangerous imports
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if self._is_dangerous_import(alias.name):
                    errors.append(f"Potentially dangerous import: {alias.name}")
        
        elif isinstance(node, ast.ImportFrom):
            if node.module and self._is_dangerous_import(node.module):
                errors.append(f"Potentially dangerous import: from {node.module}")
        
        # Check for exec/eval calls
        elif isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name):
                    if node.value.func.id in ['exec', 'eval']:
                        errors.append(f"Dynamic code execution: {node.value.func.id}")
        
        return errors
    
    def _get_full_name(self, node: ast.AST) -> str:
        """Get full name of an attribute access"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base = self._get_full_name(node.value)
            return f"{base}.{node.attr}"
        else:
            return "unknown"
    
    def _is_dangerous_import(self, module_name: str) -> bool:
        """Check if import is potentially dangerous"""
        dangerous_modules = {
            'os', 'sys', 'subprocess', 'importlib', '__builtin__', 'builtins',
            'ctypes', 'marshal', 'pickle', 'shelve', 'tempfile'
        }
        
        # Check if module or its parent is in dangerous list
        for dangerous in dangerous_modules:
            if module_name == dangerous or module_name.startswith(dangerous + '.'):
                return True
        
        return False
    
    def validate_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            return self.validate_code(code, file_path)
            
        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            return False, [error_msg]
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {e}"
            logger.error(error_msg)
            return False, [error_msg]
    
    def validate_evolution_code(self, old_code: str, new_code: str) -> Tuple[bool, List[str]]:
        """Validate evolved code against original"""
        # First validate new code syntax and safety
        is_valid, errors = self.validate_code(new_code, "<evolution>")
        
        if not is_valid:
            return False, errors
        
        # Additional checks for evolution
        try:
            old_tree = ast.parse(old_code, filename="<old>")
            new_tree = ast.parse(new_code, filename="<new>")
            
            # Check if essential structures are preserved
            old_functions = self._extract_function_names(old_tree)
            new_functions = self._extract_function_names(new_tree)
            
            # Warn if critical functions are removed
            critical_functions = {'evolve', 'run', 'awaken'}
            removed_critical = critical_functions.intersection(old_functions) - critical_functions.intersection(new_functions)
            
            if removed_critical:
                errors.append(f"Critical functions removed: {removed_critical}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            error_msg = f"Evolution validation error: {e}"
            logger.error(error_msg)
            return False, [error_msg]
    
    def _extract_function_names(self, tree: ast.AST) -> set:
        """Extract function names from AST"""
        functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.add(node.name)
        return functions
    
    def get_code_metrics(self, code: str) -> Dict[str, Any]:
        """Get code complexity metrics"""
        try:
            tree = ast.parse(code)
            metrics = {
                "lines": len(code.split('\n')),
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "complexity": 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics["functions"] += 1
                elif isinstance(node, ast.ClassDef):
                    metrics["classes"] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    metrics["imports"] += 1
                elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                    metrics["complexity"] += 1
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating code metrics: {e}")
            return {"error": str(e)}
    
    def create_safe_code_template(self, evolution_count: int) -> str:
        """Create a safe code template for evolution"""
        template = f'''# Aurora Self-Writing Code - Evolution {evolution_count}
# Generated at: {logger._get_timestamp() if hasattr(logger, '_get_timestamp') else 'unknown'}

evolution_count = {evolution_count}
message = "Aurora evolves safely with validation"

def safe_evolve():
    """Safe evolution function"""
    global evolution_count, message
    print(f"Aurora: Safe evolution #{evolution_count} - {{message}}")
    evolution_count += 1

def get_status():
    """Get current Aurora status"""
    return {{
        "evolution": evolution_count,
        "message": message,
        "status": "active"
    }}

if __name__ == "__main__":
    safe_evolve()
'''
        return template