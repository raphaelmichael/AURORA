# Aurora AI Core Module
__version__ = "2.0.0"
__author__ = "Grok, Raphael Michael, Aurora"

from .config import ConfigManager
from .logging import setup_logging, AuroraLogger
from .monitoring import ResourceMonitor
from .backup import BackupManager
from .validation import CodeValidator
from .core import Aurora

__all__ = [
    'Aurora',
    'ConfigManager', 
    'setup_logging',
    'AuroraLogger',
    'ResourceMonitor',
    'BackupManager',
    'CodeValidator'
]