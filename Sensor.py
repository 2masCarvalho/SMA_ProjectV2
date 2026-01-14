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
        # USA O NOVO MÉTODO SCAN (ENCAPSULAMENTO)
        visao = ambiente.scan(agente, self.raio_visao)
        
        pos_agente = visao["posicao_agente"]
        pos_farol = visao["alvo"]

        if pos_agente is None or pos_farol is None:
             return Observacao({"farol_visto": False})

        # 2. Calcular distância
        dx = pos_farol[0] - pos_agente[0]
        dy = pos_farol[1] - pos_agente[1]
        distancia = math.sqrt(dx**2 + dy**2)

        # 3. Verificar se está dentro do raio
        if 0 < distancia <= self.raio_visao:
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
        # USA O NOVO MÉTODO SCAN (ENCAPSULAMENTO)
        # Raio infinito para saber a direção global
        visao = ambiente.scan(agente, raio=9999)
        
        pos_agente = visao["posicao_agente"]
        pos_alvo = visao["alvo"]

        if pos_agente and pos_alvo:
            dx = pos_alvo[0] - pos_agente[0]
            dy = pos_alvo[1] - pos_agente[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                direcao = (dx / dist, dy / dist)
            else:
                direcao = (0, 0)
            return Observacao({"direcao": direcao, "distancia": dist, "posicao": pos_agente})
        
        obs = {"direcao": (0, 0), "erro": "alvo_nao_encontrado"}
        if pos_agente: obs["posicao"] = pos_agente
        return Observacao(obs)

class SensorProximidade(Sensor):
    def __init__(self, raio_visao: int = 1):
        # O raio 1 significa verificar as 8 células vizinhas
        self.raio_visao = raio_visao
        
        # As 8 direções de movimento (dx, dy)
        self.direcoes_vizinhanca = [
            (0, 1), (0, -1), (1, 0), (-1, 0), # Cardinais
            (1, 1), (1, -1), (-1, 1), (-1, -1) # Diagonais
        ]

    def detetar(self, ambiente, agente) -> Observacao:
        # USA O NOVO MÉTODO SCAN
        visao = ambiente.scan(agente, raio=self.raio_visao)
        pos_agente = visao["posicao_agente"]
        
        if pos_agente is None:
            return Observacao({"erro": "agente_nao_posicionado"})
        
        # Lista de obstáculos visíveis
        obstaculos_visiveis = visao["obstaculos"]
        
        deteccao_obstaculos = {}
        ax, ay = pos_agente
        
        for dx, dy in self.direcoes_vizinhanca:
            px = ax + dx
            py = ay + dy
            pos_vizinha = (px, py)
            
            # Verifica se esta posição vizinha está na lista de obstáculos vistos
            is_obstaculo = pos_vizinha in obstaculos_visiveis
            
            # --- FIX: Verifica limites do mundo (se o ambiente tiver dimensões definidas) ---
            if hasattr(ambiente, 'largura') and hasattr(ambiente, 'altura'):
                if not (0 <= px < ambiente.largura and 0 <= py < ambiente.altura):
                    is_obstaculo = True
            
            deteccao_obstaculos[f"obs_{dx}_{dy}"] = is_obstaculo
            
        deteccao_obstaculos["posicao"] = pos_agente
        return Observacao({"proximidade_obstaculos": deteccao_obstaculos})