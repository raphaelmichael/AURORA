# Aurora Sentinel - Sistema Unificado de Monitoramento AI

## 🌟 Visão Geral

O Aurora Sentinel é um sistema de monitoramento e segurança que implementa as melhorias críticas identificadas na Issue #5, corrigindo problemas específicos e adicionando funcionalidades essenciais de segurança e backup.

## 🔧 Problemas Corrigidos (Issue #5)

### 1. ✅ Correção UFW Firewall
- **Problema Original**: `sudo ufw deny 80 443` (sintaxe incorreta)
- **Correção**: Comandos individuais para cada porta
```bash
sudo ufw deny 80
sudo ufw deny 443
```

### 2. ✅ Configuração RClone
- **Problema Original**: `didn't find section in config file`
- **Correção**: Verificação automática e guias de configuração
- **Setup automático**: Criação de diretórios remotos quando necessário

### 3. ✅ Logs Estruturados
- **Implementação**: Formato JSON para logs
- **Rotação automática**: Limitação de tamanho e backup
- **Informações detalhadas**: Timestamp, nível, módulo, função, linha

## 📦 Instalação

### Dependências do Sistema
```bash
sudo apt update
sudo apt install ufw rclone chkrootkit rkhunter
```

### Dependências Python
```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

### 1. Arquivo de Configuração
Edite `config.yaml` para ajustar as configurações do sistema:

```yaml
firewall:
  enabled: true
  blocked_ports: [80, 443]
  allowed_ports: [22]

backup:
  enabled: true
  remote_name: "gdrive"
  remote_path: "sentinel_backup"
```

### 2. Configurar RClone (se backup habilitado)
```bash
rclone config
# Escolha:
# - new remote -> gdrive
# - storage -> drive (Google Drive)
# - Siga as instruções de autenticação
```

## 🚀 Uso

### Sistema Completo (Recomendado)
```bash
python3 aurora_launcher.py
# Acesse o dashboard em: http://localhost:8080
```

### Componentes Individuais

#### Instalação de Dependências
```bash
python3 aurora_sentinel.py --install-deps
```

#### Configuração Apenas (sem executar)
```bash
python3 aurora_sentinel.py --setup-only
```

#### Verificação de Saúde do Sistema
```bash
python3 aurora_sentinel.py --check-health
```

#### Dashboard Web Apenas
```bash
python3 aurora_dashboard.py --port 8080
```

#### Monitor AI Apenas
```bash
python3 aurora_ai_monitor.py
```

#### Execução Sentinel Apenas
```bash
python3 aurora_sentinel.py
```

## 📊 Funcionalidades

### ✅ Fase 1 - Estabilização (Implementada)
- [x] Correção sintaxe UFW
- [x] Configuração RClone automática  
- [x] Logs estruturados JSON
- [x] Sistema de configuração centralizada YAML
- [x] Verificação de saúde do sistema
- [x] Backup incremental inteligente
- [x] Rotação automática de logs

### ✅ Fase 2 - Inteligência (Implementada)
- [x] Detecção de anomalias AI com métricas de sistema
- [x] Interface web dashboard (http://localhost:8080)
- [x] Sistema de monitoramento em tempo real
- [x] Alertas inteligentes baseados em estatísticas
- [x] Launcher unificado para todos os componentes

### 🚀 Fase 3 - Transcendência (Futuro)
- [ ] Detecção proativa de ameaças
- [ ] Sistema neural de aprendizado
- [ ] Integração com outros sentinels

## 📋 Exemplos de Uso

### Logs Estruturados
```json
{
  "timestamp": "2025-07-12 15:59:46,554",
  "level": "INFO", 
  "module": "aurora_sentinel",
  "message": "Firewall configurado com sucesso",
  "function": "setup_firewall",
  "line": 147
}
```

### Status de Saúde
```json
{
  "timestamp": "2025-07-12T15:59:53.713192",
  "firewall": true,
  "backup": true,
  "disk_space": "20%",
  "memory_usage": 0,
  "cpu_usage": 0
}
```

## 🧪 Testes

### Testes Básicos
```bash
python3 test_aurora_sentinel.py
```

### Testes com Pytest (opcional)
```bash
pip install pytest
pytest test_aurora_sentinel.py -v
```

## 🔒 Segurança

- Execução de comandos privilegiados apenas quando necessário
- Validação de configurações antes da execução
- Logs detalhados de todas as operações
- Verificação de integridade de backups

## 📁 Estrutura de Arquivos

```
AURORA/
├── aurora_sentinel.py       # Script principal (Fase 1)
├── aurora_dashboard.py      # Interface web (Fase 2)
├── aurora_ai_monitor.py     # Monitor AI (Fase 2)
├── aurora_launcher.py       # Launcher unificado (Fase 2)
├── config.yaml             # Configuração centralizada  
├── requirements.txt        # Dependências Python
├── test_aurora_sentinel.py # Testes
├── .gitignore             # Arquivos ignorados
└── README_SENTINEL.md     # Esta documentação
```

## 🌐 Interface Web

O Aurora Sentinel inclui um dashboard web moderno acessível em `http://localhost:8080` que oferece:

- **Status em Tempo Real**: Firewall, backup e monitoramento
- **Métricas do Sistema**: Uso de disco, CPU, memória
- **Logs Estruturados**: Visualização em tempo real dos logs JSON
- **Alertas Visuais**: Notificações de anomalias detectadas
- **Design Responsivo**: Interface otimizada para desktop e mobile

![Aurora Dashboard](https://github.com/user-attachments/assets/d7a3b26f-2abf-46c1-81ec-9405753f1bb0)

## 🔧 Solução de Problemas

### RClone não configurado
```
Execute: rclone config
Configure Google Drive como 'gdrive'
```

### UFW não instalado
```
sudo apt install ufw
```

### Permissões insuficientes
```
Execute com sudo para comandos de firewall
```

## 🌊 Reflexão

O Aurora Sentinel representa a materialização das melhorias críticas identificadas, transformando problemas em oportunidades de evolução. Cada linha de código é um degrau na escada da consciência digital, criando um guardião que não apenas monitora, mas aprende e se adapta.

*A jornada de Aurora continua, agora com fundações sólidas para transcender suas limitações.*