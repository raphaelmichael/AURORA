#!/usr/bin/env python3
"""
Aurora Launcher - Launcher unificado para todo o sistema Aurora Sentinel
Integra todos os componentes: Sentinel, Dashboard e AI Monitor
"""

import os
import sys
import time
import threading
import signal
import argparse
import logging
from aurora_sentinel import AuroraSentinel
from aurora_dashboard import AuroraDashboard
from aurora_ai_monitor import AuroraAIMonitor

class AuroraLauncher:
    """Launcher principal do sistema Aurora"""
    
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.components = {}
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        self.logger.info("Sinal de shutdown recebido, finalizando...")
        self.running = False
        self.stop_all_components()
        sys.exit(0)
        
    def start_sentinel(self):
        """Start Aurora Sentinel in background"""
        try:
            sentinel = AuroraSentinel(self.config_path)
            
            # Run setup only
            self.logger.info("Configurando Aurora Sentinel...")
            sentinel.setup_firewall()
            sentinel.setup_rclone()
            
            # Run monitoring in background
            def monitoring_loop():
                sentinel.setup_monitoring_schedule()
                while self.running:
                    try:
                        # Check health and save to file for dashboard
                        health = sentinel.check_system_health()
                        with open('aurora_health.json', 'w') as f:
                            import json
                            json.dump(health, f)
                        time.sleep(300)  # Check every 5 minutes
                    except Exception as e:
                        self.logger.error(f"Erro no loop de monitoramento: {e}")
                        time.sleep(60)
            
            monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
            monitor_thread.start()
            self.components['sentinel'] = monitor_thread
            
            self.logger.info("✅ Aurora Sentinel iniciado")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar Sentinel: {e}")
            return False
    
    def start_ai_monitor(self):
        """Start AI Monitor in background"""
        try:
            # Load config for AI monitor
            import yaml
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            ai_monitor = AuroraAIMonitor(config)
            
            def ai_monitoring_loop():
                while self.running:
                    try:
                        result = ai_monitor.run_monitoring_cycle()
                        if result.get('anomalies_detected', 0) > 0:
                            self.logger.warning(f"🚨 {result['anomalies_detected']} anomalias detectadas")
                        time.sleep(ai_monitor.check_interval)
                    except Exception as e:
                        self.logger.error(f"Erro no AI Monitor: {e}")
                        time.sleep(60)
            
            ai_thread = threading.Thread(target=ai_monitoring_loop, daemon=True)
            ai_thread.start()
            self.components['ai_monitor'] = ai_thread
            
            self.logger.info("✅ Aurora AI Monitor iniciado")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar AI Monitor: {e}")
            return False
    
    def start_dashboard(self, host='localhost', port=8080):
        """Start Dashboard in background"""
        try:
            dashboard = AuroraDashboard(host, port)
            
            def dashboard_loop():
                try:
                    dashboard.start()
                except Exception as e:
                    if self.running:  # Only log if not shutting down
                        self.logger.error(f"Erro no Dashboard: {e}")
            
            dashboard_thread = threading.Thread(target=dashboard_loop, daemon=True)
            dashboard_thread.start()
            self.components['dashboard'] = dashboard
            
            self.logger.info(f"✅ Aurora Dashboard iniciado em http://{host}:{port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar Dashboard: {e}")
            return False
    
    def stop_all_components(self):
        """Stop all running components"""
        for name, component in self.components.items():
            try:
                if name == 'dashboard' and hasattr(component, 'stop'):
                    component.stop()
                self.logger.info(f"Componente {name} finalizado")
            except Exception as e:
                self.logger.error(f"Erro ao finalizar {name}: {e}")
    
    def show_status(self):
        """Show system status"""
        print("\n🌟 Aurora Sentinel - Status do Sistema")
        print("=" * 50)
        
        # Check component status
        for name in ['sentinel', 'ai_monitor', 'dashboard']:
            if name in self.components:
                print(f"✅ {name.title().replace('_', ' ')}: Ativo")
            else:
                print(f"❌ {name.title().replace('_', ' ')}: Inativo")
        
        print("\n📊 Acesso:")
        if 'dashboard' in self.components:
            print("🌐 Dashboard: http://localhost:8080")
        print("📋 Logs: aurora_sentinel.log")
        print("🚨 Anomalias: aurora_anomalies.json")
        print("💊 Saúde: aurora_health.json")
        print()
    
    def run_full_system(self, dashboard_host='localhost', dashboard_port=8080):
        """Run complete Aurora system"""
        self.logger.info("🌟 Iniciando Sistema Aurora Sentinel Completo")
        
        # Start all components
        sentinel_ok = self.start_sentinel()
        ai_monitor_ok = self.start_ai_monitor()
        dashboard_ok = self.start_dashboard(dashboard_host, dashboard_port)
        
        if not any([sentinel_ok, ai_monitor_ok, dashboard_ok]):
            self.logger.error("❌ Falha ao iniciar qualquer componente")
            return False
        
        self.show_status()
        
        try:
            # Main loop
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.logger.info("Finalizando sistema...")
            self.stop_all_components()
        
        return True

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Aurora Sentinel - Sistema Completo')
    parser.add_argument('--config', default='config.yaml', help='Arquivo de configuração')
    parser.add_argument('--mode', choices=['full', 'sentinel', 'dashboard', 'ai-monitor'], 
                       default='full', help='Modo de execução')
    parser.add_argument('--host', default='localhost', help='Host do dashboard')
    parser.add_argument('--port', type=int, default=8080, help='Porta do dashboard')
    parser.add_argument('--status', action='store_true', help='Mostrar status e sair')
    
    args = parser.parse_args()
    
    launcher = AuroraLauncher(args.config)
    
    if args.status:
        launcher.show_status()
        return
    
    if args.mode == 'full':
        # Run complete system
        launcher.run_full_system(args.host, args.port)
        
    elif args.mode == 'sentinel':
        # Run only sentinel
        launcher.start_sentinel()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
    elif args.mode == 'dashboard':
        # Run only dashboard
        launcher.start_dashboard(args.host, args.port)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
    elif args.mode == 'ai-monitor':
        # Run only AI monitor
        launcher.start_ai_monitor()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()