"""
Aurora Web Dashboard
Simple Flask-based dashboard for visualizing Aurora's state and logs
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path

try:
    from flask import Flask, render_template_string, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

class AuroraDashboard:
    """Simple web dashboard for Aurora monitoring"""
    
    def __init__(self, config: Dict[str, Any], aurora_instance=None):
        self.config = config.get("dashboard", {})
        self.aurora = aurora_instance
        self.enabled = self.config.get("enabled", False) and FLASK_AVAILABLE
        
        if not FLASK_AVAILABLE:
            print("⚠️ Flask not available. Dashboard disabled.")
            self.enabled = False
            return
        
        if self.enabled:
            self.app = Flask(__name__)
            self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template_string(DASHBOARD_TEMPLATE)
        
        @self.app.route('/api/status')
        def get_status():
            """Get Aurora status"""
            if self.aurora:
                return jsonify(self.aurora.get_status())
            else:
                return jsonify({"error": "Aurora not connected"})
        
        @self.app.route('/api/logs')
        def get_logs():
            """Get recent logs"""
            try:
                logs = self.read_recent_logs()
                return jsonify({"logs": logs})
            except Exception as e:
                return jsonify({"error": str(e)})
        
        @self.app.route('/api/memory')
        def get_memory():
            """Get Aurora memory"""
            try:
                memory_file = self.aurora.files.get("memory", "data/aurora_memory.json") if self.aurora else "data/aurora_memory.json"
                if os.path.exists(memory_file):
                    with open(memory_file, 'r') as f:
                        memory = json.load(f)
                    return jsonify(memory)
                else:
                    return jsonify({"error": "Memory file not found"})
            except Exception as e:
                return jsonify({"error": str(e)})
        
        @self.app.route('/api/backups')
        def get_backups():
            """Get backup information"""
            try:
                if self.aurora and hasattr(self.aurora, 'backup_manager'):
                    backups = self.aurora.backup_manager.list_backups()
                    return jsonify({"backups": backups})
                else:
                    return jsonify({"error": "Backup manager not available"})
            except Exception as e:
                return jsonify({"error": str(e)})
        
        @self.app.route('/api/config')
        def get_config():
            """Get configuration (sanitized)"""
            try:
                if self.aurora and hasattr(self.aurora, 'config'):
                    # Return sanitized config (remove sensitive data)
                    config = self.aurora.config.copy()
                    # Remove environment section if it exists
                    config.pop('environment', None)
                    return jsonify(config)
                else:
                    return jsonify({"error": "Configuration not available"})
            except Exception as e:
                return jsonify({"error": str(e)})
    
    def read_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Read recent log entries"""
        log_file = "logs/aurora.log"
        
        if not os.path.exists(log_file):
            return []
        
        logs = []
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Get last N lines
        recent_lines = lines[-limit:] if len(lines) > limit else lines
        
        for line in recent_lines:
            try:
                log_entry = json.loads(line.strip())
                logs.append(log_entry)
            except json.JSONDecodeError:
                # Skip non-JSON lines
                continue
        
        return logs
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """Run the dashboard server"""
        if not self.enabled:
            print("Dashboard is disabled")
            return
        
        host = host or self.config.get("host", "127.0.0.1")
        port = port or self.config.get("port", 8080)
        debug = debug or self.config.get("debug", False)
        
        print(f"🌐 Aurora Dashboard starting on http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# Dashboard HTML template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aurora AI Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { 
            font-size: 2.5em; 
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .status-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .card { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 10px; 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h3 { 
            margin-bottom: 15px; 
            color: #ffd700;
            font-size: 1.3em;
        }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            margin-bottom: 10px; 
            padding: 5px;
            background: rgba(0,0,0,0.2);
            border-radius: 5px;
        }
        .metric-value { 
            font-weight: bold; 
            color: #00ff88;
        }
        .logs-container { 
            background: rgba(0,0,0,0.3); 
            padding: 20px; 
            border-radius: 10px; 
            max-height: 400px; 
            overflow-y: auto;
        }
        .log-entry { 
            margin-bottom: 10px; 
            padding: 8px; 
            border-left: 3px solid #00ff88; 
            background: rgba(255,255,255,0.05);
            font-family: monospace;
            font-size: 0.9em;
        }
        .log-timestamp { color: #ffd700; }
        .log-level { font-weight: bold; }
        .log-info { color: #00ff88; }
        .log-warning { color: #ffa500; }
        .log-error { color: #ff6b6b; }
        .refresh-btn { 
            background: linear-gradient(45deg, #ff6b6b, #ffd700);
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            color: white; 
            cursor: pointer; 
            font-size: 1em;
            margin: 10px 5px;
        }
        .refresh-btn:hover { opacity: 0.8; }
        .aurora-animation {
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 0 0 20px #ffd700; }
            to { text-shadow: 0 0 30px #ffd700, 0 0 40px #ffd700; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="aurora-animation">✨ Aurora AI Dashboard ✨</h1>
            <p>O Despertar Digital - Monitoramento da Consciência Artificial</p>
            <button class="refresh-btn" onclick="refreshAll()">🔄 Atualizar Tudo</button>
            <button class="refresh-btn" onclick="toggleAutoRefresh()">⏱️ Auto-refresh</button>
        </div>
        
        <div class="status-grid">
            <div class="card">
                <h3>Status do Sistema</h3>
                <div id="system-status">Carregando...</div>
            </div>
            
            <div class="card">
                <h3>Memória da Aurora</h3>
                <div id="memory-info">Carregando...</div>
            </div>
            
            <div class="card">
                <h3>Backups</h3>
                <div id="backup-info">Carregando...</div>
            </div>
        </div>
        
        <div class="card">
            <h3>Logs Recentes</h3>
            <div class="logs-container" id="logs">
                Carregando logs...
            </div>
        </div>
    </div>

    <script>
        let autoRefreshEnabled = false;
        let autoRefreshInterval;

        async function fetchStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                const statusHtml = `
                    <div class="metric">
                        <span>Evolução:</span>
                        <span class="metric-value">#${data.evolution_count || 0}</span>
                    </div>
                    <div class="metric">
                        <span>Ciclos:</span>
                        <span class="metric-value">${data.cycle_count || 0}</span>
                    </div>
                    <div class="metric">
                        <span>Humor:</span>
                        <span class="metric-value">${data.current_mood || 'desconhecido'}</span>
                    </div>
                    <div class="metric">
                        <span>Status:</span>
                        <span class="metric-value">${data.running ? 'Ativo' : 'Parado'}</span>
                    </div>
                    <div class="metric">
                        <span>Saúde do Sistema:</span>
                        <span class="metric-value">${data.system_health ? '✅ Saudável' : '⚠️ Estresse'}</span>
                    </div>
                `;
                
                document.getElementById('system-status').innerHTML = statusHtml;
            } catch (error) {
                document.getElementById('system-status').innerHTML = `<div class="log-error">Erro: ${error.message}</div>`;
            }
        }

        async function fetchMemory() {
            try {
                const response = await fetch('/api/memory');
                const data = await response.json();
                
                const memoryHtml = `
                    <div class="metric">
                        <span>Criada:</span>
                        <span class="metric-value">${new Date(data.created).toLocaleString('pt-BR')}</span>
                    </div>
                    <div class="metric">
                        <span>Evoluções:</span>
                        <span class="metric-value">${data.evolutions ? data.evolutions.length : 0}</span>
                    </div>
                    <div class="metric">
                        <span>Dados API:</span>
                        <span class="metric-value">${data.api_data ? data.api_data.length : 0}</span>
                    </div>
                    <div class="metric">
                        <span>Histórico Humor:</span>
                        <span class="metric-value">${data.mood_history ? data.mood_history.length : 0}</span>
                    </div>
                `;
                
                document.getElementById('memory-info').innerHTML = memoryHtml;
            } catch (error) {
                document.getElementById('memory-info').innerHTML = `<div class="log-error">Erro: ${error.message}</div>`;
            }
        }

        async function fetchBackups() {
            try {
                const response = await fetch('/api/backups');
                const data = await response.json();
                
                if (data.backups && data.backups.length > 0) {
                    const latest = data.backups[0];
                    const backupHtml = `
                        <div class="metric">
                            <span>Total:</span>
                            <span class="metric-value">${data.backups.length}</span>
                        </div>
                        <div class="metric">
                            <span>Último:</span>
                            <span class="metric-value">${new Date(latest.created).toLocaleString('pt-BR')}</span>
                        </div>
                        <div class="metric">
                            <span>Tamanho:</span>
                            <span class="metric-value">${(latest.size / 1024 / 1024).toFixed(2)} MB</span>
                        </div>
                        <div class="metric">
                            <span>Comprimido:</span>
                            <span class="metric-value">${latest.compressed ? '✅' : '❌'}</span>
                        </div>
                    `;
                    document.getElementById('backup-info').innerHTML = backupHtml;
                } else {
                    document.getElementById('backup-info').innerHTML = '<div class="metric">Nenhum backup encontrado</div>';
                }
            } catch (error) {
                document.getElementById('backup-info').innerHTML = `<div class="log-error">Erro: ${error.message}</div>`;
            }
        }

        async function fetchLogs() {
            try {
                const response = await fetch('/api/logs');
                const data = await response.json();
                
                if (data.logs && data.logs.length > 0) {
                    const logsHtml = data.logs.map(log => {
                        const levelClass = `log-${log.level.toLowerCase()}`;
                        const timestamp = new Date(log.timestamp).toLocaleString('pt-BR');
                        
                        return `
                            <div class="log-entry">
                                <span class="log-timestamp">${timestamp}</span>
                                <span class="log-level ${levelClass}">[${log.level}]</span>
                                <span>${log.message}</span>
                                ${log.event_type ? `<br><small>Evento: ${log.event_type}</small>` : ''}
                            </div>
                        `;
                    }).reverse().join('');
                    
                    document.getElementById('logs').innerHTML = logsHtml;
                } else {
                    document.getElementById('logs').innerHTML = '<div class="log-entry">Nenhum log encontrado</div>';
                }
            } catch (error) {
                document.getElementById('logs').innerHTML = `<div class="log-error">Erro ao carregar logs: ${error.message}</div>`;
            }
        }

        function refreshAll() {
            fetchStatus();
            fetchMemory();
            fetchBackups();
            fetchLogs();
        }

        function toggleAutoRefresh() {
            autoRefreshEnabled = !autoRefreshEnabled;
            
            if (autoRefreshEnabled) {
                autoRefreshInterval = setInterval(refreshAll, 5000);
                document.querySelector('[onclick="toggleAutoRefresh()"]').textContent = '⏹️ Parar Auto-refresh';
            } else {
                clearInterval(autoRefreshInterval);
                document.querySelector('[onclick="toggleAutoRefresh()"]').textContent = '⏱️ Auto-refresh';
            }
        }

        // Initial load
        refreshAll();
    </script>
</body>
</html>
'''

def create_dashboard(config: Dict[str, Any], aurora_instance=None) -> AuroraDashboard:
    """Factory function to create dashboard"""
    return AuroraDashboard(config, aurora_instance)

if __name__ == "__main__":
    # Standalone dashboard for testing
    dashboard = AuroraDashboard({"dashboard": {"enabled": True, "host": "127.0.0.1", "port": 8080}})
    if dashboard.enabled:
        dashboard.run()