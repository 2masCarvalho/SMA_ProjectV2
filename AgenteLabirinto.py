import json
import random
from collections import deque # Necessário para a memória
from AgenteRL import AgenteRL
from Modelos import Accao, Observacao
from Sensor import SensorDirecao, SensorProximidade

class AgenteLabirinto(AgenteRL):
    def __init__(self, nome, posicao, ficheiro_config, learning_mode=True):
        super().__init__(nome, posicao, ficheiro_config, learning_mode)
        
        # --- MEMÓRIA EXTRA ESPECÍFICA PARA LABIRINTO ---
        # Guarda as últimas 6 posições para detetar se está preso
        self.memoria_posicoes = deque(maxlen=6)
        
        # Guarda a última ação para dar "inércia" (resolver corredores)
        self.ultima_accao_nome = "parado"

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

        # 3. Recolher dados dos sensores
        for s in self.sensores:
            if isinstance(s, SensorDirecao):
                obs = s.detetar(self.ambiente, self)
                d = obs.dados.get("direcao", (0, 0))
                direcao_alvo = self._vetor_para_cardinal(d[0], d[1])

            elif isinstance(s, SensorProximidade):
                obs = s.detetar(self.ambiente, self)
                dados_prox = obs.dados.get("proximidade_obstaculos", {})
                # Ordem: N, S, E, O, NE, SE, SO, NO
                direcoes = [
                    (0, -1), (0, 1), (1, 0), (-1, 0),
                    (1, -1), (1, 1), (-1, 1), (-1, -1)
                ]
                for i, (dx, dy) in enumerate(direcoes):
                    if dados_prox.get(f"obs_{dx}_{dy}"):
                        obstaculos_perto[i] = 1

        # 4. CONSTRUIR O ESTADO RL (OTIMIZADO)
        # Adicionamos self.ultima_accao_nome para ele saber se estava a subir ou descer
        estado_rl = (direcao_alvo, tuple(obstaculos_perto), self.ultima_accao_nome)

        # 5. Criar observação
        obs_para_politica = Observacao({
            "estado_customizado": estado_rl,
            "posicao": self.posicao
        })

        # 6. Decisão (Com lógica Anti-Loop e Epsilon Dinâmico)
        if self.politica:
            epsilon_to_use = 0.0 # Default para Teste
            
            # Se estivermos a treinar, usa o valor que vem do treinar.py
            if self.learning_mode:
                epsilon_to_use = self.epsilon_atual if self.epsilon_atual is not None else 0.1

            # --- DETETOR DE LOOP ---
            esta_preso = self._detectar_loop()
            if esta_preso:
                # Se estiver preso, força exploração alta para sair dali
                epsilon_to_use = 0.6 
            
            # Pede ação à política com o epsilon correto
            accao = self.politica.selecionar_accao(obs_para_politica, epsilon_override=epsilon_to_use)
            
            if accao:
                # Atualiza a inércia (última ação)
                if accao.tipo == "mover":
                    self.ultima_accao_nome = accao.parametros.get("direcao", "parado")
                
                # --- SAFETY LAYER (Só se não estiver preso) ---
                # Se não estiver a aprender E não estiver preso, evita bater em paredes
                if not self.learning_mode and not esta_preso:
                    direcao = accao.parametros.get("direcao")
                    idx_map = {"norte": 0, "sul": 1, "este": 2, "oeste": 3}
                    idx = idx_map.get(direcao)
                    
                    # Se a ação vai contra uma parede (índices 0-3 dos obstáculos)
                    if idx is not None and idx < 4 and obstaculos_perto[idx] == 1:
                        # Tenta encontrar uma direção livre
                        accoes_livres = [d for d, i in idx_map.items() if obstaculos_perto[i] == 0]
                        if accoes_livres:
                            # Escolhe qualquer uma livre (fallback simples)
                            return Accao("mover", {"direcao": random.choice(accoes_livres)})

                return accao

        # Fallback de segurança total
        print(f"AVISO: Fallback aleatório para {self.nome}")
        accoes_validas = self.ambiente.accoes_validas(self)
        if not accoes_validas: return Accao("parar")
        return Accao("mover", {"direcao": random.choice(accoes_validas)})