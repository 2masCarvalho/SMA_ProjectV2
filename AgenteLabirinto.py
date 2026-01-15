import json
import random
from collections import deque
from AgenteRL import AgenteRL
from Modelos import Accao, Observacao
from Sensor import SensorDirecao, SensorProximidade

class AgenteLabirinto(AgenteRL):
    def __init__(self, nome, posicao, ficheiro_config, learning_mode=True):
        super().__init__(nome, posicao, ficheiro_config, learning_mode)
        
        self.memoria_posicoes = deque(maxlen=6)
        self.ultima_accao_nome = "parado"
        
        self.historico_episodio = set()
        
        self.usar_sensores_no_estado = False 

    def _detectar_loop(self):
        if len(self.memoria_posicoes) < 4:
            return False
        p = list(self.memoria_posicoes)
        if p[-1] == p[-3] and p[-2] == p[-4]: return True
        if p[-1] == p[-2] == p[-3]: return True
        return False

    def age(self) -> Accao:
        self.memoria_posicoes.append(self.posicao)

        direcao_alvo = "desconhecida"
        obstaculos_perto = [0] * 8

        for s in self.sensores:
            if isinstance(s, SensorDirecao):
                obs = s.detetar(self.ambiente, self)
                d = obs.dados.get("direcao", (0, 0))
                direcao_alvo = self._vetor_para_cardinal(d[0], d[1])

            elif isinstance(s, SensorProximidade):
                obs = s.detetar(self.ambiente, self)
                dados_prox = obs.dados.get("proximidade_obstaculos", {})
                direcoes = [
                    (0, -1), (0, 1), (1, 0), (-1, 0),
                    (1, -1), (1, 1), (-1, 1), (-1, -1)
                ]
                for i, (dx, dy) in enumerate(direcoes):
                    if dados_prox.get(f"obs_{dx}_{dy}"):
                        obstaculos_perto[i] = 1

        estado_rl = (direcao_alvo, tuple(obstaculos_perto), self.ultima_accao_nome)

        obs_para_politica = Observacao({
            "posicao": self.posicao,  
            "estado_customizado": estado_rl
        })
        
        self.ultima_observacao = obs_para_politica

        if self.politica:
            epsilon_to_use = 0.0
            if self.learning_mode:
                epsilon_to_use = getattr(self.politica, 'epsilon', 0.1)

            esta_preso = self._detectar_loop()
            if esta_preso and self.learning_mode:
                epsilon_to_use = 0.6 
            
            epsilon_original = getattr(self.politica, 'epsilon', 0.1)
            if self.learning_mode:
                self.politica.epsilon = epsilon_to_use
            
            accao = self.politica.selecionar_accao(obs_para_politica)
            
            if self.learning_mode:
                self.politica.epsilon = epsilon_original
            
            if accao:
                if accao.tipo == "mover":
                    self.ultima_accao_nome = accao.parametros.get("direcao", "parado")
                
                if not self.learning_mode and not esta_preso:
                    direcao = accao.parametros.get("direcao")
                    idx_map = {"norte": 0, "sul": 1, "este": 2, "oeste": 3}
                    idx = idx_map.get(direcao)
                    if idx is not None and idx < 4 and obstaculos_perto[idx] == 1:
                        accoes_livres = [d for d, i in idx_map.items() if obstaculos_perto[i] == 0]
                        if accoes_livres:
                            return Accao("mover", {"direcao": random.choice(accoes_livres)})

                self.ultima_acao = accao
                return accao

        return Accao("mover", {"direcao": random.choice(["norte", "sul", "este", "oeste"])})

    def avaliacao_estado_atual(self, recompensa: float):
        if self.passos == 0:
            self.historico_episodio = set()
            self.historico_episodio.add(tuple(self.posicao))

        posicao_atual = tuple(self.posicao)
        
        recompensa_efetiva = recompensa
        
        if posicao_atual in self.historico_episodio:
            recompensa_efetiva -= 2.0  
        
        self.historico_episodio.add(posicao_atual)

        super().avaliacao_estado_atual(recompensa)
        
        if self.politica:
            self.politica.atualizar(recompensa_efetiva)

    def _vetor_para_cardinal(self, dx, dy):
        if abs(dx) > abs(dy):
            return "este" if dx > 0 else "oeste"
        else:
            return "sul" if dy > 0 else "norte"