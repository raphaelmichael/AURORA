#!/usr/bin/env python3
"""
Testes básicos para o Aurora Sentinel
"""

import os
import sys
import tempfile
import pytest
import yaml
from unittest.mock import patch, MagicMock

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aurora_sentinel import AuroraSentinel

class TestAuroraSentinel:
    """Testes para o sistema Aurora Sentinel"""
    
    def create_test_config(self):
        """Cria configuração de teste"""
        return {
            'system': {
                'name': 'Aurora Sentinel Test',
                'version': '2.0',
                'debug': True
            },
            'logging': {
                'level': 'INFO',
                'format': 'json',
                'file': 'test_aurora.log',
                'rotation': False
            },
            'firewall': {
                'enabled': True,
                'blocked_ports': [80, 443],
                'allowed_ports': [22]
            },
            'backup': {
                'enabled': True,
                'remote_name': 'test_drive',
                'remote_path': 'test_backup'
            },
            'monitoring': {
                'enabled': True,
                'check_interval': 60
            }
        }
    
    def test_config_loading(self):
        """Testa carregamento da configuração"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.create_test_config(), f)
            config_path = f.name
        
        try:
            sentinel = AuroraSentinel(config_path)
            assert sentinel.config['system']['name'] == 'Aurora Sentinel Test'
            assert sentinel.config['firewall']['enabled'] is True
        finally:
            os.unlink(config_path)
    
    @patch('subprocess.run')
    def test_firewall_setup_success(self, mock_run):
        """Testa configuração bem-sucedida do firewall"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.create_test_config(), f)
            config_path = f.name
        
        try:
            # Mock subprocess calls
            mock_run.return_value = MagicMock(returncode=0)
            
            sentinel = AuroraSentinel(config_path)
            result = sentinel.setup_firewall()
            
            assert result is True
            # Verificar se os comandos corretos foram chamados
            assert mock_run.call_count > 0
        finally:
            os.unlink(config_path)
    
    @patch('subprocess.run')
    def test_rclone_setup_not_installed(self, mock_run):
        """Testa falha quando RClone não está instalado"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.create_test_config(), f)
            config_path = f.name
        
        try:
            # Mock que RClone não está instalado
            mock_run.return_value = MagicMock(returncode=1)
            
            sentinel = AuroraSentinel(config_path)
            result = sentinel.setup_rclone()
            
            assert result is False
        finally:
            os.unlink(config_path)
    
    @patch('subprocess.run')
    def test_system_health_check(self, mock_run):
        """Testa verificação de saúde do sistema"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.create_test_config(), f)
            config_path = f.name
        
        try:
            # Mock das chamadas do sistema
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout='Status: active\n'),  # ufw status
                MagicMock(returncode=0),  # rclone lsd
                MagicMock(returncode=0, stdout='Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1       100G   20G   80G  20% /\n')  # df -h
            ]
            
            sentinel = AuroraSentinel(config_path)
            health = sentinel.check_system_health()
            
            assert 'firewall' in health
            assert 'backup' in health
            assert 'timestamp' in health
        finally:
            os.unlink(config_path)
    
    def test_disabled_components(self):
        """Testa componentes desabilitados"""
        config = self.create_test_config()
        config['firewall']['enabled'] = False
        config['backup']['enabled'] = False
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            config_path = f.name
        
        try:
            sentinel = AuroraSentinel(config_path)
            
            # Componentes desabilitados devem retornar True (sem erro)
            assert sentinel.setup_firewall() is True
            assert sentinel.setup_rclone() is True
        finally:
            os.unlink(config_path)

def test_aurora_sentinel_imports():
    """Testa se todas as importações necessárias estão disponíveis"""
    try:
        import yaml
        import schedule
        assert True
    except ImportError as e:
        pytest.fail(f"Dependência faltando: {e}")

def test_main_function_args():
    """Testa argumentos da função principal"""
    from aurora_sentinel import main
    
    # Teste básico que a função main existe e pode ser importada
    assert callable(main)

if __name__ == "__main__":
    # Executar testes básicos
    print("Executando testes do Aurora Sentinel...")
    
    # Teste de importação
    test_aurora_sentinel_imports()
    print("✓ Importações OK")
    
    # Criar teste básico
    test_sentinel = TestAuroraSentinel()
    
    # Teste de configuração
    test_sentinel.test_config_loading()
    print("✓ Carregamento de configuração OK")
    
    test_sentinel.test_disabled_components()
    print("✓ Componentes desabilitados OK")
    
    print("Testes básicos concluídos com sucesso!")