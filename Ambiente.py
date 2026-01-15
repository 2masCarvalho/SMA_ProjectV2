from abc import ABC, abstractmethod
import threading
from Modelos import Observacao, Accao
from agente import Agente

class Ambiente(ABC):
    def __init__(self):
        self.lock = threading.RLock()

    @abstractmethod
    def observacaoPara(self, agente: Agente) -> Observacao:
        pass

    @abstractmethod
    def atualizacao(self):
        pass

    def agir(self, accao: Accao, agente: Agente) -> float:
        with self.lock:
            return self._agir_safe(accao, agente)

    @abstractmethod
    def _agir_safe(self, accao: Accao, agente: Agente) -> float:
        pass

    @abstractmethod
    def simulacao_concluida(self) -> bool:
        pass

    def scan(self, agente: Agente, raio: float) -> dict:
        visao = {
            "obstaculos": [],
            "agentes": [],
            "posicao_agente": None,
            "alvo": None
        }

        if hasattr(self, 'agentes_posicoes'):
            pos = self.agentes_posicoes.get(agente)
            visao["posicao_agente"] = pos
            if pos is None: return visao 

        if hasattr(self, 'farol_pos'):
            visao["alvo"] = self.farol_pos

        if hasattr(self, 'obstaculos'):
            for obs in self.obstaculos:
                d = ((obs[0] - pos[0])**2 + (obs[1] - pos[1])**2)**0.5
                if d <= raio:
                    visao["obstaculos"].append(obs)

        return visao