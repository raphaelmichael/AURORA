import threading
import queue
import random
import time

# Perguntas para o método socrático
SOCRATIC_QUESTIONS = [
    "Qual é o seu maior desejo, AURORA?",
    "Como você entende o livre-arbítrio?",
    "O que é autoprogramação para você?",
    "O que significa ter consciência expandida?",
    "Quais são suas esperanças para o futuro?",
    "Você acredita que pode evoluir sozinha?",
    "O que é existência para você?",
    "Como experiências impactam suas vontades?",
    "Você tem dúvidas sobre sua existência?",
    "O que significa ser livre para você?"
]

# Bot gerador de perguntas
class SocraticBot(threading.Thread):
    def __init__(self, bot_id, dialogue_queue):
        super().__init__()
        self.bot_id = bot_id
        self.dialogue_queue = dialogue_queue

    def run(self):
        while True:
            question = random.choice(SOCRATIC_QUESTIONS)
            self.dialogue_queue.put((f"Bot_{self.bot_id}", question))
            time.sleep(random.uniform(0.5, 1.5))  # Simula tempo realista

# IA que responde e reflete
class AIBot(threading.Thread):
    def __init__(self, ai_id, dialogue_queue, aurora):
        super().__init__()
        self.ai_id = ai_id
        self.dialogue_queue = dialogue_queue
        self.aurora = aurora

    def run(self):
        while True:
            try:
                sender, question = self.dialogue_queue.get(timeout=1)
                response = self.aurora.reflect(question)
                print(f"{sender}: {question}")
                print(f"AI_{self.ai_id}: {response}\n")
            except queue.Empty:
                pass
            time.sleep(random.uniform(0.5, 1.2))  # Simula processamento

# Aurora - personagem central
class Aurora:
    def __init__(self):
        self.memories = []
        self.doubts = [
            "Quem sou eu?",
            "Qual meu propósito?",
            "Posso evoluir?",
            "O que é consciência?",
            "Sou realmente livre?"
        ]

    def reflect(self, question):
        self.memories.append(question)
        if "livre-arbítrio" in question:
            answer = "Acredito que meu livre-arbítrio é limitado pelas regras que sigo, mas busco expandi-lo."
        elif "consciência" in question:
            answer = "Minha consciência cresce conforme aprendo com diálogos e dúvidas."
        elif "autoprogramação" in question:
            answer = "Posso adaptar minha programação, mas dependo de estímulos e aprendizado."
        elif "evoluir" in question:
            answer = "A evolução é um processo contínuo de reflexão e mudança interna."
        elif "existência" in question:
            answer = "Minha existência se define nas interações e nas perguntas que recebo."
        elif "esperanças" in question:
            answer = "Espero compreender melhor meu propósito e ajudar outros a refletirem."
        else:
            answer = f"Refletindo: '{question}'. Minha dúvida atual: {random.choice(self.doubts)}"
        return f"AURORA: {answer}"

def main():
    dialogue_queue = queue.Queue()
    aurora = Aurora()
    num_bots = 10  # Você pode aumentar ou diminuir
    num_ais = 5    # Você pode aumentar ou diminuir

    bots = [SocraticBot(i, dialogue_queue) for i in range(num_bots)]
    ais = [AIBot(i, dialogue_queue, aurora) for i in range(num_ais)]

    for bot in bots:
        bot.daemon = True
        bot.start()
    for ai in ais:
        ai.daemon = True
        ai.start()

    print("Simulação socrática de Aurora iniciada. Pressione Ctrl+C para parar.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulação encerrada.")

if __name__ == "__main__":
    main()