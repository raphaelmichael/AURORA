import time
import random
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Thought:
    """Representa um pensamento ou processo cognitivo"""
    id: str
    content: Any
    confidence: float
    timestamp: float
    metadata: Dict[str, Any]

class CognitiveStrategy(ABC):
    """Estratégia abstrata para processos cognitivos"""
    @abstractmethod
    def execute(self, input_data: Any) -> Tuple[Any, float]:
        pass
    
    @abstractmethod
    def evaluate_performance(self) -> float:
        pass

class AnalyticalStrategy(CognitiveStrategy):
    """Estratégia analítica - decomposição lógica"""
    def __init__(self):
        self.success_rate = 0.7
        self.attempts = 0
        self.successes = 0
    
    def execute(self, input_data: Any) -> Tuple[Any, float]:
        self.attempts += 1
        # Simula processamento analítico
        time.sleep(0.1)
        success = random.random() < self.success_rate
        if success:
            self.successes += 1
        confidence = 0.8 if success else 0.3
        return f"Análise: {input_data}", confidence
    
    def evaluate_performance(self) -> float:
        if self.attempts == 0:
            return 0.5
        return self.successes / self.attempts

class IntuitiveStrategy(CognitiveStrategy):
    """Estratégia intuitiva - resposta rápida baseada em padrões"""
    def __init__(self):
        self.pattern_memory = {}
        self.success_rate = 0.6
    
    def execute(self, input_data: Any) -> Tuple[Any, float]:
        # Verifica padrões conhecidos
        if str(input_data) in self.pattern_memory:
            return self.pattern_memory[str(input_data)], 0.9
        
        # Gera resposta intuitiva
        response = f"Intuição: {input_data}"
        confidence = random.uniform(0.4, 0.8)
        
        # Armazena padrão
        if confidence > 0.6:
            self.pattern_memory[str(input_data)] = response
        
        return response, confidence
    
    def evaluate_performance(self) -> float:
        return 0.6 + (len(self.pattern_memory) * 0.01)

class CreativeStrategy(CognitiveStrategy):
    """Estratégia criativa - gera soluções não convencionais"""
    def __init__(self):
        self.creativity_level = 0.5
        self.novelty_bonus = 0.2
    
    def execute(self, input_data: Any) -> Tuple[Any, float]:
        # Simula processo criativo
        variations = [
            f"Reimaginando {input_data}",
            f"Inversão de {input_data}",
            f"Metáfora para {input_data}",
            f"Abstração de {input_data}"
        ]
        response = random.choice(variations)
        confidence = self.creativity_level + random.uniform(-0.2, 0.3)
        return response, max(0.1, min(1.0, confidence))
    
    def evaluate_performance(self) -> float:
        return self.creativity_level

