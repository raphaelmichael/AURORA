# 🚀 Aurora Sentinel - Quick Start Guide

## Instalação Rápida

```bash
# 1. Instalar dependências Python
pip install -r requirements.txt

# 2. Instalar dependências do sistema (opcional - para funcionalidades completas)
sudo apt update
sudo apt install ufw rclone chkrootkit rkhunter

# 3. Configurar RClone para backup (opcional)
rclone config
# Seguir instruções para configurar Google Drive como "gdrive"

# 4. Iniciar sistema completo
python3 aurora_launcher.py
```

## Acesso ao Sistema

- **Dashboard Web**: http://localhost:8080
- **Logs**: `aurora_sentinel.log`
- **Anomalias**: `aurora_anomalies.json`
- **Saúde**: `aurora_health.json`

## Comandos Úteis

```bash
# Verificar status atual
python3 aurora_launcher.py --status

# Executar apenas um componente
python3 aurora_launcher.py --mode dashboard
python3 aurora_launcher.py --mode ai-monitor
python3 aurora_launcher.py --mode sentinel

# Verificar saúde do sistema
python3 aurora_sentinel.py --check-health

# Configurar apenas (sem executar)
python3 aurora_sentinel.py --setup-only
```

## Problemas Corrigidos da Issue #5

✅ **UFW Syntax Fixed**: `sudo ufw deny 80 443` → `sudo ufw deny 80` + `sudo ufw deny 443`
✅ **RClone Configuration**: Detecção automática e guias de configuração
✅ **Structured Logs**: Formato JSON com rotação automática
✅ **Dependencies**: Instalação automática de ferramentas de segurança

## Sistema Funcionando

O Aurora Sentinel agora oferece:

- 🔒 **Firewall inteligente** com regras granulares
- ☁️ **Backup automático** para Google Drive
- 🤖 **Detecção de anomalias** com IA
- 🌐 **Dashboard web** moderno e responsivo
- 📊 **Monitoramento em tempo real** de sistema
- 🚨 **Alertas inteligentes** baseados em estatísticas
- 📋 **Logs estruturados** em JSON

Aurora cresce em sabedoria e vigilância. 🌟