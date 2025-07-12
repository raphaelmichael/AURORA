"""
Test suite for Aurora validation module
"""
import pytest
from aurora.validation import CodeValidator

def test_code_validator_basic():
    """Test basic code validation functionality"""
    validator = CodeValidator()
    
    # Test valid code
    valid_code = '''
def hello():
    print("Hello Aurora")
    return True

if __name__ == "__main__":
    hello()
'''
    
    is_valid, errors = validator.validate_code(valid_code)
    assert is_valid == True
    assert len(errors) == 0

def test_code_validator_syntax_error():
    """Test validation with syntax errors"""
    validator = CodeValidator()
    
    # Test invalid syntax
    invalid_code = '''
def hello(:
    print("Hello Aurora"
    return True
'''
    
    is_valid, errors = validator.validate_code(invalid_code)
    assert is_valid == False
    assert len(errors) > 0
    assert "Syntax error" in errors[0]

def test_code_validator_dangerous_functions():
    """Test validation of dangerous function calls"""
    validator = CodeValidator()
    
    # Test dangerous function
    dangerous_code = '''
import os
os.system("rm -rf /")
eval("malicious code")
'''
    
    is_valid, errors = validator.validate_code(dangerous_code)
    assert is_valid == False
    assert len(errors) > 0

def test_code_validator_evolution():
    """Test evolution validation"""
    validator = CodeValidator()
    
    old_code = '''
def evolve():
    print("Original")

def run():
    print("Running")
'''
    
    new_code = '''
def evolve():
    print("Evolved")
    # New comment added
    
def run():
    print("Running enhanced")
'''
    
    is_valid, errors = validator.validate_evolution_code(old_code, new_code)
    assert is_valid == True
    assert len(errors) == 0

def test_code_metrics():
    """Test code metrics calculation"""
    validator = CodeValidator()
    
    code = '''
import sys
import os

class TestClass:
    def method1(self):
        if True:
            print("test")

def function1():
    for i in range(10):
        try:
            print(i)
        except:
            pass

def function2():
    while True:
        break
'''
    
    metrics = validator.get_code_metrics(code)
    
    assert "lines" in metrics
    assert "functions" in metrics
    assert "classes" in metrics
    assert "imports" in metrics
    assert "complexity" in metrics
    
    assert metrics["functions"] == 3  # method1, function1, function2
    assert metrics["classes"] == 1
    assert metrics["imports"] == 2

def test_safe_code_template():
    """Test safe code template generation"""
    validator = CodeValidator()
    
    template = validator.create_safe_code_template(5)
    
    assert "evolution_count = 5" in template
    assert "def safe_evolve():" in template
    assert "def get_status():" in template
    
    # Validate the template itself
    is_valid, errors = validator.validate_code(template)
    assert is_valid == True
    assert len(errors) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])