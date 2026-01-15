import math
from typing import Tuple, List, Set, Dict
from Ambiente import Ambiente
from Modelos import Observacao, Accao

class AmbienteLabirinto(Ambiente):
    
    def __init__(self, pos_saida: Tuple[int, int], dimensoes: Tuple[int, int], obstaculos: List[Tuple[int, int]] = None):
        super().__init__()
        self.farol_pos = pos_saida 
        self.pos_saida = pos_saida
        self.dimensoes = dimensoes
        self.largura, self.altura = dimensoes
        self.obstaculos = set(obstaculos) if obstaculos else set()
        
        self.agentes_posicoes: Dict[object, Tuple[int, int]] = {}
        self.posicoes_iniciais: Dict[object, Tuple[int, int]] = {} 
        self.visitas: Dict[object, Set[Tuple[int, int]]] = {} 
        
        self._alvo_atingido = False

    def simulacao_concluida(self) -> bool:
        return self._alvo_atingido

    def adicionar_agente(self, agente, pos_inicial: Tuple[int, int]):
        self.agentes_posicoes[agente] = pos_inicial
        self.posicoes_iniciais[agente] = pos_inicial
        
        self.visitas[agente] = set()
        self.visitas[agente].add(pos_inicial)

    def reset(self):
        self._alvo_atingido = False
        
        for agente, pos_init in self.posicoes_iniciais.items():
            self.agentes_posicoes[agente] = pos_init
            
            self.visitas[agente] = set()
            self.visitas[agente].add(pos_init)
            
            if hasattr(agente, "reset_estado"):
                agente.reset_estado()

    def observacaoPara(self, agente) -> Observacao:
        if agente not in self.agentes_posicoes:
            return Observacao({})
        
        pos_agente = self.agentes_posicoes[agente]
        dx = self.pos_saida[0] - pos_agente[0]
        dy = self.pos_saida[1] - pos_agente[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        direcao = (dx/dist, dy/dist) if dist > 0 else (0,0)
        
        return Observacao({
            "direcao": direcao, 
            "posicao": pos_agente, 
            "distancia": dist
        })

    def atualizacao(self):
        pass

    def agir(self, accao: Accao, agente) -> float:
        return self._agir_safe(accao, agente)

    def _agir_safe(self, accao: Accao, agente) -> float:
        if accao.tipo != "mover":
            return -2.0

        input_direcao = accao.parametros.get("direcao")
        if not input_direcao:
            return -2.0

        vetores = {
            "norte": (0, -1), "sul": (0, 1), "este": (1, 0), "oeste": (-1, 0),
            "nordeste": (1, -1), "sudeste": (1, 1),
            "sudoeste": (-1, 1), "noroeste": (-1, -1)
        }

        dx, dy = (0, 0)
        if isinstance(input_direcao, str):
            dx, dy = vetores.get(input_direcao.lower(), (0, 0))
        elif isinstance(input_direcao, (tuple, list)):
            dx, dy = input_direcao
        
        pos_atual = self.agentes_posicoes[agente]

        nx = pos_atual[0] + dx
        ny = pos_atual[1] + dy
        xi, yi = int(round(nx)), int(round(ny))
        pos_futura = (xi, yi)

        recompensa = -0.05 

        saiu_limites = not (0 <= xi < self.largura and 0 <= yi < self.altura)
        bateu_obstaculo = (pos_futura in self.obstaculos and pos_futura != self.pos_saida)

        if saiu_limites or bateu_obstaculo:
            return -0.5 

        self.agentes_posicoes[agente] = (xi, yi)

        dist_antiga = math.sqrt((self.pos_saida[0] - pos_atual[0])**2 + (self.pos_saida[1] - pos_atual[1])**2)
        dist_nova = math.sqrt((self.pos_saida[0] - xi)**2 + (self.pos_saida[1] - yi)**2)

        melhoria = dist_antiga - dist_nova

        if melhoria > 0:
            recompensa += 0.1
        else:
            recompensa += 0.0 

        if pos_futura in self.visitas[agente]:
            recompensa -= 0.1
        else:
            self.visitas[agente].add(pos_futura)

        if dist_nova < 1.0 or pos_futura == self.pos_saida:
            recompensa += 100.0
            self._alvo_atingido = True

        agente.avaliacao_estado_atual(recompensa)

        return recompensa

    def accoes_validas(self, agente):
        if agente not in self.agentes_posicoes:
            return []

        x, y = self.agentes_posicoes[agente]
        direcoes = {
            "norte": (0, -1), "sul": (0, 1), "este": (1, 0), "oeste": (-1, 0),
            "nordeste": (1, -1), "sudeste": (1, 1), "sudoeste": (-1, 1), "noroeste": (-1, -1),
        }

        accoes = []
        for nome, (dx, dy) in direcoes.items():
            nx, ny = int(round(x + dx)), int(round(y + dy))

            if not (0 <= nx < self.largura and 0 <= ny < self.altura):
                continue
            
            pos_f = (nx, ny)
            if pos_f in self.obstaculos and pos_f != self.pos_saida:
                continue

            accoes.append(nome)
        return accoes