from abc import ABC, abstractmethod
import math
from Modelos import Observacao

class Sensor(ABC):
    """Interface base para todos os sensores."""
    
    @abstractmethod
    def detetar(self, ambiente, agente) -> Observacao:
        """
        Recolhe informação do ambiente relativa ao agente e retorna uma Observacao.
        """
        pass

class SensorVisao(Sensor):
    def __init__(self, raio_visao: float = 1.5): # 1.5 cobre as diagonais (raiz de 2 = 1.41)
        self.raio_visao = raio_visao

    def detetar(self, ambiente, agente) -> Observacao:
        # 1. Obter posições
        if not hasattr(ambiente, 'farol_pos') or agente not in ambiente.agentes_posicoes:
            # Tentar ainda devolver a posição se for possível
            pos_agente = ambiente.agentes_posicoes.get(agente) if hasattr(ambiente, 'agentes_posicoes') else None
            if pos_agente is not None:
                return Observacao({"farol_visto": False, "posicao": pos_agente})
            return Observacao({"farol_visto": False})

        pos_agente = ambiente.agentes_posicoes[agente]
        pos_farol = ambiente.farol_pos

        # 2. Calcular distância
        dx = pos_farol[0] - pos_agente[0]
        dy = pos_farol[1] - pos_agente[1]
        distancia = math.sqrt(dx**2 + dy**2)

        # 3. Verificar se está nas 8 quadrículas vizinhas
        # A distância para um vizinho lateral é 1.0, diagonal é ~1.41
        if 0 < distancia <= self.raio_visao:
            # Normalizar o vetor para saber a direção exata
            direcao = (dx / distancia, dy / distancia)
            return Observacao({
                "farol_visto": True,
                "direcao_visual": direcao,
                "distancia": distancia,
                "posicao": pos_agente
            })
        
        return Observacao({"farol_visto": False, "posicao": pos_agente})

class SensorDirecao(Sensor):
    """Sensor que deteta a direção para um alvo (ex: Farol)."""
    def detetar(self, ambiente, agente) -> Observacao:
        # Tenta obter a posição do alvo e do agente
        # Esta lógica assume que o ambiente tem 'farol_pos' e 'agentes_posicoes'
         
        if hasattr(ambiente, 'farol_pos') and hasattr(ambiente, 'agentes_posicoes'):
            pos_agente = ambiente.agentes_posicoes.get(agente)
            if pos_agente:
                dx = ambiente.farol_pos[0] - pos_agente[0]
                dy = ambiente.farol_pos[1] - pos_agente[1]
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0:
                    direcao = (dx / dist, dy / dist)
                else:
                    direcao = (0, 0)
                return Observacao({"direcao": direcao, "distancia": dist, "posicao": pos_agente})
        
        # Se não conhecemos a posição do agente, devolvemos um dicionário com erro.
        pos_agente = None
        if hasattr(ambiente, 'agentes_posicoes'):
            pos_agente = ambiente.agentes_posicoes.get(agente)
        obs = {"direcao": (0, 0), "erro": "alvo_nao_encontrado"}
        if pos_agente is not None:
            obs["posicao"] = pos_agente
        return Observacao(obs)