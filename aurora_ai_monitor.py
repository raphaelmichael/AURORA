#!/usr/bin/env python3
"""
Aurora AI Monitor - Sistema de Detecção de Anomalias
Implementa monitoramento inteligente básico sem dependências complexas
"""

import os
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque, defaultdict
import statistics
import subprocess

class AuroraAIMonitor:
    """Sistema de monitoramento AI simples para detecção de anomalias"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('monitoring', {})
        self.enabled = self.config.get('enabled', True)
        self.threshold = self.config.get('alert_threshold', 0.8)
        self.check_interval = self.config.get('check_interval', 300)
        
        # Histórico de métricas (últimas 100 leituras)
        self.cpu_history = deque(maxlen=100)
        self.memory_history = deque(maxlen=100)
        self.disk_history = deque(maxlen=100)
        self.network_history = deque(maxlen=100)
        
        # Contadores de anomalias
        self.anomaly_count = defaultdict(int)
        self.last_alert = {}
        
        self.logger = logging.getLogger(__name__)
        
    def collect_system_metrics(self) -> Dict[str, float]:
        """Coleta métricas básicas do sistema"""
        try:
            metrics = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'timestamp': time.time()
            }
            
            # Tentar coletar métricas de rede
            try:
                net_io = psutil.net_io_counters()
                if hasattr(self, '_last_net_io'):
                    time_diff = metrics['timestamp'] - self._last_net_timestamp
                    bytes_sent_rate = (net_io.bytes_sent - self._last_net_io.bytes_sent) / time_diff
                    bytes_recv_rate = (net_io.bytes_recv - self._last_net_io.bytes_recv) / time_diff
                    metrics['network_rate'] = (bytes_sent_rate + bytes_recv_rate) / (1024 * 1024)  # MB/s
                else:
                    metrics['network_rate'] = 0
                    
                self._last_net_io = net_io
                self._last_net_timestamp = metrics['timestamp']
            except:
                metrics['network_rate'] = 0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas: {e}")
            return {}
    
    def update_history(self, metrics: Dict[str, float]):
        """Atualiza histórico de métricas"""
        if not metrics:
            return
            
        self.cpu_history.append(metrics.get('cpu_percent', 0))
        self.memory_history.append(metrics.get('memory_percent', 0))
        self.disk_history.append(metrics.get('disk_percent', 0))
        self.network_history.append(metrics.get('network_rate', 0))
    
    def detect_anomalies(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Detecta anomalias usando métodos estatísticos simples"""
        anomalies = []
        
        if not metrics or len(self.cpu_history) < 10:
            return anomalies
        
        # Detecção baseada em desvio padrão
        current_time = datetime.now()
        
        # CPU
        if len(self.cpu_history) > 1:
            cpu_mean = statistics.mean(list(self.cpu_history)[:-1])
            cpu_stdev = statistics.stdev(list(self.cpu_history)[:-1]) if len(self.cpu_history) > 2 else 1
            current_cpu = metrics.get('cpu_percent', 0)
            
            if cpu_stdev > 0 and abs(current_cpu - cpu_mean) > (2 * cpu_stdev) and current_cpu > 80:
                anomalies.append({
                    'type': 'cpu_spike',
                    'severity': 'high' if current_cpu > 90 else 'medium',
                    'value': current_cpu,
                    'mean': cpu_mean,
                    'message': f'Pico de CPU detectado: {current_cpu:.1f}% (média: {cpu_mean:.1f}%)',
                    'timestamp': current_time.isoformat()
                })
        
        # Memória
        if len(self.memory_history) > 1:
            mem_mean = statistics.mean(list(self.memory_history)[:-1])
            current_mem = metrics.get('memory_percent', 0)
            
            if current_mem > 85:  # Limite fixo para memória
                anomalies.append({
                    'type': 'memory_high',
                    'severity': 'high' if current_mem > 95 else 'medium',
                    'value': current_mem,
                    'mean': mem_mean,
                    'message': f'Uso alto de memória: {current_mem:.1f}%',
                    'timestamp': current_time.isoformat()
                })
        
        # Disco
        current_disk = metrics.get('disk_percent', 0)
        if current_disk > 90:
            anomalies.append({
                'type': 'disk_full',
                'severity': 'critical' if current_disk > 95 else 'high',
                'value': current_disk,
                'message': f'Espaço em disco baixo: {current_disk:.1f}% usado',
                'timestamp': current_time.isoformat()
            })
        
        # Rede (picos de tráfego)
        if len(self.network_history) > 5:
            net_mean = statistics.mean(list(self.network_history)[:-1])
            current_net = metrics.get('network_rate', 0)
            
            if net_mean > 0 and current_net > (net_mean * 5) and current_net > 10:  # 10 MB/s
                anomalies.append({
                    'type': 'network_spike',
                    'severity': 'medium',
                    'value': current_net,
                    'mean': net_mean,
                    'message': f'Pico de tráfego de rede: {current_net:.1f} MB/s',
                    'timestamp': current_time.isoformat()
                })
        
        return anomalies
    
    def check_processes(self) -> List[Dict[str, Any]]:
        """Verifica processos suspeitos"""
        anomalies = []
        
        try:
            # Processos com alto uso de CPU
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 50:
                        anomalies.append({
                            'type': 'process_cpu_high',
                            'severity': 'medium',
                            'process': proc_info['name'],
                            'pid': proc_info['pid'],
                            'cpu_percent': proc_info['cpu_percent'],
                            'message': f"Processo {proc_info['name']} (PID: {proc_info['pid']}) usando {proc_info['cpu_percent']:.1f}% CPU",
                            'timestamp': datetime.now().isoformat()
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Erro ao verificar processos: {e}")
        
        return anomalies
    
    def check_security_indicators(self) -> List[Dict[str, Any]]:
        """Verifica indicadores básicos de segurança"""
        anomalies = []
        
        try:
            # Verificar tentativas de login SSH (se disponível)
            if os.path.exists('/var/log/auth.log'):
                try:
                    result = subprocess.run([
                        'sudo', 'grep', '-c', 'Failed password', '/var/log/auth.log'
                    ], capture_output=True, text=True, timeout=5)
                    
                    if result.returncode == 0:
                        failed_logins = int(result.stdout.strip())
                        if failed_logins > 10:  # Muitas tentativas falhadas
                            anomalies.append({
                                'type': 'security_failed_logins',
                                'severity': 'high',
                                'count': failed_logins,
                                'message': f'{failed_logins} tentativas de login SSH falhadas detectadas',
                                'timestamp': datetime.now().isoformat()
                            })
                except:
                    pass
            
            # Verificar conexões de rede suspeitas
            try:
                connections = psutil.net_connections(kind='inet')
                external_connections = 0
                
                for conn in connections:
                    if conn.raddr and conn.status == psutil.CONN_ESTABLISHED:
                        # Contar conexões externas (não localhost)
                        if not conn.raddr.ip.startswith('127.') and not conn.raddr.ip.startswith('192.168.'):
                            external_connections += 1
                
                if external_connections > 50:  # Muitas conexões externas
                    anomalies.append({
                        'type': 'security_many_connections',
                        'severity': 'medium',
                        'count': external_connections,
                        'message': f'{external_connections} conexões externas ativas',
                        'timestamp': datetime.now().isoformat()
                    })
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar segurança: {e}")
        
        return anomalies
    
    def save_anomaly_report(self, anomalies: List[Dict[str, Any]]):
        """Salva relatório de anomalias"""
        if not anomalies:
            return
            
        try:
            report_file = 'aurora_anomalies.json'
            
            # Carregar relatórios existentes
            existing_reports = []
            if os.path.exists(report_file):
                try:
                    with open(report_file, 'r') as f:
                        existing_reports = json.load(f)
                except:
                    existing_reports = []
            
            # Adicionar novas anomalias
            existing_reports.extend(anomalies)
            
            # Manter apenas últimas 1000 anomalias
            if len(existing_reports) > 1000:
                existing_reports = existing_reports[-1000:]
            
            # Salvar relatório atualizado
            with open(report_file, 'w') as f:
                json.dump(existing_reports, f, indent=2)
                
            self.logger.info(f"Relatório de anomalias salvo: {len(anomalies)} novas anomalias")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório de anomalias: {e}")
    
    def should_alert(self, anomaly: Dict[str, Any]) -> bool:
        """Verifica se deve enviar alerta (evita spam)"""
        anomaly_key = f"{anomaly['type']}_{anomaly.get('severity', 'medium')}"
        current_time = time.time()
        
        # Enviar alerta apenas se:
        # 1. É a primeira vez que vemos esta anomalia
        # 2. Ou passaram mais de 30 minutos desde o último alerta do mesmo tipo
        if anomaly_key not in self.last_alert:
            self.last_alert[anomaly_key] = current_time
            return True
        elif current_time - self.last_alert[anomaly_key] > 1800:  # 30 minutos
            self.last_alert[anomaly_key] = current_time
            return True
        
        return False
    
    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Executa um ciclo completo de monitoramento"""
        if not self.enabled:
            return {'status': 'disabled'}
        
        try:
            # Coletar métricas
            metrics = self.collect_system_metrics()
            if not metrics:
                return {'status': 'error', 'message': 'Falha ao coletar métricas'}
            
            # Atualizar histórico
            self.update_history(metrics)
            
            # Detectar anomalias
            system_anomalies = self.detect_anomalies(metrics)
            process_anomalies = self.check_processes()
            security_anomalies = self.check_security_indicators()
            
            all_anomalies = system_anomalies + process_anomalies + security_anomalies
            
            # Salvar relatório
            if all_anomalies:
                self.save_anomaly_report(all_anomalies)
                
                # Log das anomalias importantes
                for anomaly in all_anomalies:
                    if self.should_alert(anomaly):
                        self.logger.warning(f"ANOMALIA DETECTADA: {anomaly['message']}")
            
            return {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'anomalies_detected': len(all_anomalies),
                'anomalies': all_anomalies[:5]  # Apenas as primeiras 5 para evitar logs grandes
            }
            
        except Exception as e:
            self.logger.error(f"Erro no ciclo de monitoramento: {e}")
            return {'status': 'error', 'message': str(e)}

def main():
    """Função principal para teste do monitor"""
    import yaml
    
    # Configuração básica de teste
    config = {
        'monitoring': {
            'enabled': True,
            'check_interval': 60,
            'alert_threshold': 0.8
        }
    }
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    monitor = AuroraAIMonitor(config)
    
    print("🤖 Aurora AI Monitor iniciado")
    print("Pressione Ctrl+C para parar")
    
    try:
        while True:
            result = monitor.run_monitoring_cycle()
            print(f"Ciclo de monitoramento: {result['status']}")
            
            if result.get('anomalies_detected', 0) > 0:
                print(f"⚠️  {result['anomalies_detected']} anomalias detectadas")
            
            time.sleep(monitor.check_interval)
            
    except KeyboardInterrupt:
        print("\nMonitor finalizado")

if __name__ == "__main__":
    main()