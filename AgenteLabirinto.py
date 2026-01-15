import json
import random
from collections import deque
from AgenteRL import AgenteRL
from Modelos import Accao, Observacao
from Sensor import SensorDirecao, SensorProximidade

class AgenteLabirinto(AgenteRL):
    def __init__(self, nome, posicao, ficheiro_config, learning_mode=True):
        super().__init__(nome, posicao, ficheiro_config, learning_mode)
        
        # --- MEMÓRIA DE LOOP ---
        self.memoria_posicoes = deque(maxlen=6)
        self.ultima_accao_nome = "parado"
        
        # --- MEMÓRIA DE REVISITAÇÃO (NOVO) ---
        self.historico_episodio = set()
        
        # Variável para controlar se usamos sensores ou posição pura (teu Politica usa 'posicao')
        self.usar_sensores_no_estado = False 

    def _detectar_loop(self):
        """Verifica se o agente está em oscilação (Ping-Pong)."""
        if len(self.memoria_posicoes) < 4:
            return False
        p = list(self.memoria_posicoes)
        # Padrão A -> B -> A -> B
        if p[-1] == p[-3] and p[-2] == p[-4]: return True
        # Padrão A -> A -> A (Parado na parede)
        if p[-1] == p[-2] == p[-3]: return True
        return False

    def age(self) -> Accao:
        # 1. Atualizar Memória de Posições
        self.memoria_posicoes.append(self.posicao)

        # 2. Inicializar variáveis de perceção
        direcao_alvo = "desconhecida"
        obstaculos_perto = [0] * 8

        # 3. Recolher dados dos sensores (para Safety Layer e detecção de parede)
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

        # 4. CONSTRUIR O ESTADO RL
        # Nota: A tua PoliticaQLearning atual lê observacao.get("posicao").
        # Se quiseres usar estado complexo, terias de alterar o Politica.py.
        # Por agora, mantemos a posição para ser compatível, mas calculamos o complexo se necessário.
        estado_rl = (direcao_alvo, tuple(obstaculos_perto), self.ultima_accao_nome)

        # 5. Criar observação
        obs_para_politica = Observacao({
            "posicao": self.posicao,  # Isto é o que a tua política vai ler
            "estado_customizado": estado_rl
        })
        
        self.ultima_observacao = obs_para_politica

        # 6. Decisão
        if self.politica:
            epsilon_to_use = 0.0
            if self.learning_mode:
                # Tenta ler epsilon da política ou usa default
                epsilon_to_use = getattr(self.politica, 'epsilon', 0.1)

            esta_preso = self._detectar_loop()
            if esta_preso and self.learning_mode:
                epsilon_to_use = 0.6 # Força exploração se estiver preso
            
            # Ajuste temporário do epsilon na política (hack para o epsilon dinâmico)
            epsilon_original = getattr(self.politica, 'epsilon', 0.1)
            if self.learning_mode:
                self.politica.epsilon = epsilon_to_use
            
            accao = self.politica.selecionar_accao(obs_para_politica)
            
            # Restaurar epsilon
            if self.learning_mode:
                self.politica.epsilon = epsilon_original
            
            if accao:
                if accao.tipo == "mover":
                    self.ultima_accao_nome = accao.parametros.get("direcao", "parado")
                
                # --- SAFETY LAYER (Só em Teste e se não estiver preso) ---
                if not self.learning_mode and not esta_preso:
                    direcao = accao.parametros.get("direcao")
                    idx_map = {"norte": 0, "sul": 1, "este": 2, "oeste": 3}
                    idx = idx_map.get(direcao)
                    # Verifica se vai bater numa parede conhecida
                    if idx is not None and idx < 4 and obstaculos_perto[idx] == 1:
                        accoes_livres = [d for d, i in idx_map.items() if obstaculos_perto[i] == 0]
                        if accoes_livres:
                            return Accao("mover", {"direcao": random.choice(accoes_livres)})

                self.ultima_acao = accao
                return accao

        return Accao("mover", {"direcao": random.choice(["norte", "sul", "este", "oeste"])})

    def avaliacao_estado_atual(self, recompensa: float):
        """
        Recebe a recompensa e aplica penalização por revisitação usando .atualizar()
        """
        # Detetar início de novo episódio para limpar memória
        if self.passos == 0:
            self.historico_episodio = set()
            self.historico_episodio.add(tuple(self.posicao))

        posicao_atual = tuple(self.posicao)
        
        # --- LÓGICA DE PENALIZAÇÃO POR REVISITAÇÃO ---
        recompensa_efetiva = recompensa
        
        # Se já estivemos aqui neste episódio...
        if posicao_atual in self.historico_episodio:
            recompensa_efetiva -= 2.0  # Penaliza!
        
        self.historico_episodio.add(posicao_atual)

        # Chama o método da superclasse para os gráficos (usa a recompensa "oficial")
        super().avaliacao_estado_atual(recompensa)
        
        # --- CORREÇÃO DO ERRO ---
        # Em vez de .aprender(), usamos .atualizar() que existe na tua classe PoliticaQLearning.
        # Isto guarda a 'recompensa_efetiva' para ser usada no cálculo do Q-Value no próximo passo.
        if self.politica:
            self.politica.atualizar(recompensa_efetiva)

    def _vetor_para_cardinal(self, dx, dy):
        if abs(dx) > abs(dy):
            return "este" if dx > 0 else "oeste"
        else:
            return "sul" if dy > 0 else "norte"