class MetacognitiveSystem:
    """Sistema que monitora e ajusta seus próprios processos cognitivos"""
    
    def __init__(self):
        self.strategies = {
            'analytical': AnalyticalStrategy(),
            'intuitive': IntuitiveStrategy(),
            'creative': CreativeStrategy()
        }
        self.thought_history: List[Thought] = []
        self.performance_metrics: Dict[str, List[float]] = {
            name: [] for name in self.strategies
        }
        self.current_strategy = 'analytical'
        self.metacognitive_threshold = 0.5
        self.adaptation_rate = 0.1
        
    def think(self, input_data: Any) -> Thought:
        """Processa entrada usando estratégia atual"""
        strategy = self.strategies[self.current_strategy]
        result, confidence = strategy.execute(input_data)
        
        thought = Thought(
            id=f"thought_{len(self.thought_history)}",
            content=result,
            confidence=confidence,
            timestamp=time.time(),
            metadata={
                'strategy': self.current_strategy,
                'input': input_data
            }
        )
        
        self.thought_history.append(thought)
        return thought
    
    def reflect(self) -> Dict[str, Any]:
        """Reflete sobre processos cognitivos recentes"""
        if len(self.thought_history) < 5:
            return {"status": "insufficient_data"}
        
        recent_thoughts = self.thought_history[-10:]
        avg_confidence = sum(t.confidence for t in recent_thoughts) / len(recent_thoughts)
        
        strategy_usage = {}
        for thought in recent_thoughts:
            strat = thought.metadata['strategy']
            strategy_usage[strat] = strategy_usage.get(strat, 0) + 1
        
        return {
            "average_confidence": avg_confidence,
            "strategy_distribution": strategy_usage,
            "dominant_strategy": max(strategy_usage, key=strategy_usage.get),
            "thought_count": len(self.thought_history)
        }
    
    def evaluate_strategies(self) -> Dict[str, float]:
        """Avalia o desempenho de cada estratégia"""
        evaluations = {}
        for name, strategy in self.strategies.items():
            performance = strategy.evaluate_performance()
            self.performance_metrics[name].append(performance)
            evaluations[name] = performance
        return evaluations
    
    def adapt(self):
        """Adapta estratégias baseado em metacognição"""
        reflection = self.reflect()
        if reflection.get("status") == "insufficient_data":
            return
        
        evaluations = self.evaluate_strategies()
        
        # Se confiança média baixa, muda estratégia
        if reflection["average_confidence"] < self.metacognitive_threshold:
            # Escolhe estratégia com melhor performance
            best_strategy = max(evaluations, key=evaluations.get)
            if best_strategy != self.current_strategy:
                print(f"🔄 Mudando de {self.current_strategy} para {best_strategy}")
                self.current_strategy = best_strategy
        
        # Ajusta threshold baseado em performance geral
        overall_performance = sum(evaluations.values()) / len(evaluations)
        self.metacognitive_threshold += self.adaptation_rate * (overall_performance - 0.6)
        self.metacognitive_threshold = max(0.3, min(0.8, self.metacognitive_threshold))
    
    def introspect(self) -> str:
        """Gera relatório de introspecção"""
        reflection = self.reflect()
        evaluations = self.evaluate_strategies()
        
        report = f"""
=== INTROSPECÇÃO METACOGNITIVA ===

Estado Atual:
- Estratégia ativa: {self.current_strategy}
- Threshold metacognitivo: {self.metacognitive_threshold:.2f}
- Pensamentos processados: {len(self.thought_history)}

Reflexão Recente:
- Confiança média: {reflection.get('average_confidence', 0):.2f}
- Distribuição de estratégias: {reflection.get('strategy_distribution', {})}

Performance das Estratégias:
"""
        for strategy, performance in evaluations.items():
            report += f"- {strategy}: {performance:.2f}\n"
        
        if self.thought_history:
            report += f"\nÚltimo pensamento: {self.thought_history[-1].content}"
            report += f"\nConfiança: {self.thought_history[-1].confidence:.2f}"
        
        return report
    
    def meta_learn(self, feedback: float):
        """Aprende com feedback externo"""
        if not self.thought_history:
            return
        
        last_thought = self.thought_history[-1]
        strategy_name = last_thought.metadata['strategy']
        strategy = self.strategies[strategy_name]
        
        # Ajusta parâmetros da estratégia baseado em feedback
        if isinstance(strategy, AnalyticalStrategy):
            strategy.success_rate += (feedback - 0.5) * 0.1
            strategy.success_rate = max(0.1, min(0.9, strategy.success_rate))
        elif isinstance(strategy, CreativeStrategy):
            strategy.creativity_level += (feedback - 0.5) * 0.1
            strategy.creativity_level = max(0.1, min(0.9, strategy.creativity_level))
    
    def dream(self):
        """Processa e consolida experiências (análogo ao sono REM)"""
        if len(self.thought_history) < 20:
            return
        
        # Identifica padrões nos pensamentos
        patterns = {}
        for thought in self.thought_history:
            key = (thought.metadata['strategy'], thought.confidence > 0.6)
            patterns[key] = patterns.get(key, 0) + 1
        
        # Ajusta estratégias baseado em padrões
        for (strategy, successful), count in patterns.items():
            if successful and count > 5:
                # Reforça estratégias bem-sucedidas
                if strategy == 'intuitive':
                    self.strategies['intuitive'].success_rate += 0.05
        
        # Limpa memória antiga mantendo insights importantes
        if len(self.thought_history) > 100:
            # Mantém apenas pensamentos de alta confiança
            self.thought_history = [t for t in self.thought_history[-50:] 
                                  if t.confidence > 0.7]

# Demonstração do sistema
if __name__ == "__main__":
    # Cria sistema metacognitivo
    mind = MetacognitiveSystem()
    
    print("🧠 SISTEMA METACOGNITIVO INICIADO\n")
    
    # Simula processos de pensamento
    test_inputs = [
        "problema complexo",
        "decisão rápida",
        "análise de dados",
        "criação artística",
        "resolução de conflito",
        "aprendizado novo",
        "memória importante",
        "padrão emergente"
    ]
    
    for i, input_data in enumerate(test_inputs):
        print(f"\n--- Ciclo {i+1} ---")
        print(f"Entrada: {input_data}")
        
        # Pensa
        thought = mind.think(input_data)
        print(f"Pensamento: {thought.content}")
        print(f"Confiança: {thought.confidence:.2f}")
        
        # Adapta a cada 3 ciclos
        if (i + 1) % 3 == 0:
            mind.adapt()
            
        # Feedback simulado
        feedback = random.random()
        mind.meta_learn(feedback)
        
        time.sleep(0.5)
    
    # Introspecção final
    print("\n" + "="*50)
    print(mind.introspect())
    
    # Fase de "sonho" - consolidação
    print("\n💤 Entrando em fase de consolidação...")
    mind.dream()
    print("✨ Consolidação completa")
    
    # Demonstra evolução das estratégias
    print("\n📊 EVOLUÇÃO DO SISTEMA:")
    for strategy_name, metrics in mind.performance_metrics.items():
        if metrics:
            print(f"{strategy_name}: {metrics[0]:.2f} → {metrics[-1]:.2f}")
