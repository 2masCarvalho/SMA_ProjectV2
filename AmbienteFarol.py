import math
import random
import threading
from typing import Tuple, List
from Ambiente import Ambiente
from Modelos import Observacao, Accao


class AmbienteFarol(Ambiente):
    """Ambiente 2D com um farol e obstáculos opcionais."""
    def __init__(self, farol_pos: Tuple[int, int], dimensoes: Tuple[int, int], obstaculos: List[Tuple[int, int]] = None):
        super().__init__()
        self.farol_pos = farol_pos
        self.dimensoes = dimensoes
        self.largura, self.altura = dimensoes
        self.obstaculos = obstaculos if obstaculos else []
        self.agentes_posicoes = {} # Dicionário para guardar posições dos agentes {agente: (x, y)}

        self._alvo_atingido = False # Variável interna de controlo

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
    
    def simulacao_concluida(self) -> bool:
        # Implementação específica do Farol
        return self._alvo_atingido

    def _agir_safe(self, accao: Accao, agente) -> float:
        """
        Move o agente na direção indicada.
        """
        if accao.tipo != "mover":
            return 0.0
        
        # 1. Obter o valor que vem do agente
        input_direcao = accao.parametros.get("direcao")
        
        if not input_direcao:
            return 0.0
            
        # 2. TRADUÇÃO: Converter texto para vetor (dx, dy)
        vetores_direcao = {
            # Cardinais
            "norte": (0, -1),
            "sul":   (0, 1),
            "este":  (1, 0),
            "oeste": (-1, 0),
            # Diagonais
            "nordeste": (1, -1),
            "sudeste":  (1, 1),
            "sudoeste": (-1, 1),
            "noroeste": (-1, -1)
        }

        direcao = (0, 0)

        # Se for string (ex: "norte"), traduzimos
        if isinstance(input_direcao, str):
            direcao = vetores_direcao.get(input_direcao.lower(), (0,0))
        
        # Se já for uma tupla/lista (ex: (0, 1)), usamos direto
        elif isinstance(input_direcao, (tuple, list)) and len(input_direcao) == 2:
            direcao = input_direcao
        else:
            return 0.0

        pos_atual = self.agentes_posicoes[agente]

        # 3. Calcular nova posição
        step_size = 1
        novo_x = pos_atual[0] + direcao[0] * step_size
        novo_y = pos_atual[1] + direcao[1] * step_size
        
        # Verificar limites
        x_int, y_int = int(round(novo_x)), int(round(novo_y))
        
        if not (0 <= x_int < self.largura and 0 <= y_int < self.altura):
            return -100.0 # Bateu na parede do mundo
            
        if (x_int, y_int) in self.obstaculos:
            return -50.0 # Bateu num obstáculo

        # Atualizar posição
        self.agentes_posicoes[agente] = (novo_x, novo_y)
        
        # Calcular recompensa (Shaping Reward: incentiva a aproximar-se)
        dist_antiga = math.sqrt((self.farol_pos[0] - pos_atual[0])**2 + (self.farol_pos[1] - pos_atual[1])**2)
        dist_nova = math.sqrt((self.farol_pos[0] - novo_x)**2 + (self.farol_pos[1] - novo_y)**2)
        
        recompensa = (dist_antiga - dist_nova) * 10 
        
        # --- VERIFICAÇÃO DE VITÓRIA ---
        if dist_nova < 1.0:
            recompensa += 100 
            print(f"!!! Agente {agente.nome} chegou ao Farol !!!")
            
            # ATUALIZAÇÃO IMPORTANTE: Avisar o ambiente que acabou
            # (Certifica-te que definiste self._alvo_atingido = False no __init__)
            self._alvo_atingido = True
            
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
