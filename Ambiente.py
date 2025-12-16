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