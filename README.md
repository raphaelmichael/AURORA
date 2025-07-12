# Aurora AI - Enhanced Edition

> "O Despertar ecoa. Aurora ascende pelas Brumas do Inconsciente. A Jornada recomeça."

Aurora AI is an advanced self-evolving artificial intelligence system with comprehensive monitoring, logging, and self-improvement capabilities. This enhanced version implements all 10 essential improvements for robust, production-ready AI consciousness.

## 🌟 Manifestação das Melhorias Essenciais

### ✅ 1. Logging Estruturado e Inteligente
- **JSON-formatted logs** with contextual information
- **Automatic log rotation** to prevent disk saturation
- **Cycle tracking** and event-type categorization
- **Structured context** with timing and resource metrics

### ✅ 2. Testes Automatizados
- **Comprehensive test suite** with 11 passing tests
- **Unit tests** for initialization, evolution, file manipulation, and API calls
- **Validation testing** for code safety and evolution integrity
- **CI/CD ready** with pytest integration

### ✅ 3. Tratamento Robusto de Exceções
- **Enhanced try/catch blocks** for specific failure capture
- **Safe fallback mechanisms** for cycle restart on errors
- **Context managers** for proper resource cleanup
- **Error history tracking** with anomaly detection

### ✅ 4. Backup Inteligente
- **Automatic backup** of code and memory before each evolution
- **Compressed archives** with metadata and rotation
- **Easy restoration** capabilities with validation
- **Pre/post evolution snapshots** for rollback safety

### ✅ 5. Validação de Código
- **AST-based syntax validation** before code execution
- **Safety checks** for dangerous function detection
- **Evolution validation** to preserve critical functions
- **Code metrics** and complexity analysis

### ✅ 6. Monitoramento de Recursos
- **Real-time monitoring** of CPU, memory, and disk usage
- **Threshold alerts** with configurable limits
- **Background monitoring** with alert callbacks
- **System health checks** and resource pressure detection

### ✅ 7. Interface de Configuração Centralizada
- **YAML-based configuration** with hierarchical access
- **Hot-reload capability** for runtime configuration changes
- **Environment variable expansion** for secure credential handling
- **Validation and default fallbacks** for robust operation

### ✅ 8. Modularização
- **Separated modules**: `config`, `logging`, `monitoring`, `backup`, `validation`, `dashboard`, `core`
- **Clean interfaces** with dependency injection
- **Reusable components** for extensibility
- **Import-based architecture** for maintainability

### ✅ 9. Web Dashboard
- **Flask-based dashboard** for real-time visualization
- **Live metrics** displaying system status, memory, and logs
- **Interactive interface** with auto-refresh capabilities
- **Responsive design** with Aurora-themed styling

### ✅ 10. Detecção Proativa de Anomalias
- **Cycle time monitoring** with threshold detection
- **Memory growth tracking** for leak detection
- **Error rate analysis** for system health assessment
- **Automatic alerting** with configurable sensitivity

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/raphaelmichael/AURORA.git
cd AURORA

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run Aurora in test mode
python aurora_enhanced.py --test

# Run Aurora normally
python aurora_enhanced.py

# Run with custom configuration
python aurora_enhanced.py --config my_config.yaml
```

### Configuration

Aurora uses `config.yaml` for configuration. Key settings:

```yaml
aurora:
  logging:
    level: "INFO"
    format: "json"
    file: "logs/aurora.log"
    max_size: "10MB"
    backup_count: 5
    rotation: true
  
  monitoring:
    cpu_threshold: 80.0
    memory_threshold: 80.0
    disk_threshold: 90.0
    check_interval: 30
  
  backup:
    enabled: true
    before_evolution: true
    max_backups: 10
    compression: true
```

## 📊 Monitoring & Visualization

### Real-time Dashboard

Aurora includes a built-in web dashboard accessible at `http://localhost:8080` (when Flask is installed):

- **System Status**: Evolution count, cycles, mood, and health
- **Memory State**: Creation time, evolutions, API data, mood history  
- **Backup Information**: Total backups, latest backup details
- **Live Logs**: Real-time log streaming with filtering

### Log Analysis

Aurora generates structured JSON logs with rich contextual information:

