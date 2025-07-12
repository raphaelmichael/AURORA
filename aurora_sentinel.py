#!/usr/bin/env python3
"""
Aurora Sentinel - Sistema Unificado de Monitoramento AI
Endereça os problemas críticos identificados na Issue #5:
- Correção da sintaxe UFW
- Configuração automática do RClone
- Logs estruturados
- Sistema de configuração centralizada
"""

import os
import sys
import json
import yaml
import time
import logging
import logging.handlers
import subprocess
import datetime
import schedule
from pathlib import Path
from typing import Dict, List, Any, Optional

class AuroraSentinel:
    """Sistema Aurora Sentinel - Monitoramento e Segurança AI"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Aurora Sentinel iniciado")
        
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Arquivo de configuração {self.config_path} não encontrado.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Erro ao carregar configuração: {e}")
            sys.exit(1)
            
    def setup_logging(self):
        """Configura sistema de logging estruturado"""
        log_config = self.config.get('logging', {})
        log_format = log_config.get('format', 'json')
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'aurora_sentinel.log')
        
        # Formato estruturado JSON
        if log_format == 'json':
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"module": "%(name)s", "message": "%(message)s", '
                '"function": "%(funcName)s", "line": %(lineno)d}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s'
            )
        
        # Configurar handlers
        handlers = []
        
        # File handler com rotação
        if log_config.get('rotation', True):
            max_bytes = log_config.get('max_size_mb', 10) * 1024 * 1024
            backup_count = log_config.get('backup_count', 5)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count
            )
        else:
            file_handler = logging.FileHandler(log_file)
            
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
        
        # Configurar logging
        logging.basicConfig(
            level=log_level,
            handlers=handlers,
            force=True
        )
        
    def setup_firewall(self) -> bool:
        """
        Configura firewall UFW com sintaxe corrigida
        Corrige o erro: sudo ufw deny 80 443 -> comandos individuais
        """
        if not self.config.get('firewall', {}).get('enabled', True):
            self.logger.info("Firewall configuração desabilitada")
            return True
            
        try:
            firewall_config = self.config['firewall']
            
            # Verificar se UFW está instalado
            result = subprocess.run(['which', 'ufw'], capture_output=True)
            if result.returncode != 0:
                self.logger.error("UFW não está instalado. Execute: sudo apt install ufw")
                return False
            
            # Ativar UFW
            self.logger.info("Ativando UFW firewall")
            subprocess.run(['sudo', 'ufw', '--force', 'enable'], check=True)
            
            # Configurar política padrão
            default_policy = firewall_config.get('default_policy', 'deny')
            subprocess.run(['sudo', 'ufw', 'default', default_policy], check=True)
            
            # CORREÇÃO: Configurar portas bloqueadas individualmente
            blocked_ports = firewall_config.get('blocked_ports', [])
            for port in blocked_ports:
                self.logger.info(f"Bloqueando porta {port}")
                subprocess.run(['sudo', 'ufw', 'deny', str(port)], check=True)
                
            # Configurar portas permitidas
            allowed_ports = firewall_config.get('allowed_ports', [])
            for port in allowed_ports:
                self.logger.info(f"Permitindo porta {port}")
                subprocess.run(['sudo', 'ufw', 'allow', str(port)], check=True)
            
            # Ativar logging se configurado
            if firewall_config.get('log_attempts', True):
                subprocess.run(['sudo', 'ufw', 'logging', 'on'], check=True)
                
            self.logger.info("Firewall configurado com sucesso")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao configurar firewall: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado na configuração do firewall: {e}")
            return False
            
    def setup_rclone(self) -> bool:
        """
        Configura RClone para backup automático
        Corrige o erro: didn't find section in config file
        """
        if not self.config.get('backup', {}).get('enabled', True):
            self.logger.info("Backup configuração desabilitada")
            return True
            
        try:
            backup_config = self.config['backup']
            remote_name = backup_config.get('remote_name', 'gdrive')
            
            # Verificar se RClone está instalado
            result = subprocess.run(['which', 'rclone'], capture_output=True)
            if result.returncode != 0:
                self.logger.error("RClone não está instalado. Execute: sudo apt install rclone")
                return False
            
            # Verificar se remote já existe
            result = subprocess.run(['rclone', 'listremotes'], capture_output=True, text=True)
            if f"{remote_name}:" not in result.stdout:
                self.logger.warning(f"Remote '{remote_name}' não configurado.")
                self.logger.info("Execute 'rclone config' para configurar Google Drive:")
                self.logger.info("1. Escolha 'n' para new remote")
                self.logger.info(f"2. Nome: {remote_name}")
                self.logger.info("3. Storage: drive (Google Drive)")
                self.logger.info("4. Siga as instruções para autenticação")
                return False
                
            # Testar conexão
            remote_path = backup_config.get('remote_path', 'sentinel_backup')
            test_result = subprocess.run(
                ['rclone', 'lsd', f"{remote_name}:{remote_path}"],
                capture_output=True, text=True
            )
            
            if test_result.returncode != 0:
                # Criar diretório de backup se não existir
                self.logger.info(f"Criando diretório de backup: {remote_path}")
                subprocess.run(['rclone', 'mkdir', f"{remote_name}:{remote_path}"], check=True)
                
            self.logger.info("RClone configurado e testado com sucesso")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao configurar RClone: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado na configuração do RClone: {e}")
            return False
            
    def perform_backup(self) -> bool:
        """Executa backup incremental inteligente"""
        if not self.config.get('backup', {}).get('enabled', True):
            return True
            
        try:
            backup_config = self.config['backup']
            remote_name = backup_config.get('remote_name', 'gdrive')
            remote_path = backup_config.get('remote_path', 'sentinel_backup')
            
            # Preparar arquivos para backup
            backup_files = [
                'aurora_sentinel.log',
                'config.yaml',
                '*.py',
                'aurora_*.json'
            ]
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = f"{remote_path}/backup_{timestamp}"
            
            # Criar backup incremental
            for pattern in backup_files:
                if Path(pattern).exists() or any(Path('.').glob(pattern)):
                    self.logger.info(f"Fazendo backup de: {pattern}")
                    subprocess.run([
                        'rclone', 'copy', pattern, f"{remote_name}:{backup_dir}"
                    ], check=True)
            
            # Verificar integridade se habilitado
            if backup_config.get('verify_integrity', True):
                result = subprocess.run([
                    'rclone', 'check', '.', f"{remote_name}:{backup_dir}"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info("Backup verificado com sucesso")
                else:
                    self.logger.warning("Falha na verificação de integridade do backup")
            
            self.logger.info(f"Backup concluído: {backup_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro durante backup: {e}")
            return False
            
    def check_system_health(self) -> Dict[str, Any]:
        """Verifica saúde do sistema"""
        health_status = {
            'timestamp': datetime.datetime.now().isoformat(),
            'firewall': False,
            'backup': False,
            'disk_space': 0,
            'memory_usage': 0,
            'cpu_usage': 0
        }
        
        try:
            # Verificar firewall
            result = subprocess.run(['sudo', 'ufw', 'status'], capture_output=True, text=True)
            health_status['firewall'] = 'Status: active' in result.stdout
            
            # Verificar backup
            backup_config = self.config.get('backup', {})
            if backup_config.get('enabled'):
                remote_name = backup_config.get('remote_name', 'gdrive')
                result = subprocess.run(['rclone', 'lsd', f"{remote_name}:"], capture_output=True)
                health_status['backup'] = result.returncode == 0
            else:
                health_status['backup'] = True  # Disabled, so considered OK
                
            # Verificar espaço em disco
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) > 4:
                        health_status['disk_space'] = parts[4].rstrip('%')
            
            self.logger.info(f"Status do sistema: {health_status}")
            return health_status
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar saúde do sistema: {e}")
            return health_status
            
    def install_dependencies(self) -> bool:
        """Instala dependências faltantes conforme Issue #5"""
        try:
            dependencies = ['ufw', 'rclone', 'chkrootkit', 'rkhunter']
            
            self.logger.info("Atualizando lista de pacotes")
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            
            for dep in dependencies:
                self.logger.info(f"Instalando: {dep}")
                subprocess.run(['sudo', 'apt', 'install', '-y', dep], check=True)
                
            self.logger.info("Dependências instaladas com sucesso")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao instalar dependências: {e}")
            return False
            
    def setup_monitoring_schedule(self):
        """Configura agendamento de monitoramento"""
        monitoring_config = self.config.get('monitoring', {})
        if not monitoring_config.get('enabled', True):
            return
            
        # Agendar verificações regulares
        interval = monitoring_config.get('check_interval', 300) // 60  # Convert to minutes
        schedule.every(interval).minutes.do(self.check_system_health)
        
        # Agendar backup
        backup_config = self.config.get('backup', {})
        if backup_config.get('enabled', True):
            backup_schedule = backup_config.get('schedule', '0 2 * * *')
            # Simplificado - backup diário às 2h
            schedule.every().day.at("02:00").do(self.perform_backup)
            
    def run(self):
        """Executa o Aurora Sentinel"""
        self.logger.info("=== Aurora Sentinel - Iniciando ===")
        
        # Configurações iniciais
        if not self.setup_firewall():
            self.logger.error("Falha na configuração do firewall")
            
        if not self.setup_rclone():
            self.logger.error("Falha na configuração do RClone")
            
        # Configurar monitoramento
        self.setup_monitoring_schedule()
        
        # Verificação inicial
        self.check_system_health()
        
        self.logger.info("Aurora Sentinel operacional")
        
        # Loop principal
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Aurora Sentinel finalizado pelo usuário")
        except Exception as e:
            self.logger.error(f"Erro inesperado: {e}")
            
def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aurora Sentinel - Sistema de Monitoramento AI')
    parser.add_argument('--config', default='config.yaml', help='Arquivo de configuração')
    parser.add_argument('--install-deps', action='store_true', help='Instalar dependências')
    parser.add_argument('--setup-only', action='store_true', help='Apenas configurar, não executar')
    parser.add_argument('--check-health', action='store_true', help='Verificar saúde do sistema')
    
    args = parser.parse_args()
    
    sentinel = AuroraSentinel(args.config)
    
    if args.install_deps:
        sentinel.install_dependencies()
        return
        
    if args.check_health:
        health = sentinel.check_system_health()
        print(json.dumps(health, indent=2))
        return
        
    if args.setup_only:
        sentinel.setup_firewall()
        sentinel.setup_rclone()
        return
        
    # Executar modo completo
    sentinel.run()

if __name__ == "__main__":
    main()