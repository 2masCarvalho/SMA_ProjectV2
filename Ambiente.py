from abc import ABC, abstractmethod
import threading
from Modelos import Observacao, Accao
# Forward reference for Agente to avoid circular import if possible, or just import if no cycle.
# Since Agente imports Modelos, and Ambiente imports Modelos, that's fine.
# But Ambiente uses Agente in type hints.
# For now, let's use string forward references or TYPE_CHECKING, but simple import might work if Agente doesn't import Ambiente.
# Agente.py does NOT import Ambiente.
from agente import Agente

class Ambiente(ABC):
    """Interface base para todos os ambientes de simulação."""
    def __init__(self):
        self.lock = threading.RLock()

    @abstractmethod
    def observacaoPara(self, agente: Agente) -> Observacao:
        """Gera a observação específica para um agente."""
        pass


    @abstractmethod
    def atualizacao(self):
        """Atualiza o estado do ambiente (e.g., movimento de recursos, tempo)."""
        pass

    def agir(self, accao: Accao, agente: Agente) -> float:
        """Processa a ação do agente e retorna a recompensa."""
        with self.lock:
            return self._agir_safe(accao, agente)
from abc import ABC, abstractmethod
import threading
from Modelos import Observacao, Accao
# Forward reference for Agente to avoid circular import if possible, or just import if no cycle.
# Since Agente imports Modelos, and Ambiente imports Modelos, that's fine.
# But Ambiente uses Agente in type hints.
# For now, let's use string forward references or TYPE_CHECKING, but simple import might work if Agente doesn't import Ambiente.
# Agente.py does NOT import Ambiente.
from agente import Agente

class Ambiente(ABC):
    """Interface base para todos os ambientes de simulação."""
    def __init__(self):
        self.lock = threading.RLock()

    @abstractmethod
    def observacaoPara(self, agente: Agente) -> Observacao:
        """Gera a observação específica para um agente."""
        pass


    @abstractmethod
    def atualizacao(self):
        """Atualiza o estado do ambiente (e.g., movimento de recursos, tempo)."""
        pass

    def agir(self, accao: Accao, agente: Agente) -> float:
        """Processa a ação do agente e retorna a recompensa."""
        with self.lock:
            return self._agir_safe(accao, agente)

    @abstractmethod
    def _agir_safe(self, accao: Accao, agente: Agente) -> float:
        """Implementação da ação (chamada dentro do lock)."""
        pass

    @abstractmethod
    def simulacao_concluida(self) -> bool:
        """
        Retorna True se o objetivo do ambiente foi atingido.
        O Motor usa isto para saber quando parar.
        """
        pass

    def scan(self, agente: Agente, raio: float) -> dict:
        """
        Retorna o que é visível para o agente dentro de um raio.
        Subclasses devem implementar a lógica específica se necessário,
        mas aqui fornecemos uma implementação base genérica.
        """
        # Implementação base que assume que as subclasses têm 'agentes_posicoes' e 'obstaculos'
        # Se a arquitetura mudar, só mudamos aqui!
        
        visao = {
            "obstaculos": [],
            "agentes": [],
            "posicao_agente": None,
            "alvo": None
        }

        # 1. Onde estou?
        if hasattr(self, 'agentes_posicoes'):
            pos = self.agentes_posicoes.get(agente)
            visao["posicao_agente"] = pos
            if pos is None: return visao # Agente não está no mundo

        # 2. Onde está o alvo? (Farol ou Saída)
        if hasattr(self, 'farol_pos'):
            visao["alvo"] = self.farol_pos

        # 3. O que está à volta?
        # Nota: Para performance, num mundo gigante, usaríamos uma QuadTree.
        # Aqui, iterar tudo é aceitável para grelhas pequenas.
        
        # Obstáculos
        if hasattr(self, 'obstaculos'):
            for obs in self.obstaculos:
                # Distância Euclidiana
                d = ((obs[0] - pos[0])**2 + (obs[1] - pos[1])**2)**0.5
                if d <= raio:
                    visao["obstaculos"].append(obs)

        return visao