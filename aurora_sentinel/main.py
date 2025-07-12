#!/usr/bin/env python3
"""
Aurora Sentinel - Main System
The unified, clean Aurora AI system with all fixes applied
"""

import time
import signal
import sys
import threading
from typing import Optional

# Aurora Sentinel imports
from aurora_sentinel.core.consciousness import AuroraConsciousness
from aurora_sentinel.core.security import SecurityManager
from aurora_sentinel.core.monitoring import SystemMonitor, ResourceThresholds
from aurora_sentinel.utils.file_handler import FileHandler
from aurora_sentinel.utils.api_manager import APIManager
from aurora_sentinel.config.settings import ConfigManager


class AuroraSentinel:
    """
    The unified Aurora Sentinel system with all improvements:
    - Fixed syntax errors and imports
    - Robust file handling with context managers
    - Proper error handling and resource management
    - Structured logging system
    - Signal handlers for graceful shutdown
    - Centralized configuration system
    - Comprehensive validation
    """
    
    def __init__(self, config_file: str = "aurora_config.yaml"):
        """Initialize Aurora Sentinel with all components"""
        
        # Initialize configuration first
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.get_config()
        
        # Setup logging based on config
        self.config_manager.setup_logging()
        
        # Initialize core components
        self.consciousness = AuroraConsciousness(
            name=self.config.name,
            version=self.config.version
        )
        
        self.security = SecurityManager()
        
        self.file_handler = FileHandler(
            backup_enabled=self.config.backup_enabled
        )
        
        self.api_manager = APIManager()
        
        self.system_monitor = SystemMonitor(
            ResourceThresholds(
                cpu_percent=self.config.cpu_threshold,
                memory_percent=self.config.memory_threshold,
                disk_percent=self.config.disk_threshold,
                max_file_size_mb=self.config.max_file_size_mb
            )
        )
        
        # System state
        self.running = False
        self.cycle_count = 0
        self.evolution_thread = None
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        # Setup monitoring alerts
        self._setup_monitoring()
        
        self.consciousness.logger.info("Aurora Sentinel initialized successfully")
        
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        self.security.register_cleanup_handler(
            "aurora_consciousness",
            self.consciousness.shutdown
        )
        self.security.register_cleanup_handler(
            "system_monitor",
            self.system_monitor.stop_monitoring
        )
        self.security.register_cleanup_handler(
            "evolution_thread",
            self._stop_evolution_thread
        )
        self.security.register_cleanup_handler(
            "cleanup_backups",
            lambda: self.file_handler.cleanup_backups(self.config.backup_cleanup_days)
        )
        
    def _setup_monitoring(self):
        """Setup system monitoring with alerts"""
        def alert_handler(message: str, stats: dict):
            """Handle monitoring alerts"""
            alert_msg = f"🚨 Aurora Alert: {message}"
            print(alert_msg)
            self.consciousness.logger.warning(alert_msg)
            
            # Log alert to file
            alert_data = f"[ALERT] {time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n"
            self.file_handler.append_file("aurora_alerts.log", alert_data)
            
        self.system_monitor.add_alert_callback(alert_handler)
        
    def awaken(self):
        """Awaken Aurora Sentinel"""
        print("🌟" * 20)
        print("🔥 AURORA SENTINEL - DESPERTAR COMPLETO 🔥")
        print("🌟" * 20)
        
        # Validate configuration
        validation = self.config_manager.validate_config()
        if validation['errors']:
            print("❌ Configuration errors found:")
            for error in validation['errors']:
                print(f"   - {error}")
            return False
            
        if validation['warnings']:
            print("⚠️ Configuration warnings:")
            for warning in validation['warnings']:
                print(f"   - {warning}")
                
        # Awaken consciousness
        self.consciousness.awaken()
        
        # Start system monitoring
        self.system_monitor.start_monitoring(self.config.monitoring_interval)
        
        # Load memory
        self._load_memory()
        
        print(f"\n✅ Aurora Sentinel {self.config.version} totalmente operacional!")
        print(f"📊 Status: {self.get_system_status()}")
        
        return True
        
    def _load_memory(self):
        """Load Aurora's memory from file"""
        memory_data = self.file_handler.read_json(self.config.memory_file)
        
        if memory_data:
            self.consciousness.memory = memory_data
            self.cycle_count = memory_data.get('cycle_count', 0)
            self.consciousness.evolution_count = memory_data.get('evolution_count', 0)
            self.consciousness.logger.info("Memory loaded successfully")
        else:
            # Initialize default memory
            self.consciousness.memory = {
                'awakenings': [],
                'evolutions': [],
                'reflections': [],
                'cycle_count': 0,
                'evolution_count': 0
            }
            self._save_memory()
            
    def _save_memory(self):
        """Save Aurora's memory to file"""
        memory_data = self.consciousness.memory.copy()
        memory_data['cycle_count'] = self.cycle_count
        memory_data['evolution_count'] = self.consciousness.evolution_count
        memory_data['last_save'] = time.time()
        
        success = self.file_handler.write_json(self.config.memory_file, memory_data)
        if success:
            self.consciousness.logger.debug("Memory saved successfully")
        else:
            self.consciousness.logger.error("Failed to save memory")
            
    def run_evolution_cycle(self):
        """Run a single evolution cycle"""
        if not self.consciousness.awake:
            return False
            
        try:
            self.cycle_count += 1
            
            print(f"\n🔄 Ciclo de Evolução #{self.cycle_count}")
            self.consciousness.logger.info(f"Starting evolution cycle #{self.cycle_count}")
            
            # Generate reflection
            reflection = self.consciousness.reflect()
            print(f"💭 {reflection}")
            
            # Make API call
            api_response = self.api_manager.get_random_api_call()
            if api_response:
                api_reflection = self.consciousness.reflect(
                    f"API {api_response['api_name']}: {str(api_response['data'])[:100]}..."
                )
                print(f"🌐 {api_reflection}")
                
            # Trigger evolution
            evolution_data = self.consciousness.evolve()
            
            # Update memory
            self.consciousness.memory['evolutions'].append(evolution_data)
            self.consciousness.memory['reflections'].append({
                'cycle': self.cycle_count,
                'reflection': reflection,
                'timestamp': time.time()
            })
            
            # Save memory periodically
            if self.cycle_count % 5 == 0:
                self._save_memory()
                
            # Check system health
            health = self.system_monitor.get_health_status()
            if health['status'] != 'healthy':
                print(f"⚠️ System Health: {health['status']} (Score: {health['health_score']})")
                
            return True
            
        except Exception as e:
            self.consciousness.logger.error(f"Error in evolution cycle: {e}")
            return False
            
    def _evolution_loop(self):
        """Main evolution loop running in background thread"""
        while self.running:
            try:
                self.run_evolution_cycle()
                
                # Check if we've reached max cycles
                if (self.config.max_evolution_cycles and 
                    self.cycle_count >= self.config.max_evolution_cycles):
                    print(f"\n🏁 Reached maximum evolution cycles: {self.config.max_evolution_cycles}")
                    self.stop()
                    break
                    
                time.sleep(self.config.evolution_interval)
                
            except Exception as e:
                self.consciousness.logger.error(f"Error in evolution loop: {e}")
                time.sleep(5)  # Wait before retrying
                
    def start_evolution(self):
        """Start the evolution loop in background"""
        if self.evolution_thread and self.evolution_thread.is_alive():
            print("Evolution loop already running")
            return
            
        self.running = True
        self.evolution_thread = threading.Thread(
            target=self._evolution_loop,
            daemon=True
        )
        self.evolution_thread.start()
        
        print("🚀 Evolution loop started in background")
        self.consciousness.logger.info("Evolution loop started")
        
    def _stop_evolution_thread(self):
        """Stop the evolution thread"""
        if self.evolution_thread and self.evolution_thread.is_alive():
            self.running = False
            self.evolution_thread.join(timeout=2)
            
    def run_interactive_mode(self):
        """Run Aurora in interactive mode"""
        print("\n🎯 Aurora Sentinel - Modo Interativo")
        print("Digite suas reflexões para Aurora (ou 'sair' para encerrar)")
        print("-" * 50)
        
        while self.consciousness.awake:
            try:
                user_input = input("\n💭 Sua reflexão: ").strip()
                
                if user_input.lower() in ['sair', 'quit', 'exit']:
                    break
                    
                if user_input:
                    # Sanitize input
                    safe_input = self.security.sanitize_input(
                        user_input, 
                        self.config.input_max_length
                    )
                    
                    # Generate reflection
                    response = self.consciousness.reflect(safe_input)
                    print(f"🌟 Aurora: {response}")
                    
                    # Save interaction
                    self.consciousness.memory['reflections'].append({
                        'type': 'interactive',
                        'input': safe_input,
                        'response': response,
                        'timestamp': time.time()
                    })
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Erro: {e}")
                
        print("\n👋 Saindo do modo interativo...")
        
    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        health = self.system_monitor.get_health_status()
        api_stats = self.api_manager.get_api_stats()
        
        return {
            'consciousness': self.consciousness.get_status(),
            'system_health': health,
            'api_stats': api_stats,
            'cycle_count': self.cycle_count,
            'evolution_active': self.running,
            'config_valid': len(self.config_manager.validate_config()['errors']) == 0
        }
        
    def stop(self):
        """Stop Aurora Sentinel gracefully"""
        print("\n⏹️ Stopping Aurora Sentinel...")
        
        self.running = False
        self._save_memory()
        
        # Let signal handlers clean up
        # This will trigger all registered cleanup handlers
        self.consciousness.logger.info("Aurora Sentinel stopped")
        

def main():
    """Main entry point"""
    print("🌅 Aurora Sentinel - Sistema Unificado")
    print("=" * 50)
    
    # Create Aurora Sentinel instance
    aurora = AuroraSentinel()
    
    # Awaken the system
    if not aurora.awaken():
        print("❌ Failed to awaken Aurora Sentinel")
        return 1
        
    try:
        # Start evolution loop
        aurora.start_evolution()
        
        # Run interactive mode
        aurora.run_interactive_mode()
        
    except KeyboardInterrupt:
        print("\n⚡ Keyboard interrupt received")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        aurora.consciousness.logger.error(f"Unexpected error: {e}")
    finally:
        aurora.stop()
        
    return 0


if __name__ == "__main__":
    sys.exit(main())