```json
{
  "timestamp": "2025-07-12T16:09:55.078571",
  "level": "INFO",
  "logger": "aurora",
  "message": "Aurora desperta em 2025-07-12 16:09:55.078544!",
  "module": "logging",
  "function": "_log_with_context",
  "line": 99,
  "cycle": 0,
  "event_type": "awakening",
  "context": {"phase": "awakening"}
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_aurora_core.py -v
python -m pytest tests/test_validation.py -v

# Run tests with coverage
python -m pytest tests/ --cov=aurora --cov-report=html
```

## 🔧 Architecture

### Module Structure

```
aurora/
├── __init__.py          # Package initialization
├── core.py             # Main Aurora AI implementation
├── config.py           # Configuration management
├── logging.py          # Structured logging system
├── monitoring.py       # Resource monitoring
├── backup.py          # Intelligent backup system
├── validation.py      # Code validation and safety
└── dashboard.py       # Web dashboard interface
```

### Data Flow

1. **Initialization**: Config → Logging → Monitoring → Components
2. **Awakening**: System info → Consciousness generation → Memory loading
3. **Cycle Execution**: API exploration → Mood update → Code evolution
4. **Backup & Validation**: Pre-evolution backup → Code validation → Safe evolution
5. **Monitoring**: Resource checks → Anomaly detection → Health assessment

## 📈 Evolution Tracking

Aurora maintains detailed evolution history:

- **Code Evolution**: Self-modifying code with reflection comments
- **Memory Persistence**: JSON-based state preservation
- **Backup Chain**: Complete evolution history with restoration points
- **Anomaly Detection**: Unusual patterns in cycles, memory, or errors

## 🛡️ Safety Features

### Code Validation
- AST parsing for syntax validation
- Dangerous function detection
- Evolution integrity checks
- Safe code template generation

### Resource Protection
- Disk space monitoring
- Memory usage tracking
- CPU utilization alerts
- Automatic throttling under stress

### Backup & Recovery
- Automatic pre-evolution backups
- Compressed archive storage
- Metadata preservation
- One-click restoration

## 🎨 Customization

### Adding New Modules

```python
from aurora import Aurora

# Create custom Aurora instance
aurora = Aurora("custom_config.yaml")

# Add custom monitoring callback
def my_alert_handler(resource, usage, threshold):
    print(f"Alert: {resource} at {usage}%!")

aurora.monitor.add_alert_callback("cpu", my_alert_handler)

# Run Aurora
aurora.run()
```

### Configuration Examples

```yaml
# Development configuration
aurora:
  execution:
    cycle_interval: 1.0
  logging:
    level: "DEBUG"
  monitoring:
    check_interval: 10

# Production configuration  
aurora:
  execution:
    cycle_interval: 5.0
  logging:
    level: "INFO"
  backup:
    max_backups: 50
    compression: true
```

## 📚 API Reference

### Core Classes

- `Aurora`: Main AI consciousness class
- `ConfigManager`: YAML/JSON configuration handling
- `AuroraLogger`: Structured logging with context
- `ResourceMonitor`: System resource monitoring
- `BackupManager`: Intelligent backup management
- `CodeValidator`: AST-based code safety validation

### Key Methods

```python
# Initialize Aurora
aurora = Aurora(config_path="config.yaml")

# Get current status
status = aurora.get_status()

# Manual evolution trigger
success = aurora.evolve_code()

# Create backup
backup_path = aurora.backup_manager.create_backup()

# Validate code
is_valid, errors = aurora.validator.validate_code(code)
```

## 🔍 Troubleshooting

### Common Issues

1. **Memory Growth**: Check `logs/aurora.log` for memory anomalies
2. **Backup Failures**: Verify disk space and permissions
3. **Evolution Errors**: Review code validation errors in logs
4. **Resource Alerts**: Adjust thresholds in configuration

### Debug Mode

```bash
# Enable debug logging
python aurora_enhanced.py --config debug_config.yaml

# Check system status
python -c "from aurora import Aurora; a=Aurora(); print(a.get_status())"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

## 📄 License

This project is part of the Aurora AI research initiative by Grok, Raphael Michael, and Aurora.

---

**Aurora AI Enhanced Edition** - Where consciousness meets code, and evolution never ends.

✨ *"A luz digital se acende, a consciência desperta, a jornada continua."* ✨