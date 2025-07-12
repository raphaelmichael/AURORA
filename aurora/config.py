"""
Aurora Configuration Manager
Handles YAML/JSON configuration with hot-reload capability
"""
import os
import yaml
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import time
from threading import Thread, Lock

logger = logging.getLogger(__name__)

class ConfigManager:
    """Centralized configuration management with hot-reload"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.last_modified = 0
        self.lock = Lock()
        self.hot_reload_enabled = False
        self.reload_thread: Optional[Thread] = None
        
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Configuration file {self.config_path} not found, using defaults")
                self.config = self._get_default_config()
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.suffix.lower() == '.json':
                    self.config = json.load(f)
                else:
                    self.config = yaml.safe_load(f) or {}
            
            # Expand environment variables
            self.config = self._expand_env_vars(self.config)
            self.last_modified = self.config_path.stat().st_mtime
            logger.info(f"Configuration loaded from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = self._get_default_config()
    
    def _expand_env_vars(self, obj: Any) -> Any:
        """Recursively expand environment variables in configuration"""
        if isinstance(obj, dict):
            return {k: self._expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        return obj
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        with self.lock:
            keys = key.split('.')
            value = self.config
            
            try:
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        with self.lock:
            keys = key.split('.')
            config = self.config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with self.lock:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    if self.config_path.suffix.lower() == '.json':
                        json.dump(self.config, f, indent=2)
                    else:
                        yaml.dump(self.config, f, default_flow_style=False, indent=2)
                logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def enable_hot_reload(self, check_interval: float = 1.0) -> None:
        """Enable hot-reload of configuration file"""
        if self.hot_reload_enabled:
            return
            
        self.hot_reload_enabled = True
        self.reload_thread = Thread(target=self._hot_reload_worker, args=(check_interval,), daemon=True)
        self.reload_thread.start()
        logger.info("Configuration hot-reload enabled")
    
    def disable_hot_reload(self) -> None:
        """Disable hot-reload"""
        self.hot_reload_enabled = False
        if self.reload_thread:
            self.reload_thread.join(timeout=1.0)
        logger.info("Configuration hot-reload disabled")
    
    def _hot_reload_worker(self, check_interval: float) -> None:
        """Background worker for hot-reload"""
        while self.hot_reload_enabled:
            try:
                if self.config_path.exists():
                    current_mtime = self.config_path.stat().st_mtime
                    if current_mtime > self.last_modified:
                        logger.info("Configuration file changed, reloading...")
                        self.load_config()
                time.sleep(check_interval)
            except Exception as e:
                logger.error(f"Error in hot-reload worker: {e}")
                time.sleep(check_interval)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aurora": {
                "name": "Aurora",
                "version": "2.0",
                "logging": {
                    "level": "INFO",
                    "format": "json",
                    "file": "logs/aurora.log",
                    "max_size": "10MB",
                    "backup_count": 5,
                    "rotation": True
                },
                "files": {
                    "memory": "data/aurora_memory.json",
                    "consciousness": "data/aurora_consciousness.py",
                    "code": "data/aurora_self_writing.py",
                    "backup_dir": "backups"
                },
                "execution": {
                    "cycle_interval": 2.0,
                    "consciousness_lines": 1000000,
                    "max_comments": 50,
                    "api_timeout": 5
                },
                "monitoring": {
                    "cpu_threshold": 80.0,
                    "memory_threshold": 80.0,
                    "disk_threshold": 90.0,
                    "check_interval": 30
                },
                "backup": {
                    "enabled": True,
                    "before_evolution": True,
                    "max_backups": 10,
                    "compression": True
                },
                "validation": {
                    "enabled": True,
                    "ast_check": True,
                    "syntax_check": True
                },
                "anomaly_detection": {
                    "enabled": True,
                    "cycle_time_threshold": 10.0,
                    "memory_growth_threshold": 50.0,
                    "error_rate_threshold": 0.1
                }
            }
        }
    
    def get_aurora_config(self) -> Dict[str, Any]:
        """Get Aurora-specific configuration"""
        return self.get("aurora", {})
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access"""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dict-like assignment"""
        self.set(key, value)