"""
Aurora Sentinel - Monitoring Module
System resource monitoring and health checks
"""

import psutil
import time
import logging
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class ResourceThresholds:
    """Resource usage thresholds for monitoring"""
    cpu_percent: float = 80.0
    memory_percent: float = 85.0
    disk_percent: float = 90.0
    max_file_size_mb: float = 100.0


class SystemMonitor:
    """Monitors system resources and health"""
    
    def __init__(self, thresholds: ResourceThresholds = None):
        self.thresholds = thresholds or ResourceThresholds()
        self.logger = logging.getLogger("Aurora_Monitor")
        self.monitoring = False
        self.monitor_thread = None
        self.alert_callbacks = []
        self.stats_history = []
        
    def start_monitoring(self, interval: float = 5.0):
        """Starts continuous system monitoring"""
        if self.monitoring:
            self.logger.warning("Monitoring already started")
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"System monitoring started with {interval}s interval")
        
    def stop_monitoring(self):
        """Stops system monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        self.logger.info("System monitoring stopped")
        
    def _monitor_loop(self, interval: float):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                stats = self.get_system_stats()
                self._check_thresholds(stats)
                self._update_history(stats)
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
                
    def get_system_stats(self) -> Dict[str, Any]:
        """Gets current system statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            stats = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'process_count': len(psutil.pids())
            }
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {}
            
    def _check_thresholds(self, stats: Dict[str, Any]):
        """Checks if any thresholds are exceeded"""
        alerts = []
        
        if stats.get('cpu_percent', 0) > self.thresholds.cpu_percent:
            alerts.append(f"High CPU usage: {stats['cpu_percent']:.1f}%")
            
        if stats.get('memory_percent', 0) > self.thresholds.memory_percent:
            alerts.append(f"High memory usage: {stats['memory_percent']:.1f}%")
            
        if stats.get('disk_percent', 0) > self.thresholds.disk_percent:
            alerts.append(f"High disk usage: {stats['disk_percent']:.1f}%")
            
        if alerts:
            for alert in alerts:
                self.logger.warning(alert)
                self._trigger_alerts(alert, stats)
                
    def _update_history(self, stats: Dict[str, Any]):
        """Updates statistics history"""
        self.stats_history.append(stats)
        
        # Keep only last 100 entries
        if len(self.stats_history) > 100:
            self.stats_history = self.stats_history[-100:]
            
    def _trigger_alerts(self, alert_message: str, stats: Dict[str, Any]):
        """Triggers alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alert_message, stats)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
                
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Adds an alert callback function"""
        self.alert_callbacks.append(callback)
        self.logger.info("Alert callback added")
        
    def get_stats_summary(self) -> Dict[str, Any]:
        """Gets a summary of recent statistics"""
        if not self.stats_history:
            return {}
            
        recent_stats = self.stats_history[-10:]  # Last 10 readings
        
        cpu_values = [s.get('cpu_percent', 0) for s in recent_stats]
        memory_values = [s.get('memory_percent', 0) for s in recent_stats]
        
        return {
            'cpu_avg': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            'cpu_max': max(cpu_values) if cpu_values else 0,
            'memory_avg': sum(memory_values) / len(memory_values) if memory_values else 0,
            'memory_max': max(memory_values) if memory_values else 0,
            'readings_count': len(recent_stats),
            'latest_stats': recent_stats[-1] if recent_stats else {}
        }
        
    def check_file_size(self, file_path: str) -> bool:
        """Checks if file size is within limits"""
        try:
            import os
            if not os.path.exists(file_path):
                return True
                
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if size_mb > self.thresholds.max_file_size_mb:
                self.logger.warning(f"File {file_path} exceeds size limit: {size_mb:.1f}MB")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error checking file size: {e}")
            return False
            
    def get_health_status(self) -> Dict[str, Any]:
        """Gets overall system health status"""
        stats = self.get_system_stats()
        
        health_score = 100
        issues = []
        
        if stats.get('cpu_percent', 0) > self.thresholds.cpu_percent:
            health_score -= 20
            issues.append("High CPU usage")
            
        if stats.get('memory_percent', 0) > self.thresholds.memory_percent:
            health_score -= 25
            issues.append("High memory usage")
            
        if stats.get('disk_percent', 0) > self.thresholds.disk_percent:
            health_score -= 30
            issues.append("High disk usage")
            
        status = "healthy" if health_score > 80 else "warning" if health_score > 50 else "critical"
        
        return {
            'status': status,
            'health_score': max(0, health_score),
            'issues': issues,
            'stats': stats,
            'monitoring_active': self.monitoring
        }