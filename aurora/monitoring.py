"""
Aurora Resource Monitoring Module
Monitors CPU, memory, and disk usage with alerts
"""
import os
import psutil
import time
import threading
from typing import Dict, Any, Callable, Optional
from pathlib import Path

class ResourceMonitor:
    """Monitor system resources and trigger alerts"""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config.get("monitoring", {})
        self.logger = logger
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.alert_callbacks: Dict[str, Callable] = {}
        
        # Thresholds
        self.cpu_threshold = self.config.get("cpu_threshold", 80.0)
        self.memory_threshold = self.config.get("memory_threshold", 80.0)
        self.disk_threshold = self.config.get("disk_threshold", 90.0)
        self.check_interval = self.config.get("check_interval", 30)
        
        # Alert tracking to avoid spam
        self.last_alerts = {}
        self.alert_cooldown = 300  # 5 minutes
    
    def add_alert_callback(self, resource: str, callback: Callable[[str, float, float], None]) -> None:
        """Add callback for resource alerts"""
        self.alert_callbacks[resource] = callback
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage information"""
        memory = psutil.virtual_memory()
        return {
            "percent": memory.percent,
            "used_mb": memory.used / (1024 * 1024),
            "available_mb": memory.available / (1024 * 1024),
            "total_mb": memory.total / (1024 * 1024)
        }
    
    def get_disk_usage(self, path: str = ".") -> Dict[str, float]:
        """Get disk usage for specified path"""
        usage = psutil.disk_usage(path)
        return {
            "percent": (usage.used / usage.total) * 100,
            "used_gb": usage.used / (1024 * 1024 * 1024),
            "free_gb": usage.free / (1024 * 1024 * 1024),
            "total_gb": usage.total / (1024 * 1024 * 1024)
        }
    
    def get_process_info(self) -> Dict[str, Any]:
        """Get current process information"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "pid": process.pid,
            "cpu_percent": process.cpu_percent(),
            "memory_mb": memory_info.rss / (1024 * 1024),
            "memory_percent": process.memory_percent(),
            "num_threads": process.num_threads(),
            "create_time": process.create_time(),
            "status": process.status()
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all system metrics"""
        return {
            "timestamp": time.time(),
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "process": self.get_process_info()
        }
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> None:
        """Check if any metrics exceed thresholds"""
        current_time = time.time()
        
        # Check CPU
        cpu_usage = metrics["cpu"]
        if cpu_usage > self.cpu_threshold:
            self._trigger_alert("cpu", cpu_usage, self.cpu_threshold, current_time)
        
        # Check memory
        memory_usage = metrics["memory"]["percent"]
        if memory_usage > self.memory_threshold:
            self._trigger_alert("memory", memory_usage, self.memory_threshold, current_time)
        
        # Check disk
        disk_usage = metrics["disk"]["percent"]
        if disk_usage > self.disk_threshold:
            self._trigger_alert("disk", disk_usage, self.disk_threshold, current_time)
    
    def _trigger_alert(self, resource: str, usage: float, threshold: float, current_time: float) -> None:
        """Trigger alert for resource threshold breach"""
        # Check cooldown
        last_alert_time = self.last_alerts.get(resource, 0)
        if current_time - last_alert_time < self.alert_cooldown:
            return
        
        self.last_alerts[resource] = current_time
        
        # Log alert
        if self.logger:
            self.logger.resource_alert(resource, usage, threshold)
        
        # Call registered callback
        callback = self.alert_callbacks.get(resource)
        if callback:
            try:
                callback(resource, usage, threshold)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in alert callback for {resource}: {e}")
    
    def start_monitoring(self) -> None:
        """Start background monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        if self.logger:
            self.logger.info("Resource monitoring started", event_type="monitoring_start")
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        if self.logger:
            self.logger.info("Resource monitoring stopped", event_type="monitoring_stop")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self.running:
            try:
                metrics = self.get_all_metrics()
                self.check_thresholds(metrics)
                
                # Log metrics periodically (every 10 checks)
                if hasattr(self, '_check_count'):
                    self._check_count += 1
                else:
                    self._check_count = 1
                
                if self._check_count % 10 == 0 and self.logger:
                    self.logger.debug("Resource metrics", 
                                    event_type="resource_metrics",
                                    cpu_usage=metrics["cpu"],
                                    memory_usage=metrics["memory"]["percent"],
                                    context=metrics)
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        return {
            "platform": {
                "system": psutil.WINDOWS if os.name == 'nt' else "unix",
                "cpu_count": psutil.cpu_count(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "boot_time": psutil.boot_time()
            },
            "memory": {
                "total_gb": psutil.virtual_memory().total / (1024 * 1024 * 1024),
                "swap_total_gb": psutil.swap_memory().total / (1024 * 1024 * 1024) if psutil.swap_memory().total > 0 else 0
            },
            "disk": {
                "partitions": [
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": psutil.disk_usage(partition.mountpoint).total / (1024 * 1024 * 1024)
                    }
                    for partition in psutil.disk_partitions()
                ]
            }
        }
    
    def check_disk_space(self, required_gb: float, path: str = ".") -> bool:
        """Check if there's enough disk space"""
        disk_info = self.get_disk_usage(path)
        return disk_info["free_gb"] >= required_gb
    
    def estimate_memory_growth(self, window_size: int = 10) -> float:
        """Estimate memory growth rate (requires history tracking)"""
        # This would require implementing a history buffer
        # For now, return current memory usage
        return self.get_memory_usage()["percent"]
    
    def is_system_healthy(self) -> bool:
        """Check if system is within healthy resource limits"""
        metrics = self.get_all_metrics()
        
        return (
            metrics["cpu"] < self.cpu_threshold and
            metrics["memory"]["percent"] < self.memory_threshold and
            metrics["disk"]["percent"] < self.disk_threshold
        )