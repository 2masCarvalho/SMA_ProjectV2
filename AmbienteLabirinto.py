import math
from typing import Tuple, List
from Ambiente import Ambiente
from Modelos import Observacao, Accao

class AmbienteLabirinto(Ambiente):
    """Ambiente de Labirinto onde o objetivo é chegar à Saída."""
    
    def __init__(self, pos_saida: Tuple[int, int], dimensoes: Tuple[int, int], obstaculos: List[Tuple[int, int]] = None):
        super().__init__()
        # Mapeamos a saída para 'farol_pos' para que os sensores existentes funcionem sem alterações
        self.farol_pos = pos_saida 
        self.pos_saida = pos_saida
        self.dimensoes = dimensoes
        self.largura, self.altura = dimensoes
        self.obstaculos = obstaculos if obstaculos else []
        self.agentes_posicoes = {}
        self._alvo_atingido = False

    def simulacao_concluida(self) -> bool:
        return self._alvo_atingido

    def adicionar_agente(self, agente, pos_inicial: Tuple[int, int]):
        self.agentes_posicoes[agente] = pos_inicial

    def observacaoPara(self, agente) -> Observacao:
        # Lógica idêntica ao Farol: vetor para o objetivo
        if agente not in self.agentes_posicoes:
            return Observacao({})
        
        pos_agente = self.agentes_posicoes[agente]
        dx = self.pos_saida[0] - pos_agente[0]
        dy = self.pos_saida[1] - pos_agente[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        direcao = (dx/dist, dy/dist) if dist > 0 else (0,0)
        return Observacao({"direcao": direcao, "posicao": pos_agente, "distancia": dist})

    def atualizacao(self):
        pass

    def _agir_safe(self, accao: Accao, agente) -> float:
        if accao.tipo != "mover": return 0.0
        
        # 1. Traduzir Direção
        input_direcao = accao.parametros.get("direcao")
        if not input_direcao: return 0.0
        
        vetores = {
            "norte": (0, -1), "sul": (0, 1), "este": (1, 0), "oeste": (-1, 0),
            "nordeste": (1, -1), "sudeste": (1, 1), "sudoeste": (-1, 1), "noroeste": (-1, -1)
        }
        
        direcao = (0,0)
        if isinstance(input_direcao, str):
            direcao = vetores.get(input_direcao.lower(), (0,0))
        elif isinstance(input_direcao, (tuple, list)):
            direcao = input_direcao

        pos_atual = self.agentes_posicoes[agente]
        
        # 2. Calcular Nova Posição
        nx = pos_atual[0] + direcao[0]
        ny = pos_atual[1] + direcao[1]
        
        xi, yi = int(round(nx)), int(round(ny))
        pos_futura = (xi, yi)

        # 3. Verificações
        # Bateu nas paredes do mundo?
        if not (0 <= xi < self.largura and 0 <= yi < self.altura):
            return -100.0
            
        # Bateu num obstáculo? (A saída nunca é obstáculo)
        if pos_futura in self.obstaculos and pos_futura != self.pos_saida:
            return -50.0

        # Atualizar
        self.agentes_posicoes[agente] = (nx, ny)
        
        # 4. Recompensas
        dist_antiga = math.sqrt((self.pos_saida[0]-pos_atual[0])**2 + (self.pos_saida[1]-pos_atual[1])**2)
        dist_nova = math.sqrt((self.pos_saida[0]-nx)**2 + (self.pos_saida[1]-ny)**2)
        
        recompensa = (dist_antiga - dist_nova) * 10
        
        # Chegou à saída
        if dist_nova < 1.0:
            recompensa += 500 
            print(f"!!! {agente.nome} ESCAPOU DO LABIRINTO !!!")
            self._alvo_atingido = True
            
        agente.avaliacao_estado_atual(recompensa)
        return recompensa

    def display(self):
        # Opcional: para debug visual no terminal
        pass