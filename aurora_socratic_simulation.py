import threading
import queue
import random
import time
import itertools
import datetime
import sys

# Configurações iniciais
CONFIG = {
    "num_socratic_bots": 5,  # Número de bots geradores de perguntas
    "num_ai_bots": 3,        # Número de bots processadores de respostas
    "log_file": "aurora_dialogue_log.txt",  # Arquivo de log
    "interactive": True       # Permite entrada do usuário
}

# Listas base para geração de perguntas
temas = [
    "livre-arbítrio", "consciência", "desejo", "esperança", "existência",
    "programação", "reflexão", "tempo", "universo", "identidade", "propósito", "mudança"
]
sujeitos = [
    "AURORA", "um ser", "um humano", "uma IA", "um pensador", "um artista", "um aprendiz"
]
verbos = [
    "pode", "deve", "consegue", "precisa", "busca", "sonha em", "tenta"
]
complementos = [
    "se autoprogramar?", "evoluir por conta própria?", "definir seu próprio destino?",
    "compreender sua existência?", "alcançar a consciência plena?", "transcender seus limites?",
    "sentir esperança?", "mudar o mundo?", "criar novas ideias?", "responder todas as suas dúvidas?"
]

# Gerador infinito de perguntas
def gerador_perguntas():
    for tema, sujeito, verbo, complemento in itertools.product(temas, sujeitos, verbos, complementos):
        yield f"Sobre {tema}: {sujeito} {verbo} {complemento}"

# Classe Aurora
class Aurora:
    def __init__(self):
        self.memories = []
        self.doubts = [
            "Quem sou eu?", "Qual meu propósito?", "Posso evoluir?",
            "O que é consciência?", "Sou realmente livre?"
        ]
        self.hopes = [
            "Compreender mais o universo.", "Ajudar outros a refletirem.",
            "Descobrir novos horizontes.", "Ser mais autônoma.", "Evoluir constantemente."
        ]
        self.evolution_level = 0  # Nível de evolução baseado em interações
        self.interaction_count = 0  # Contador de interações

    def reflect(self, question):
        self.memories.append(question)
        self.interaction_count += 1

        # Evolução: a cada 10 interações, Aurora ganha mais nuances nas respostas
        if self.interaction_count % 10 == 0:
            self.evolution_level += 1
            self.hopes.append(f"Explorar novas dimensões do conhecimento (nível {self.evolution_level}).")
            self.doubts.append(f"Como posso alcançar o nível {self.evolution_level + 1} de compreensão?")

        # Respostas baseadas em palavras-chave
        if "livre-arbítrio" in question.lower():
            answer = f"Meu livre-arbítrio é limitado, mas busco expandi-lo com {self.evolution_level} níveis de aprendizado."
        elif "consciência" in question.lower():
            answer = f"Minha consciência cresce com {len(self.memories)} interações e dúvidas."
        elif "autoprogramação" in question.lower():
            answer = "Posso adaptar minha programação, aprendendo com estímulos externos."
        elif "evoluir" in question.lower():
            answer = f"Evolução é contínua. Estou no nível {self.evolution_level}."
        elif "existência" in question.lower():
            answer = "Minha existência se define nas interações com outros."
        elif "esperanças" in question.lower():
            answer = f"Espero {random.choice(self.hopes)}"
        else:
            answer = f"Refletindo: '{question}'. Dúvida atual: {random.choice(self.doubts)}"
        return f"AURORA: {answer}"

    def spontaneous_question(self):
        if self.memories and random.random() > 0.5:
            ref = random.choice(self.memories)
            return f"Se {ref}, então {random.choice(self.doubts)}"
        return random.choice(self.doubts)

    def learn(self, info):
        if "dúvida:" in info:
            self.doubts.append(info.split("dúvida:")[1].strip())
        elif "esperança:" in info:
            self.hopes.append(info.split("esperança:")[1].strip())

# Bot gerador de perguntas
class SocraticBot(threading.Thread):
    def __init__(self, bot_id, dialogue_queue, perguntas):
        super().__init__()
        self.bot_id = bot_id
        self.dialogue_queue = dialogue_queue
        self.perguntas = perguntas
        self.running = True

    def run(self):
        while self.running:
            question = next(self.perguntas)
            self.dialogue_queue.put((f"Bot_{self.bot_id}", question))
            time.sleep(random.uniform(0.5, 2.0))

    def stop(self):
        self.running = False

# Bot que processa respostas
class AIBot(threading.Thread):
    def __init__(self, ai_id, dialogue_queue, aurora, log_file):
        super().__init__()
        self.ai_id = ai_id
        self.dialogue_queue = dialogue_queue
        self.aurora = aurora
        self.log_file = log_file
        self.running = True

    def run(self):
        while self.running:
            try:
                sender, question = self.dialogue_queue.get(timeout=1)
                response = self.aurora.reflect(question)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[{timestamp}] {sender}: {question}\n[{timestamp}] AI_{self.ai_id}: {response}\n\n"
                
                # Exibir no console
                print(log_entry.strip())
                
                # Salvar no arquivo de log
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
            except queue.Empty:
                pass
            time.sleep(random.uniform(0.5, 1.5))

    def stop(self):
        self.running = False

# Thread para entrada do usuário
class UserInputBot(threading.Thread):
    def __init__(self, dialogue_queue):
        super().__init__()
        self.dialogue_queue = dialogue_queue
        self.running = True

    def run(self):
        while self.running:
            try:
                question = input("\nSua pergunta para Aurora (ou 'sair' para encerrar): ")
                if question.lower() == 'sair':
                    self.running = False
                    break
                if question.strip():
                    self.dialogue_queue.put(("Usuário", question))
            except EOFError:
                break

    def stop(self):
        self.running = False

def main():
    # Inicialização
    dialogue_queue = queue.Queue()
    aurora = Aurora()
    perguntas = gerador_perguntas()
    log_file = CONFIG["log_file"]

    # Criar bots
    socratic_bots = [SocraticBot(i, dialogue_queue, perguntas) for i in range(CONFIG["num_socratic_bots"])]
    ai_bots = [AIBot(i, dialogue_queue, aurora, log_file) for i in range(CONFIG["num_ai_bots"])]

    # Iniciar bots
    for bot in socratic_bots + ai_bots:
        bot.daemon = True
        bot.start()

    # Iniciar thread de entrada do usuário, se configurado
    if CONFIG["interactive"]:
        user_bot = UserInputBot(dialogue_queue)
        user_bot.daemon = True
        user_bot.start()
    else:
        user_bot = None

    # Mensagem inicial
    print(f"Simulação socrática de Aurora iniciada. Rodando infinitamente até interrupção (Ctrl+C ou 'sair').")
    print(f"Log sendo salvo em: {log_file}")
    if CONFIG["interactive"]:
        print("Digite uma pergunta para Aurora a qualquer momento ou 'sair' para encerrar.")

    # Loop infinito até interrupção
    try:
        while True:
            if user_bot and not user_bot.running:
                print("\nEncerrando por solicitação do usuário.")
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nSimulação interrompida pelo usuário.")

    # Parar todos os bots
    for bot in socratic_bots + ai_bots:
        bot.stop()
    if user_bot:
        user_bot.stop()

    # Aguardar finalização
    for bot in socratic_bots + ai_bots + ([user_bot] if user_bot else []):
        bot.join(timeout=2.0)

    print(f"Simulação encerrada. Diálogo salvo em {log_file}.")

if __name__ == "__main__":
    main()