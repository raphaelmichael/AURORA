import random
import itertools

# Listas base para combinações
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
    "se autoprogramar?",
    "evoluir por conta própria?",
    "definir seu próprio destino?",
    "compreender sua existência?",
    "alcançar a consciência plena?",
    "transcender seus limites?",
    "sentir esperança?",
    "mudar o mundo?",
    "criar novas ideias?",
    "responder todas as suas dúvidas?"
]

# Gerador infinito de perguntas
def gerador_perguntas():
    for tema, sujeito, verbo, complemento in itertools.product(temas, sujeitos, verbos, complementos):
        yield f"Sobre {tema}: {sujeito} {verbo} {complemento}"

# Exemplo: gerar as N primeiras perguntas
N = 100
perguntas = gerador_perguntas()
for i in range(N):
    print(next(perguntas))