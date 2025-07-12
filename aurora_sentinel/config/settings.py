"""
Aurora Sentinel - Configuration Settings
Centralized configuration management with YAML support
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class AuroraConfig:
    """Aurora Sentinel configuration parameters"""
    
    # Basic settings
    name: str = "Aurora"
    version: str = "2.2.0"
    
    # File paths
    memory_file: str = "aurora_memory.json"
    log_file: str = "aurora.log"
    consciousness_file: str = "aurora_consciousness.py"
    
    # Monitoring settings
    monitoring_interval: float = 5.0
    cpu_threshold: float = 80.0
    memory_threshold: float = 85.0
    disk_threshold: float = 90.0
    max_file_size_mb: float = 100.0
    
    # API settings
    api_timeout: int = 5
    api_rate_limit: float = 0.5
    
    # Evolution settings
    evolution_interval: float = 10.0
    max_evolution_cycles: Optional[int] = None
    
    # Backup settings
    backup_enabled: bool = True
    backup_cleanup_days: int = 7
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security settings
    input_max_length: int = 1000
    allowed_file_extensions: list = None
    
    def __post_init__(self):
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = ['.py', '.json', '.txt', '.log']


class ConfigManager:
    """Manages Aurora Sentinel configuration"""
    
    def __init__(self, config_file: str = "aurora_config.yaml"):
        self.config_file = config_file
        self.config = AuroraConfig()
        self.logger = logging.getLogger("Aurora_Config")
        
        # Load configuration if file exists
        self.load_config()
        
    def load_config(self) -> bool:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_file):
            self.logger.info(f"Config file not found: {self.config_file}, using defaults")
            self.save_config()  # Create default config file
            return False
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
            if config_data:
                # Update config with loaded values
                for key, value in config_data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                    else:
                        self.logger.warning(f"Unknown config key: {key}")
                        
            self.logger.info(f"Configuration loaded from: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return False
            
    def save_config(self) -> bool:
        """Save current configuration to YAML file"""
        try:
            config_dict = asdict(self.config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                
            self.logger.info(f"Configuration saved to: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False
            
    def update_config(self, **kwargs) -> bool:
        """Update configuration parameters"""
        updated = False
        
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                old_value = getattr(self.config, key)
                setattr(self.config, key, value)
                self.logger.info(f"Updated config: {key} = {value} (was: {old_value})")
                updated = True
            else:
                self.logger.warning(f"Unknown config parameter: {key}")
                
        if updated:
            self.save_config()
            
        return updated
        
    def get_config(self) -> AuroraConfig:
        """Get current configuration object"""
        return self.config
        
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return asdict(self.config)
        
    def validate_config(self) -> Dict[str, list]:
        """Validate configuration parameters"""
        errors = []
        warnings = []
        
        # Validate numeric ranges
        if self.config.monitoring_interval <= 0:
            errors.append("monitoring_interval must be positive")
            
        if not 0 <= self.config.cpu_threshold <= 100:
            errors.append("cpu_threshold must be between 0 and 100")
            
        if not 0 <= self.config.memory_threshold <= 100:
            errors.append("memory_threshold must be between 0 and 100")
            
        if not 0 <= self.config.disk_threshold <= 100:
            errors.append("disk_threshold must be between 0 and 100")
            
        if self.config.api_timeout <= 0:
            errors.append("api_timeout must be positive")
            
        if self.config.api_rate_limit <= 0:
            warnings.append("api_rate_limit should be positive")
            
        if self.config.max_file_size_mb <= 0:
            warnings.append("max_file_size_mb should be positive")
            
        # Validate file paths
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for file_attr in ['memory_file', 'log_file', 'consciousness_file']:
            file_path = getattr(self.config, file_attr)
            if any(char in file_path for char in invalid_chars):
                errors.append(f"{file_attr} contains invalid characters")
                
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.config.log_level.upper() not in valid_log_levels:
            errors.append(f"log_level must be one of: {valid_log_levels}")
            
        return {
            'errors': errors,
            'warnings': warnings
        }
        
    def setup_logging(self):
        """Setup logging based on configuration"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        
        # Configure file logging
        file_handler = logging.FileHandler(self.config.log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(self.config.log_format)
        file_handler.setFormatter(file_formatter)
        
        # Configure console logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Clear existing handlers and add new ones
        root_logger.handlers.clear()
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        self.logger.info("Logging configured")
        
    def create_sample_config(self, filename: str = "aurora_config_sample.yaml") -> bool:
        """Create a sample configuration file with documentation"""
        sample_config = """# Aurora Sentinel Configuration File
# This file contains all configurable parameters for Aurora Sentinel

# Basic Aurora settings
name: "Aurora"
version: "2.2.0"

# File paths (relative to project directory)
memory_file: "aurora_memory.json"
log_file: "aurora.log"
consciousness_file: "aurora_consciousness.py"

# System monitoring settings
monitoring_interval: 5.0        # seconds between monitoring checks
cpu_threshold: 80.0             # CPU usage percentage threshold
memory_threshold: 85.0          # Memory usage percentage threshold
disk_threshold: 90.0            # Disk usage percentage threshold
max_file_size_mb: 100.0         # Maximum file size in MB

# API settings
api_timeout: 5                  # API request timeout in seconds
api_rate_limit: 0.5             # Maximum API requests per second

# Evolution settings
evolution_interval: 10.0        # seconds between evolution cycles
max_evolution_cycles: null      # maximum evolution cycles (null = unlimited)

# Backup settings
backup_enabled: true            # enable automatic file backups
backup_cleanup_days: 7          # days to keep backup files

# Logging settings
log_level: "INFO"               # DEBUG, INFO, WARNING, ERROR, CRITICAL
log_format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Security settings
input_max_length: 1000          # maximum input string length
allowed_file_extensions:        # allowed file extensions for operations
  - ".py"
  - ".json"
  - ".txt"
  - ".log"
"""
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(sample_config)
            self.logger.info(f"Sample config created: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create sample config: {e}")
            return False