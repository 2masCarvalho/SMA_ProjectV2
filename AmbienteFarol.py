import math
import random
import threading
from typing import Tuple, List
from Ambiente import Ambiente
from Modelos import Observacao, Accao
from agente import AgenteDirecional

class AmbienteFarol(Ambiente):
    """Ambiente 2D com um farol e obstáculos opcionais."""
    def __init__(self, farol_pos: Tuple[int, int], dimensoes: Tuple[int, int], obstaculos: List[Tuple[int, int]] = None):
        super().__init__()
        self.farol_pos = farol_pos
        self.largura, self.altura = dimensoes
        self.obstaculos = obstaculos if obstaculos else []
        self.agentes_posicoes = {} # Dicionário para guardar posições dos agentes {agente: (x, y)}

    def adicionar_agente(self, agente, pos_inicial: Tuple[int, int]):
        self.agentes_posicoes[agente] = pos_inicial

    def observacaoPara(self, agente) -> Observacao:
        """
        Calcula a direção (vetor unitário) para o farol.
        """
        if agente not in self.agentes_posicoes:
            print("Agente não encontrado no ambiente para observação.")
            return Observacao({})
        
        pos_agente = self.agentes_posicoes[agente]
        dx = self.farol_pos[0] - pos_agente[0]
        dy = self.farol_pos[1] - pos_agente[1]
        
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist == 0:
            direcao = (0, 0) # Já está no farol
        else:
            direcao = (dx / dist, dy / dist) # Vetor normalizado
            
        return Observacao({"direcao": direcao, "posicao": pos_agente, "distancia": dist})

    def atualizacao(self):
        """Pode ser usado para mover obstáculos ou alterar o ambiente."""
        pass

    def _agir_safe(self, accao: Accao, agente) -> float:
        """
        Move o agente na direção indicada.
        """
        if accao.tipo != "mover":
            return 0.0
        
        direcao = accao.parametros.get("direcao")
        if not direcao:
            return 0.0
            
        pos_atual = self.agentes_posicoes[agente]

        
        # Movimento simples: arredondar a direção para mover na grelha (ou movimento contínuo)
        # Aqui assumimos movimento discreto na grelha para simplificar, ou passos pequenos
        step_size = 1
        novo_x = pos_atual[0] + direcao[0] * step_size
        novo_y = pos_atual[1] + direcao[1] * step_size
        
        # Verificar limites e obstáculos
        # (Simplificação: arredondar para verificar colisão em grelha inteira)
        x_int, y_int = int(round(novo_x)), int(round(novo_y))
        
        if not (0 <= x_int < self.largura and 0 <= y_int < self.altura):
            return -100.0 # Bateu na parede do mundo
            
        if (x_int, y_int) in self.obstaculos:
            return -50.0 # Bateu num obstáculo

            
        # Atualizar posição
        self.agentes_posicoes[agente] = (novo_x, novo_y)
        
        # Calcular recompensa
        dist_antiga = math.sqrt((self.farol_pos[0] - pos_atual[0])**2 + (self.farol_pos[1] - pos_atual[1])**2)
        dist_nova = math.sqrt((self.farol_pos[0] - novo_x)**2 + (self.farol_pos[1] - novo_y)**2)
        
        recompensa = (dist_antiga - dist_nova) * 10 # Recompensa por se aproximar
        
        if dist_nova < 1.0:
            recompensa += 100 # Chegou ao farol
            print(f"!!! Agente {agente.nome} chegou ao Farol !!!")
            
        agente.avaliacao_estado_atual(recompensa)
        return recompensa

    def display(self):
        """Imprime o estado atual do ambiente no terminal."""
        # Criar grelha vazia
        grid = [['.' for _ in range(self.largura)] for _ in range(self.altura)]
        
        # Colocar Obstáculos
        for ox, oy in self.obstaculos:
            if 0 <= ox < self.largura and 0 <= oy < self.altura:
                grid[oy][ox] = 'O'
                
        # Colocar Farol
        fx, fy = self.farol_pos
        if 0 <= fx < self.largura and 0 <= fy < self.altura:
            grid[fy][fx] = 'F'
            
        # Colocar Agentes
        for agente, pos in self.agentes_posicoes.items():
            ax, ay = int(round(pos[0])), int(round(pos[1]))
            if 0 <= ax < self.largura and 0 <= ay < self.altura:
                # Se houver colisão visual, mostra o último
                grid[ay][ax] = agente.nome[0].upper() 
                
        # Imprimir
        print("+" + "-" * self.largura + "+")
        for y in range(self.altura):
            print("|" + "".join(grid[y]) + "|")
        print("+" + "-" * self.largura + "+")
