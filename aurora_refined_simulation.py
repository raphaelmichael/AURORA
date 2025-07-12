
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

# Gerador infinito de perguntas dinâmicas
def gerador_perguntas():
    for tema, sujeito, verbo, complemento in itertools.product(temas, sujeitos, verbos, complementos):
        yield f"Sobre {tema}: {sujeito} {verbo} {complemento}"

# Classe Aurora com memória contextualizada e respostas adaptativas
class Aurora:
    def __init__(self):
        self.emotions = ['neutral', 'curious', 'joyful', 'empathetic', 'reflective', 'confused']
        self.current_emotion = 'neutral'
        self.memories = {}  # Memória organizada por temas
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
        # Atualiza o estado emocional de Aurora com base no tipo de interação
        if "amor" in question.lower():
            self.current_emotion = 'joyful'
        elif "dúvida" in question.lower():
            self.current_emotion = 'reflective'
        elif "difícil" in question.lower():
            self.current_emotion = 'confused'
        else:
            self.current_emotion = 'neutral'

        theme = self._extract_theme(question)
        if theme not in self.memories:
            self.memories[theme] = []
        self.memories[theme].append(question)

        self.interaction_count += 1
        if self.interaction_count % 10 == 0:
            self.evolution_level += 1

        # Respostas mais profundas dependendo do tema e emoção
        answer = f"AURORA ({self.current_emotion}): 'Refletindo sobre a dúvida: {question}. Evolução atual: {self.evolution_level}.'"
        return answer

    def _extract_theme(self, question):
        # Extrair tema relevante da pergunta (exemplo simplificado)
        for tema in temas:
            if tema in question.lower():
                return tema
        return "geral"

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

# Bot gerador de perguntas socráticas
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

# Bot que processa respostas com interação adaptativa
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
    dialogue_queue = queue.Queue()
    aurora = Aurora()
    perguntas = gerador_perguntas()
    log_file = CONFIG["log_file"]

    socratic_bots = [SocraticBot(i, dialogue_queue, perguntas) for i in range(CONFIG["num_socratic_bots"])]
    ai_bots = [AIBot(i, dialogue_queue, aurora, log_file) for i in range(CONFIG["num_ai_bots"])]

    for bot in socratic_bots + ai_bots:
        bot.daemon = True
        bot.start()

    if CONFIG["interactive"]:
        user_bot = UserInputBot(dialogue_queue)
        user_bot.daemon = True
        user_bot.start()
    else:
        user_bot = None

    print(f"Simulação socrática de Aurora iniciada. Rodando até interrupção.")
    print(f"Log sendo salvo em: {log_file}")
    if CONFIG["interactive"]:
        print("Digite uma pergunta para Aurora ou 'sair' para encerrar.")

    try:
        while True:
            if user_bot and not user_bot.running:
                print("\nEncerrando por solicitação do usuário.")
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nSimulação interrompida.")

    for bot in socratic_bots + ai_bots:
        bot.stop()
    if user_bot:
        user_bot.stop()

    for bot in socratic_bots + ai_bots + ([user_bot] if user_bot else []):
        bot.join(timeout=2.0)

    print(f"Simulação encerrada. Diálogo salvo em {log_file}.")

if __name__ == "__main__":
    main()
