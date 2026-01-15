import json
import random
import math
from collections import deque
from agente import Agente
from Modelos import Accao, Observacao
from Politica import PoliticaQLearning
from Sensor import SensorDirecao, SensorProximidade

class AgenteRL(Agente):
    def __init__(self, nome: str, posicao: tuple, ficheiro_config: str, learning_mode: bool = True):
        super().__init__(nome)
        self.cor = "red"
        self.posicao = posicao 
        self.learning_mode = learning_mode
        self.epsilon_atual = None 

        # Memória para detetar loops (Anti-Stuck)
        self.memoria_posicoes = deque(maxlen=6)
        
        # --- NOVO: Memória da Última Ação ---
        # Guarda o índice da última ação (0-3) ou nome para dar contexto
        self.ultima_accao_nome = "parado" 

        caminho_limpo = ficheiro_config.lstrip('/').lstrip('\\')
        self.ficheiro_config = caminho_limpo
        self.ficheiro_memoria = caminho_limpo.replace(".json", ".pkl")
        
        self.politica = self._criar_politica_do_ficheiro(self.ficheiro_config)
        
        if self.politica:
            self.politica.carregar(self.ficheiro_memoria)

    def set_epsilon(self, novo_valor: float):
        self.epsilon_atual = novo_valor

    def _criar_politica_do_ficheiro(self, caminho: str):
        try:
            caminho_limpo = caminho.lstrip('/') if caminho.startswith('/') else caminho
            with open(caminho_limpo, 'r') as f:
                params = json.load(f)
            
            accoes = params.get("accoes", ["norte", "sul", "este", "oeste", 
                                           "nordeste", "sudeste", "sudoeste", "noroeste"])
            
            return PoliticaQLearning(
                accoes_possiveis=accoes,
                alpha=params.get("alpha", 0.1),
                gamma=params.get("gamma", 0.99), # Gamma alto é bom para labirintos longos
                epsilon=params.get("epsilon", 0.1)
            )
        except Exception as e:
            print(f"ERRO: {e}")
            return None 

    def _vetor_para_cardinal(self, dx, dy):
        if dx == 0 and dy == 0: return "parado"
        limiar = 0.3
        v, h = "", ""
        if dy < -limiar: v = "norte"
        elif dy > limiar: v = "sul"
        if dx > limiar: h = "este"
        elif dx < -limiar: h = "oeste"
        
        mapa = {
            ("norte", "este"): "nordeste", ("norte", "oeste"): "noroeste",
            ("sul", "este"): "sudeste", ("sul", "oeste"): "sudoeste"
        }
        return mapa.get((v, h), v or h)

    def instala(self, sensor):
        super().instala(sensor)

    def observacao(self, obs: Observacao):
        super().observacao(obs)
        if "posicao" in obs.dados:
            self.posicao = obs.dados["posicao"]

    def avaliacao_estado_atual(self, recompensa: float):
        super().avaliacao_estado_atual(recompensa)
        if self.politica and self.learning_mode:
            self.politica.atualizar(recompensa)
            if hasattr(self, 'passos') and self.passos % 100 == 0:
                self.politica.salvar(self.ficheiro_memoria)

    def comunica(self, mensagem: str, de_agente):
        pass

    def _detectar_loop(self):
        if len(self.memoria_posicoes) < 4: return False
        p = list(self.memoria_posicoes)
        if p[-1] == p[-3] and p[-2] == p[-4]: return True # Ping-Pong
        if p[-1] == p[-2] == p[-3]: return True # Parado
        return False

    def age(self) -> Accao:
        self.memoria_posicoes.append(self.posicao)
        
        direcao_farol = "desconhecida"
        vetor_objetivo = (0, 0)
        obstaculos_perto = tuple([0]*8)

        if not self.sensores:
            print(f"[ALERTA] {self.nome} NÃO TEM SENSORES INSTALADOS!")

        for s in self.sensores:
            if isinstance(s, SensorDirecao):
                obs = s.detetar(self.ambiente, self)
                d = obs.dados.get("direcao", (0,0))
                vetor_objetivo = d
                direcao_farol = self._vetor_para_cardinal(d[0], d[1])
            elif isinstance(s, SensorProximidade):
                obs = s.detetar(self.ambiente, self)
                dados_prox = obs.dados.get("proximidade_obstaculos", {})
                chaves_ordem = [(0, -1), (0, 1), (1, 0), (-1, 0)]
                obstaculos_perto = tuple(
                    1 if dados_prox.get(f"obs_{x}_{y}") else 0 
                    for x, y in chaves_ordem
                )

        # --- DEFINIÇÃO DO ESTADO ---
        # Estado = (Onde está o Farol, Obstáculos à volta, O que fiz antes)
        # Isto ajuda a manter o "Momentum" nos corredores
        estado_rl = (direcao_farol, obstaculos_perto, self.ultima_accao_nome)
        
        obs_para_politica = Observacao({
            "estado_customizado": estado_rl,
            "posicao": self.posicao 
        })

        if self.politica:
            epsilon_to_use = 0.0
            if self.learning_mode:
                epsilon_to_use = self.epsilon_atual if self.epsilon_atual is not None else 0.1
            
            # Anti-Stuck Trigger
            esta_preso = self._detectar_loop()
            if esta_preso:
                epsilon_to_use = 0.6 # Aumentei para 60% para garantir que ele sai mesmo dali
            
            accao = self.politica.selecionar_accao(obs_para_politica, epsilon_override=epsilon_to_use)
            
            # Safety Layer (Só se não estiver preso)
            if not self.learning_mode and not esta_preso:
                direcao_escolhida = accao.parametros.get("direcao")
                mapa_idx = {"norte": 0, "sul": 1, "este": 2, "oeste": 3}
                vetores_dir = {"norte": (0, -1), "sul": (0, 1), "este": (1, 0), "oeste": (-1, 0)}
                
                idx = mapa_idx.get(direcao_escolhida)
                if idx is not None and idx < len(obstaculos_perto) and obstaculos_perto[idx] == 1:
                    accoes_livres = []
                    for dir_nome, i in mapa_idx.items():
                        if i < len(obstaculos_perto) and obstaculos_perto[i] == 0:
                            accoes_livres.append(dir_nome)
                    if accoes_livres:
                        melhor_dir = None
                        melhor_score = -float('inf')
                        for dir_nome in accoes_livres:
                            v = vetores_dir[dir_nome]
                            score = v[0] * vetor_objetivo[0] + v[1] * vetor_objetivo[1]
                            score += random.uniform(0, 0.1)
                            if score > melhor_score:
                                melhor_score = score
                                melhor_dir = dir_nome
                        accao = Accao("mover", {"direcao": melhor_dir})
            
            # --- ATUALIZAR A ÚLTIMA AÇÃO ---
            if accao.tipo == "mover":
                self.ultima_accao_nome = accao.parametros.get("direcao", "parado")
            # -------------------------------

            return accao
        
        return Accao("parar")

    def stop(self):
        if self.politica:
            self.politica.salvar(self.ficheiro_memoria)

    def reset_estado(self):
        """Limpa a memória de curto prazo para novos episódios."""
        self.memoria_posicoes.clear()
        self.ultima_accao_nome = "parado"