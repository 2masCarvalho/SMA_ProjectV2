import math
import random
import threading
from typing import Tuple, List
from Ambiente import Ambiente
from Modelos import Observacao, Accao

class AmbienteFarol(Ambiente):
    def __init__(self, farol_pos: Tuple[int, int], dimensoes: Tuple[int, int], obstaculos: List[Tuple[int, int]] = None):
        super().__init__()
        self.farol_pos = farol_pos
        self.dimensoes = dimensoes
        self.largura, self.altura = dimensoes
        self.obstaculos = obstaculos if obstaculos else []
        
        self.agentes_posicoes = {}   
        self.posicoes_iniciais = {}  
        
        self._alvo_atingido = False 

    def adicionar_agente(self, agente, pos_inicial: Tuple[int, int]):
        self.agentes_posicoes[agente] = pos_inicial
        self.posicoes_iniciais[agente] = pos_inicial 

    def reset(self):
        self._alvo_atingido = False
        for agente, pos_init in self.posicoes_iniciais.items():
            self.agentes_posicoes[agente] = pos_init
            
            if hasattr(agente, "reset_estado"):
                agente.reset_estado()
    def observacaoPara(self, agente) -> Observacao:
        if agente not in self.agentes_posicoes:
            return Observacao({})
        
        pos_agente = self.agentes_posicoes[agente]
        dx = self.farol_pos[0] - pos_agente[0]
        dy = self.farol_pos[1] - pos_agente[1]
        
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist == 0:
            direcao = (0, 0) 
        else:
            direcao = (dx / dist, dy / dist) 
            
        return Observacao({"direcao": direcao, "posicao": pos_agente, "distancia": dist})

    def atualizacao(self):
        pass
    
    def simulacao_concluida(self) -> bool:
        return self._alvo_atingido

    def _agir_safe(self, accao: Accao, agente) -> float:
        if accao.tipo != "mover":
            return 0.0
        
        input_direcao = accao.parametros.get("direcao")
        
        if not input_direcao:
            return 0.0
            
        vetores_direcao = {
            "norte": (0, -1),
            "sul":   (0, 1),
            "este":  (1, 0),
            "oeste": (-1, 0),
            "nordeste": (1, -1),
            "sudeste":  (1, 1),
            "sudoeste": (-1, 1),
            "noroeste": (-1, -1)
        }

        direcao = (0, 0)

        if isinstance(input_direcao, str):
            direcao = vetores_direcao.get(input_direcao.lower(), (0,0))
        
        elif isinstance(input_direcao, (tuple, list)) and len(input_direcao) == 2:
            direcao = input_direcao
        else:
            return 0.0

        pos_atual = self.agentes_posicoes[agente]

        step_size = 1
        novo_x = pos_atual[0] + direcao[0] * step_size
        novo_y = pos_atual[1] + direcao[1] * step_size
        
        x_int, y_int = int(round(novo_x)), int(round(novo_y))
        
        if not (0 <= x_int < self.largura and 0 <= y_int < self.altura):
            return -100.0 
            
        if (x_int, y_int) in self.obstaculos:
            return -50.0 

        self.agentes_posicoes[agente] = (novo_x, novo_y)
        
        dist_antiga = math.sqrt((self.farol_pos[0] - pos_atual[0])**2 + (self.farol_pos[1] - pos_atual[1])**2)
        dist_nova = math.sqrt((self.farol_pos[0] - novo_x)**2 + (self.farol_pos[1] - novo_y)**2)
        
        recompensa = (dist_antiga - dist_nova) * 10 
        
        if dist_nova < 1.0:
            recompensa += 100 
            self._alvo_atingido = True
            
        agente.avaliacao_estado_atual(recompensa)
        return recompensa
        
    def display(self):
        grid = [['.' for _ in range(self.largura)] for _ in range(self.altura)]
        
        for ox, oy in self.obstaculos:
            if 0 <= ox < self.largura and 0 <= oy < self.altura:
                grid[oy][ox] = 'O'
                
        fx, fy = self.farol_pos
        if 0 <= fx < self.largura and 0 <= fy < self.altura:
            grid[fy][fx] = 'F'
            
        for agente, pos in self.agentes_posicoes.items():
            ax, ay = int(round(pos[0])), int(round(pos[1]))
            if 0 <= ax < self.largura and 0 <= ay < self.altura:
                grid[ay][ax] = agente.nome[0].upper() 
                
        print("+" + "-" * self.largura + "+")
        for y in range(self.altura):
            print("|" + "".join(grid[y]) + "|")
        print("+" + "-" * self.largura + "+")