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
        self.visitas = {} # Para cada agente, um conjunto de posições visitadas

    def simulacao_concluida(self) -> bool:
        return self._alvo_atingido

    def adicionar_agente(self, agente, pos_inicial: Tuple[int, int]):
        self.agentes_posicoes[agente] = pos_inicial
        self.visitas[agente] = set()
        self.visitas[agente].add(pos_inicial)

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
        # Ação inválida
        if accao.tipo != "mover":
            return -2.0

        # 1. Traduzir direção
        input_direcao = accao.parametros.get("direcao")
        if not input_direcao:
                return -2.0

        vetores = {
            "norte": (0, -1), "sul": (0, 1), "este": (1, 0), "oeste": (-1, 0),
            "nordeste": (1, -1), "sudeste": (1, 1),
            "sudoeste": (-1, 1), "noroeste": (-1, -1)
        }

        if isinstance(input_direcao, str):
            dx, dy = vetores.get(input_direcao.lower(), (0, 0))
        elif isinstance(input_direcao, (tuple, list)):
            dx, dy = input_direcao
        else:
            return -2.0
        pos_atual = self.agentes_posicoes[agente]

        # 2. Nova posição (float para distância, int para grelha)
        nx = pos_atual[0] + dx
        ny = pos_atual[1] + dy

        xi, yi = int(round(nx)), int(round(ny))
        pos_futura = (xi, yi)

        # 3. Verificações de validade
        # Fora do mundo
        if not (0 <= xi < self.largura and 0 <= yi < self.altura):
            return -10.0

        # Obstáculo (exceto saída)
        if pos_futura in self.obstaculos and pos_futura != self.pos_saida:
            return -5.0

        # 4. Atualizar posição
        self.agentes_posicoes[agente] = (xi, yi)

        # 5. Recompensas
        dist_antiga = math.sqrt(
            (self.pos_saida[0] - pos_atual[0]) ** 2 +
            (self.pos_saida[1] - pos_atual[1]) ** 2
        )
        dist_nova = math.sqrt(
            (self.pos_saida[0] - xi) ** 2 +
            (self.pos_saida[1] - yi) ** 2
        )

        # Penalização base por passo
        recompensa = -1.0

        # Progresso em direção à saída
        recompensa += (dist_antiga - dist_nova) * 10

        # Penalizar estagnação / afastamento
        #if dist_nova >= dist_antiga:
        #    recompensa -= 2.0

        # Penalização por revisitar posições
        if pos_futura in self.visitas[agente]:
            recompensa -= 5.0
        else:
            self.visitas[agente].add(pos_futura)
        # 6. Chegou à saída
        if dist_nova < 1.0:
            recompensa += 500.0
            print(f"!!! {agente.nome} ESCAPOU DO LABIRINTO !!!")
            self._alvo_atingido = True

        # 7. Feedback para o agente (aprendizagem)
        agente.avaliacao_estado_atual(recompensa)

        return recompensa
                

    def display(self):
        # Opcional: para debug visual no terminal
        pass

def accoes_validas(self, agente):
    
    if agente not in self.agentes_posicoes:
        return []

    x, y = self.agentes_posicoes[agente]

    direcoes = {
        "norte": (0, -1),
        "sul": (0, 1),
        "este": (1, 0),
        "oeste": (-1, 0),
        "nordeste": (1, -1),
        "sudeste": (1, 1),
        "sudoeste": (-1, 1),
        "noroeste": (-1, -1),
    }

    accoes = []

    for nome, (dx, dy) in direcoes.items():
        nx = int(round(x + dx))
        ny = int(round(y + dy))

        # Limites do mundo
        if not (0 <= nx < self.largura and 0 <= ny < self.altura):
            continue

        pos_futura = (nx, ny)

        # Obstáculo (exceto saída)
        if pos_futura in self.obstaculos and pos_futura != self.pos_saida:
            continue

        accoes.append(nome)

    return accoes
    