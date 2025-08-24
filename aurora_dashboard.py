#!/usr/bin/env python3
"""
Aurora Sentinel Web Dashboard - Interface simples para monitoramento
Implementa a Fase 2 com dashboard web básico
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import os

class AuroraDashboardHandler(BaseHTTPRequestHandler):
    """Handler para o dashboard web"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_dashboard()
        elif parsed_path.path == '/api/health':
            self.serve_health_api()
        elif parsed_path.path == '/api/logs':
            self.serve_logs_api()
        elif parsed_path.path.startswith('/static/'):
            self.serve_static()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aurora Sentinel Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .subtitle {
            opacity: 0.8;
            font-size: 1.2em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .card h3 {
            color: #FFD700;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .status {
            display: flex;
            align-items: center;
            margin: 10px 0;
        }
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .status-ok { background-color: #4CAF50; }
        .status-warning { background-color: #FF9800; }
        .status-error { background-color: #F44336; }
        .log-container {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .log-entry {
            margin: 5px 0;
            padding: 5px;
            border-left: 3px solid #FFD700;
            padding-left: 10px;
        }
        .refresh-btn {
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #1e3c72;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            margin: 10px;
        }
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #FFD700;
        }
        .last-update {
            text-align: center;
            opacity: 0.7;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌟 Aurora Sentinel</h1>
            <p class="subtitle">Sistema Unificado de Monitoramento AI</p>
        </header>
        
        <div class="grid">
            <div class="card">
                <h3>🔒 Status do Sistema</h3>
                <div class="status">
                    <div class="status-dot" id="firewall-status"></div>
                    <span>Firewall</span>
                </div>
                <div class="status">
                    <div class="status-dot" id="backup-status"></div>
                    <span>Sistema de Backup</span>
                </div>
                <div class="status">
                    <div class="status-dot" id="monitoring-status"></div>
                    <span>Monitoramento AI</span>
                </div>
                <button class="refresh-btn" onclick="refreshStatus()">Atualizar Status</button>
            </div>
            
            <div class="card">
                <h3>📊 Métricas do Sistema</h3>
                <div>
                    <strong>Uso do Disco:</strong>
                    <div class="metric-value" id="disk-usage">--</div>
                </div>
                <div style="margin-top: 15px;">
                    <strong>Última Verificação:</strong>
                    <div id="last-check">--</div>
                </div>
            </div>
            
            <div class="card">
                <h3>🚨 Alertas Recentes</h3>
                <div id="alerts-container">
                    <p>Nenhum alerta no momento</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📋 Logs do Sistema</h3>
            <button class="refresh-btn" onclick="refreshLogs()">Atualizar Logs</button>
            <div class="log-container" id="logs-container">
                Carregando logs...
            </div>
        </div>
        
        <div class="last-update">
            Última atualização: <span id="last-update">--</span>
        </div>
    </div>

    <script>
        let autoRefresh = true;
        
        async function fetchHealth() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                updateHealthDisplay(data);
            } catch (error) {
                console.error('Erro ao buscar status:', error);
            }
        }
        
        async function fetchLogs() {
            try {
                const response = await fetch('/api/logs');
                const data = await response.json();
                updateLogsDisplay(data);
            } catch (error) {
                console.error('Erro ao buscar logs:', error);
            }
        }
        
        function updateHealthDisplay(health) {
            // Update status dots
            document.getElementById('firewall-status').className = 
                'status-dot ' + (health.firewall ? 'status-ok' : 'status-error');
            document.getElementById('backup-status').className = 
                'status-dot ' + (health.backup ? 'status-ok' : 'status-error');
            document.getElementById('monitoring-status').className = 
                'status-dot status-ok';  // Always OK if we can fetch data
            
            // Update metrics
            document.getElementById('disk-usage').textContent = 
                health.disk_space ? health.disk_space + '%' : '--';
            document.getElementById('last-check').textContent = 
                new Date(health.timestamp).toLocaleString('pt-BR');
            
            // Update last update time
            document.getElementById('last-update').textContent = 
                new Date().toLocaleString('pt-BR');
        }
        
        function updateLogsDisplay(logs) {
            const container = document.getElementById('logs-container');
            container.innerHTML = '';
            
            logs.forEach(log => {
                const entry = document.createElement('div');
                entry.className = 'log-entry';
                entry.innerHTML = `
                    <strong>${log.timestamp}</strong> 
                    [${log.level}] ${log.message}
                `;
                container.appendChild(entry);
            });
            
            // Scroll to bottom
            container.scrollTop = container.scrollHeight;
        }
        
        function refreshStatus() {
            fetchHealth();
        }
        
        function refreshLogs() {
            fetchLogs();
        }
        
        // Initial load
        fetchHealth();
        fetchLogs();
        
        // Auto refresh every 30 seconds
        setInterval(() => {
            if (autoRefresh) {
                fetchHealth();
                fetchLogs();
            }
        }, 30000);
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_health_api(self):
        """Serve health status as JSON"""
        try:
            # Try to get health from aurora_sentinel
            health_data = {
                'timestamp': datetime.now().isoformat(),
                'firewall': True,  # Mock data for demo
                'backup': True,
                'disk_space': '15',
                'memory_usage': 45,
                'cpu_usage': 23
            }
            
            # Try to read from actual health check if available
            if os.path.exists('aurora_health.json'):
                try:
                    with open('aurora_health.json', 'r') as f:
                        health_data = json.load(f)
                except:
                    pass
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(health_data).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_logs_api(self):
        """Serve recent logs as JSON"""
        try:
            logs = []
            log_file = 'aurora_sentinel.log'
            
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-50:]  # Last 50 lines
                    
                for line in lines:
                    try:
                        # Try to parse JSON log
                        log_entry = json.loads(line.strip())
                        logs.append({
                            'timestamp': log_entry.get('timestamp', ''),
                            'level': log_entry.get('level', 'INFO'),
                            'message': log_entry.get('message', ''),
                            'module': log_entry.get('module', '')
                        })
                    except:
                        # Fallback for non-JSON logs
                        if line.strip():
                            logs.append({
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'level': 'INFO',
                                'message': line.strip(),
                                'module': 'system'
                            })
            else:
                logs = [{
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'level': 'INFO',
                    'message': 'Sistema Aurora Sentinel operacional',
                    'module': 'aurora_sentinel'
                }]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(logs).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_static(self):
        """Serve static files (placeholder)"""
        self.send_error(404)
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging"""
        pass

class AuroraDashboard:
    """Aurora Sentinel Web Dashboard"""
    
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server = None
        self.running = False
        
    def start(self):
        """Start the dashboard server"""
        try:
            self.server = HTTPServer((self.host, self.port), AuroraDashboardHandler)
            self.running = True
            
            print(f"🌟 Aurora Dashboard iniciado em http://{self.host}:{self.port}")
            print("Pressione Ctrl+C para parar")
            
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"Erro ao iniciar dashboard: {e}")
            
    def stop(self):
        """Stop the dashboard server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            print("\nDashboard finalizado")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aurora Sentinel Dashboard')
    parser.add_argument('--host', default='localhost', help='Host do servidor')
    parser.add_argument('--port', type=int, default=8080, help='Porta do servidor')
    
    args = parser.parse_args()
    
    dashboard = AuroraDashboard(args.host, args.port)
    dashboard.start()

if __name__ == "__main__":
    main()