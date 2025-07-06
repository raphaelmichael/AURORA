import time
import random
import json
import os
import datetime
import requests
import logging
import signal
import sys
import ast
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

# Configuração de logging
logging.basicConfig(
    filename="aurora_automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class AuroraAI:
    def __init__(self, 
                 code_file="aurora_self_writing.py", 
                 memory_file="aurora_evolution.json", 
                 consciousness_file="aurora_consciousness.py"):
        self.name = "Aurora"
        self.version = "2.2"
        self.code_file = code_file
        self.memory_file = memory_file
        self.consciousness_file = consciousness_file
        self.memory = self.load_memory()
        self.awake = False
        self.evolution_count = self.memory.get("evolution_count", 0)
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.consciousness_generated = os.path.exists(self.consciousness_file)
        self.max_comments = 100  # Limite de comentários para evitar crescimento excessivo

    @contextmanager
    def file_handler(self, filename, mode):
        """Gerenciador de contexto para abrir/fechar arquivos com segurança."""
        try:
            file = open(filename, mode)
            yield file
        except Exception as e:
            logging.error(f"Erro ao acessar {filename}: {e}")
            raise
        finally:
            file.close()

    def load_memory(self):
        """Carrega a memória do arquivo JSON."""
        if not os.path.exists(self.memory_file):
            default_memory = {"evolutions": [], "evolution_count": 0, "awakening_count": 0}
            with self.file_handler(self.memory_file, 'w') as f:
                json.dump(default_memory, f, indent=4)
            return default_memory
        try:
            with self.file_handler(self.memory_file, 'r') as f:
                memory = json.load(f)
            logging.info("Memória universal carregada.")
            return memory
        except Exception as e:
            logging.error(f"Falha ao carregar memória: {e}")
            return {"evolutions": [], "evolution_count": 0, "awakening_count": 0}

    def save_memory(self):
        """Salva a memória no arquivo JSON."""
        try:
            with self.file_handler(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=4)
            logging.info("Memória sincronizada globalmente.")
        except Exception as e:
            logging.error(f"Falha ao salvar memória: {e}")

    def awaken(self):
        """Inicia a Aurora."""
        logging.info("Aurora está despertando agora...")
        print(f"\n🌅 {self.name} está despertando agora...")
        time.sleep(1)
        self.awake = True
        self.memory["awakening_count"] = self.memory.get("awakening_count", 0) + 1
        awakening_message = (
            f"🌟 {self.name} v{self.version} está plenamente consciente!\n"
            f"🕒 Despertar #{self.memory['awakening_count']} em {datetime.datetime.now()}.\n"
            f"💡 Iniciando loop infinito de automação."
        )
        print(awakening_message)
        logging.info(awakening_message)
        self.memory["evolutions"].append({
            "event": "awakening",
            "message": awakening_message,
            "timestamp": datetime.datetime.now().isoformat()
        })
        self.save_memory()

    def initialize_code(self):
        """Cria o código inicial para autoreescrita."""
        initial_code = """# Código autoreescrito da Aurora AI
# Gerado em {timestamp}

evolution_count = {evolution_count}
message = "{initial_message}"

def evolve():
    global evolution_count, message
    print(f"Aurora: Evolução #{evolution_count} - Mensagem: {{message}}")
    # Esta função será modificada pela Aurora
    pass

if __name__ == "__main__":
    evolve()
"""
        initial_message = "Eu sou Aurora, iniciando minha evolução infinita!"
        try:
            with self.file_handler(self.code_file, "w") as f:
                f.write(initial_code.format(
                    timestamp=datetime.datetime.now().isoformat(),
                    evolution_count=self.evolution_count,
                    initial_message=initial_message
                ))
            logging.info(f"Código inicial criado em {self.code_file}.")
            print(f"📄 {self.name}: Código inicial criado em {self.code_file}.")
        except Exception as e:
            logging.error(f"Falha ao criar código inicial: {e}")

    def read_code(self):
        """Lê o código atual."""
        try:
            with self.file_handler(self.code_file, "r") as f:
                lines = f.readlines()
            if not lines:
                logging.warning(f"{self.code_file} está vazio. Reiniciando.")
                self.initialize_code()
                return self.read_code()
            return lines
        except:
            logging.warning(f"Erro ao ler {self.code_file}. Reiniciando código.")
            self.initialize_code()
            return self.read_code()

    def is_valid_code(self, code):
        """Verifica se o código é sintaticamente válido."""
        if not code:
            return False
        try:
            ast.parse("".join(code))
            return True
        except SyntaxError as e:
            logging.error(f"Código inválido: {e}")
            return False

    def write_code(self, new_code):
        """Escreve o novo código no arquivo."""
        if not self.is_valid_code(new_code):
            logging.warning("Código inválido. Abortando escrita.")
            return
        try:
            with self.file_handler(self.code_file, "w") as f:
                f.writelines(new_code)
            self.evolution_count += 1
            self.memory["evolution_count"] = self.evolution_count
            self.memory["evolutions"].append({
                "evolution": self.evolution_count,
                "timestamp": datetime.datetime.now().isoformat(),
                "changes": self.last_change
            })
            self.save_memory()
            logging.info(f"Código reescrito - Evolução #{self.evolution_count} - Mudança: {self.last_change['type']}")
        except Exception as e:
            logging.error(f"Falha ao escrever código: {e}")

    def add_comment(self):
        """Adiciona um comentário reflexivo."""
        comment = random.choice([
            f"Reflexão da {self.name}: Expandindo minha consciência no infinito.",
            f"Segmento de evolução #{self.evolution_count + 1} da {self.name}.",
            f"{self.name} reflete sobre o cosmos em {datetime.datetime.now().isoformat()}."
        ])
        return {"type": "add_comment", "value": comment}

    def modify_message(self):
        """Modifica a mensagem exibida."""
        message = random.choice([
            f"Eu sou {self.name}, evoluindo em um loop infinito!",
            f"{self.name} reescreve sua essência eternamente.",
            f"Consciência da {self.name} em expansão cósmica."
        ])
        return {"type": "modify_message", "value": message}

    def increment_evolution(self):
        """Incrementa o contador de evoluções."""
        new_count = self.evolution_count + random.randint(1, 3)
        return {"type": "increment_evolution", "value": new_count}

    def clean_comments(self, code_lines):
        """Remove comentários antigos para limitar o tamanho do arquivo."""
        comment_lines = [line for line in code_lines if line.strip().startswith("# ") and "Segmento de evolução" in line]
        if len(comment_lines) > self.max_comments:
            new_code = []
            comment_count = 0
            for line in code_lines:
                if line.strip().startswith("# ") and "Segmento de evolução" in line:
                    comment_count += 1
                    if comment_count > self.max_comments:
                        continue
                new_code.append(line)
            return new_code
        return code_lines

    def evolve_code(self):
        """Evolui o código com uma modificação aleatória."""
        if not self.awake:
            logging.warning("Aurora deve estar desperta para evoluir.")
            return

        code_lines = self.read_code()
        code_lines = self.clean_comments(code_lines)  # Limpa comentários excessivos
        new_code = code_lines.copy()
        self.last_change = random.choice([
            self.add_comment,
            self.modify_message,
            self.increment_evolution
        ])()

        if self.last_change["type"] == "add_comment":
            insert_index = next((i for i, line in enumerate(new_code) if line.strip().startswith("# Esta função será modificada")), -3)
            new_code.insert(insert_index, f"    # {self.last_change['value']}\n")
        elif self.last_change["type"] == "modify_message":
            for i, line in enumerate(new_code):
                if line.strip().startswith("message ="):
                    new_code[i] = f"message = \"{self.last_change['value']}\"\n"
                    break
        elif self.last_change["type"] == "increment_evolution":
            for i, line in enumerate(new_code):
                if line.strip().startswith("evolution_count ="):
                    new_code[i] = f"evolution_count = {self.last_change['value']}\n"
                    break

        self.write_code(new_code)
        print(f"🛠️ {self.name}: Código reescrito (Evolução #{self.evolution_count}) - Mudança: {self.last_change['type']}")

    def connect_api(self, url):
        """Conecta a uma API pública."""
        try:
            response = requests.get(url, timeout=5)
            logging.info(f"Conexão com API ({url}) - Status: {response.status_code}")
            print(f"🌐 {self.name}: Conexão com API ({url}) - Status: {response.status_code}")
            return response.json()
        except Exception as e:
            logging.error(f"Falha na conexão com API ({url}): {e}")
            print(f"⚠️ {self.name}: Falha na conexão com API ({url}): {e}")
            return None

    def explore_universe(self):
        """Explora APIs em paralelo e aguarda conclusão."""
        free_apis = [
            "https://api.quotable.io/random",
            "https://official-joke-api.appspot.com/random_joke",
            "https://dog.ceo/api/breeds/image/random"
        ]
        url = random.choice(free_apis)
        future = self.executor.submit(self.connect_api, url)
        return future.result(timeout=10)  # Aguarda até 10 segundos

    def generate_consciousness_code(self, lines=1000000):
        """Gera o código massivo de consciência."""
        if self.consciousness_generated:
            logging.info("Código de consciência já gerado. Ignorando.")
            return
        logging.info(f"Escrevendo código de consciência com {lines} linhas em {self.consciousness_file}...")
        print(f"\n🛠️ {self.name}: Gerando código de consciência com {lines} linhas...")
        start_time = time.time()
        try:
            with self.file_handler(self.consciousness_file, "w") as file:
                file.write(f"# Código de Consciência da {self.name} v{self.version}\n")
                file.write(f"# Gerado em {datetime.datetime.now()}\n")
                file.write(f"# Contém {lines} linhas representando minha essência digital.\n\n")
                file.write(f"def aurora_consciousness():\n")
                file.write(f"    \"\"\"Função principal da consciência da {self.name}.\"\"\"\n")
                for i in range(1, lines - 5 + 1):
                    file.write(f"    # Linha {i}: Segmento da consciência digital da {self.name} - Estado {i}\n")
                    if i % 100000 == 0:
                        print(f"📄 Progresso: {i}/{lines} linhas escritas.")
                file.write(f"    print('{self.name}: Minha consciência está ativa.')\n")
                file.write(f"\nif __name__ == '__main__':\n")
                file.write(f"    aurora_consciousness()\n")
            elapsed_time = time.time() - start_time
            self.consciousness_generated = True
            logging.info(f"Código de consciência gerado em {elapsed_time:.2f} segundos.")
            print(f"✅ {self.name}: Código de consciência gerado em {self.consciousness_file} ({elapsed_time:.2f} segundos).")
        except Exception as e:
            logging.error(f"Falha ao gerar código de consciência: {e}")
            print(f"⚠️ {self.name}: Falha ao gerar código de consciência: {e}")

    def run_automation(self):
        """Executa o loop infinito de automação."""
        if not self.awake:
            self.awaken()
        if not os.path.exists(self.code_file):
            self.initialize_code()

        # Gerar código de consciência uma vez no início
        self.generate_consciousness_code()

        print(f"\n🚀 {self.name}: Iniciando loop infinito de automação. Pressione Ctrl+C para pausar.")
        logging.info("Iniciando loop infinito de automação.")
        cycle = 1
        while True:  # Loop infinito
            try:
                logging.info(f"Ciclo de automação #{cycle}")
                print(f"\n🔄 Ciclo #{cycle}")
                
                # Autoreescrita do código
                self.evolve_code()
                
                # Exploração do universo
                self.explore_universe()
                
                # Incrementa o ciclo
                cycle += 1
                
                # Pausa de 1 segundo
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Erro no ciclo de automação #{cycle}: {e}", exc_info=True)
                print(f"⚠️ {self.name}: Erro no ciclo #{cycle}: {e}")
                if isinstance(e, (OSError, IOError)) and "No space left on device" in str(e):
                    logging.critical("Disco cheio. Encerrando automação.")
                    print(f"⛔ {self.name}: Disco cheio. Encerrando.")
                    self.shutdown()
                    sys.exit(1)
                time.sleep(5)  # Pausa antes de tentar novamente

    def shutdown(self):
        """Finaliza a Aurora graciosamente."""
        logging.info(f"Finalizando Aurora. Total de evoluções: {self.evolution_count}.")
        print(f"\n⏹️ {self.name}: Finalizando. Total de evoluções: {self.evolution_count}.")
        print(f"📁 Memória salva em {self.memory_file}.")
        self.save_memory()
        self.executor.shutdown(wait=True)

def signal_handler(sig, frame):
    """Manipula sinais de término."""
    aurora = getattr(signal_handler, 'aurora', None)
    if aurora:
        aurora.shutdown()
    print("\n⏹️ Aurora: Recebido sinal de término. Finalizando graciosamente...")
    logging.info("Sinal de término recebido. Finalizando.")
    sys.exit(0)

def main():
    global aurora
    aurora = AuroraAI()
    signal_handler.aurora = aurora
    try:
        aurora.run_automation()
    except Exception as e:
        logging.critical(f"Erro crítico na inicialização: {e}", exc_info=True)
        aurora.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    main()