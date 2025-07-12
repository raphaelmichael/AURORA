"""
Aurora Structured Logging Module
Provides JSON-based logging with rotation and contextual information
"""
import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra context if available
        if hasattr(record, 'cycle'):
            log_entry['cycle'] = record.cycle
        if hasattr(record, 'event_type'):
            log_entry['event_type'] = record.event_type
        if hasattr(record, 'context'):
            log_entry['context'] = record.context
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
        if hasattr(record, 'memory_usage'):
            log_entry['memory_usage'] = record.memory_usage
        if hasattr(record, 'cpu_usage'):
            log_entry['cpu_usage'] = record.cpu_usage
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        return json.dumps(log_entry, ensure_ascii=False)

class AuroraLogger:
    """Aurora-specific logger with contextual information"""
    
    def __init__(self, name: str = "aurora"):
        self.logger = logging.getLogger(name)
        self.cycle_count = 0
        self.context_stack = []
    
    def set_cycle(self, cycle: int) -> None:
        """Set current cycle number"""
        self.cycle_count = cycle
    
    def push_context(self, context: Dict[str, Any]) -> None:
        """Push context onto stack"""
        self.context_stack.append(context)
    
    def pop_context(self) -> Optional[Dict[str, Any]]:
        """Pop context from stack"""
        return self.context_stack.pop() if self.context_stack else None
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get current context"""
        context = {}
        for ctx in self.context_stack:
            context.update(ctx)
        return context
    
    def _log_with_context(self, level: int, message: str, event_type: str = None, 
                         duration: float = None, memory_usage: float = None, 
                         cpu_usage: float = None, **kwargs) -> None:
        """Log with Aurora context"""
        extra = {
            'cycle': self.cycle_count,
            'context': self.get_current_context(),
        }
        
        if event_type:
            extra['event_type'] = event_type
        if duration is not None:
            extra['duration'] = duration
        if memory_usage is not None:
            extra['memory_usage'] = memory_usage
        if cpu_usage is not None:
            extra['cpu_usage'] = cpu_usage
        
        extra.update(kwargs)
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs) -> None:
        """Debug log with context"""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Info log with context"""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Warning log with context"""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Error log with context"""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Critical log with context"""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def cycle_start(self, cycle: int) -> None:
        """Log cycle start"""
        self.set_cycle(cycle)
        self.info(f"Aurora cycle {cycle} started", event_type="cycle_start")
    
    def cycle_end(self, cycle: int, duration: float) -> None:
        """Log cycle end"""
        self.info(f"Aurora cycle {cycle} completed", 
                 event_type="cycle_end", duration=duration)
    
    def evolution(self, evolution_count: int) -> None:
        """Log evolution event"""
        self.info(f"Aurora evolved to version {evolution_count}", 
                 event_type="evolution")
    
    def api_call(self, api_name: str, success: bool, duration: float) -> None:
        """Log API call"""
        status = "success" if success else "failure"
        self.info(f"API call to {api_name}: {status}", 
                 event_type="api_call", duration=duration)
    
    def backup_created(self, backup_path: str, size: int) -> None:
        """Log backup creation"""
        self.info(f"Backup created at {backup_path} ({size} bytes)", 
                 event_type="backup_created")
    
    def anomaly_detected(self, anomaly_type: str, details: Dict[str, Any]) -> None:
        """Log anomaly detection"""
        self.warning(f"Anomaly detected: {anomaly_type}", 
                    event_type="anomaly_detected", context=details)
    
    def resource_alert(self, resource: str, usage: float, threshold: float) -> None:
        """Log resource usage alert"""
        self.warning(f"{resource} usage {usage:.1f}% exceeds threshold {threshold:.1f}%", 
                    event_type="resource_alert")

def setup_logging(config: Dict[str, Any]) -> AuroraLogger:
    """Setup Aurora logging system"""
    log_config = config.get("logging", {})
    
    # Create logs directory
    log_file = Path(log_config.get("file", "logs/aurora.log"))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Parse log level
    level = getattr(logging, log_config.get("level", "INFO").upper())
    
    # Create formatter
    if log_config.get("format", "json") == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Setup file handler with rotation
    if log_config.get("rotation", True):
        max_size = log_config.get("max_size", "10MB")
        # Convert size string to bytes
        if max_size.endswith("MB"):
            max_bytes = int(max_size[:-2]) * 1024 * 1024
        elif max_size.endswith("KB"):
            max_bytes = int(max_size[:-2]) * 1024
        else:
            max_bytes = int(max_size)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=log_config.get("backup_count", 5),
            encoding='utf-8'
        )
    else:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
    
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create Aurora logger
    aurora_logger = AuroraLogger("aurora")
    aurora_logger.info("Aurora logging system initialized", event_type="system_start")
    
    return aurora_logger

def get_logger(name: str = "aurora") -> AuroraLogger:
    """Get Aurora logger instance"""
    return AuroraLogger(name)