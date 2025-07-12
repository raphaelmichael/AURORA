"""
Test suite for Aurora core modules
"""
import pytest
import tempfile
import shutil
import json
import time
from pathlib import Path

def test_imports():
    """Test that all Aurora modules can be imported"""
    from aurora.config import ConfigManager
    from aurora.logging import setup_logging, AuroraLogger
    from aurora.monitoring import ResourceMonitor
    from aurora.backup import BackupManager
    
    assert ConfigManager is not None
    assert setup_logging is not None
    assert AuroraLogger is not None
    assert ResourceMonitor is not None
    assert BackupManager is not None

def test_config_manager():
    """Test ConfigManager functionality"""
    from aurora.config import ConfigManager
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
aurora:
  name: "Test Aurora"
  version: "2.0"
  logging:
    level: "DEBUG"
""")
        config_path = f.name
    
    try:
        config = ConfigManager(config_path)
        
        # Test getting values
        assert config.get("aurora.name") == "Test Aurora"
        assert config.get("aurora.version") == "2.0"
        assert config.get("aurora.logging.level") == "DEBUG"
        assert config.get("nonexistent.key", "default") == "default"
        
        # Test setting values
        config.set("aurora.test", "value")
        assert config.get("aurora.test") == "value"
        
    finally:
        Path(config_path).unlink()

def test_aurora_logger():
    """Test AuroraLogger functionality"""
    from aurora.logging import AuroraLogger
    
    logger = AuroraLogger("test")
    
    # Test context management
    logger.push_context({"test": "value"})
    context = logger.get_current_context()
    assert context["test"] == "value"
    
    popped = logger.pop_context()
    assert popped["test"] == "value"
    assert logger.get_current_context() == {}
    
    # Test cycle management
    logger.set_cycle(5)
    assert logger.cycle_count == 5

def test_resource_monitor():
    """Test ResourceMonitor functionality"""
    from aurora.monitoring import ResourceMonitor
    
    config = {
        "monitoring": {
            "cpu_threshold": 80.0,
            "memory_threshold": 80.0,
            "disk_threshold": 90.0,
            "check_interval": 1
        }
    }
    
    monitor = ResourceMonitor(config)
    
    # Test metric collection
    cpu_usage = monitor.get_cpu_usage()
    assert isinstance(cpu_usage, float)
    assert 0 <= cpu_usage <= 100
    
    memory_usage = monitor.get_memory_usage()
    assert "percent" in memory_usage
    assert "used_mb" in memory_usage
    assert "available_mb" in memory_usage
    
    disk_usage = monitor.get_disk_usage()
    assert "percent" in disk_usage
    assert "used_gb" in disk_usage
    assert "free_gb" in disk_usage
    
    process_info = monitor.get_process_info()
    assert "pid" in process_info
    assert "cpu_percent" in process_info
    assert "memory_mb" in process_info
    
    # Test system health check
    health = monitor.is_system_healthy()
    assert isinstance(health, bool)

def test_backup_manager():
    """Test BackupManager functionality"""
    from aurora.backup import BackupManager
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test data directory
        data_dir = temp_path / "data"
        data_dir.mkdir()
        
        # Create test files
        memory_file = data_dir / "aurora_memory.json"
        memory_file.write_text('{"evolution_count": 5}')
        
        code_file = data_dir / "aurora_self_writing.py"
        code_file.write_text('print("Hello Aurora")')
        
        config = {
            "backup": {
                "enabled": True,
                "backup_dir": str(temp_path / "backups"),
                "compression": False,
                "max_backups": 5
            },
            "files": {
                "memory": str(memory_file),
                "code": str(code_file)
            }
        }
        
        backup_manager = BackupManager(config)
        
        # Test backup creation
        backup_path = backup_manager.create_backup(evolution_count=5, backup_type="test")
        assert backup_path is not None
        assert Path(backup_path).exists()
        
        # Test backup listing
        backups = backup_manager.list_backups()
        assert len(backups) >= 1
        
        # Test backup size calculation
        size_info = backup_manager.get_backup_size()
        assert "total_size_mb" in size_info
        assert "backup_count" in size_info

if __name__ == "__main__":
    pytest.main([__file__, "-v"])