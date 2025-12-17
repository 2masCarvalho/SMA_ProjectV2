from abc import ABC, abstractmethod
import random
from typing import Dict, List, Any
from Modelos import Observacao, Accao

class Politica(ABC):
    """Interface para estratégias de tomada de decisão."""

    @abstractmethod
    def selecionar_accao(self, observacao: Observacao) -> Accao:
        """Decide qual ação tomar com base na observação atual."""
        pass

    @abstractmethod
    def atualizar(self, recompensa: float):
        """Atualiza a política com base na recompensa recebida."""
        pass

class PoliticaAleatoria(Politica):
    """Escolhe uma ação aleatória das opções disponíveis."""
    def __init__(self, accoes_possiveis):
        self.accoes = accoes_possiveis

    def selecionar_accao(self, observacao: Observacao) -> Accao:
        escolha = random.choice(self.accoes)
        return Accao("mover", {"direcao": escolha})

    def atualizar(self, recompensa: float):
        pass # Não aprende nada

class PoliticaQLearning(Politica):
    """Implementa Q-Learning."""
    def __init__(self, accoes_possiveis: List[str], alpha=0.1, gamma=0.9, epsilon=0.3):
        self.q_table = {} # {(x, y): {accao: valor}}
        self.accoes = accoes_possiveis
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        
        # Estado temporário para o ciclo de update
        self.ultimo_estado = None
        self.ultima_accao = None
        self.ultima_recompensa = 0.0
    
    def get_estado_key(self, observacao: Observacao):
        # 1. Tentar obter os dados
        dados = observacao.dados if hasattr(observacao, 'dados') else observacao
        if not isinstance(dados, dict):
            return None

        # --- ALTERAÇÃO AQUI ---
        # Prioridade 1: Se o agente já processou os sensores e mandou um estado pronto
        if "estado_customizado" in dados:
            return dados["estado_customizado"] # Retorna o tuplo (Direcao, Obstaculos)

        # Prioridade 2: Fallback para posição (x,y) se não houver sensores (o modo antigo)
        pos = dados.get("posicao")
        if pos is not None:
            return tuple(pos)
            
        return None


    def selecionar_accao(self, observacao: Observacao) -> Accao:
        estado_atual = self.get_estado_key(observacao)

        # --- DEBUG PRINT ---
        conhecido = estado_atual in self.q_table
        print(f"Estado: {estado_atual} | Conhecido? {conhecido}")
        if conhecido:
            valores = self.q_table[estado_atual]
            print(f"   -> Valores: {valores}")
        
        # 1. Se tivermos um passo anterior pendente, fazemos o update do Q-Value agora
        # Q(S, A) = Q(S, A) + alpha * (R + gamma * max(Q(S', a')) - Q(S, A))
        if self.ultimo_estado is not None and self.ultima_accao is not None:
            self._atualizar_q_table(self.ultimo_estado, self.ultima_accao, self.ultima_recompensa, estado_atual)

        # 2. Escolher ação (Epsilon-Greedy)
        if random.random() < self.epsilon:
            accao_nome = random.choice(self.accoes)
        else:
            accao_nome = self._melhor_accao(estado_atual)

        # 3. Guardar estado para o próximo update
        self.ultimo_estado = estado_atual
        self.ultima_accao = accao_nome
        
        return Accao("mover", {"direcao": accao_nome})

    def atualizar(self, recompensa: float):
        # Apenas guardamos a recompensa. O update matemático acontece 
        # quando soubermos o "próximo estado" (na próxima chamada de selecionar_accao)
        self.ultima_recompensa = recompensa

    def _melhor_accao(self, estado):
        if estado not in self.q_table:
            return random.choice(self.accoes)
        
        # Encontrar ação com maior valor Q
        q_valores = self.q_table[estado]
        # Se estado existe mas vazio (não deve acontecer se inicializarmos), random
        if not q_valores:
            return random.choice(self.accoes)
            
        # Retorna a ação com max valor. Em caso de empate, max escolhe uma (a primeira).
        return max(q_valores, key=q_valores.get)

    def _atualizar_q_table(self, s, a, r, s_next):
        if s not in self.q_table:
            self.q_table[s] = {ac: 0.0 for ac in self.accoes}
        
        if s_next not in self.q_table:
            self.q_table[s_next] = {ac: 0.0 for ac in self.accoes}
            
        old_q = self.q_table[s][a]
        next_max = max(self.q_table[s_next].values())
        
        new_q = old_q + self.alpha * (r + self.gamma * next_max - old_q)
        self.q_table[s][a] = new_q

    def salvar(self, caminho: str):
        import pickle
        with open(caminho, 'wb') as f:
            pickle.dump(self.q_table, f)
        print(f"Política salva em {caminho}")

    def carregar(self, caminho: str):
        import pickle
        try:
            with open(caminho, 'rb') as f:
                self.q_table = pickle.load(f)
            print(f"Política carregada de {caminho}")
        except FileNotFoundError:
            print(f"Ficheiro {caminho} não encontrado. Começando com Q-Table vazia.")

# vai deretamente ao farol
class PoliticaGulosa(Politica):
    """Escolhe a ação que mais aproxima o agente do alvo (baseado em sensores)."""
    def __init__(self, accoes_possiveis):
        self.accoes = accoes_possiveis

    def selecionar_accao(self, observacao: Observacao) -> Accao:
        # A observação tem de vir do SensorDirecao
        dados = observacao.dados if hasattr(observacao, 'dados') else observacao
        vetor = dados.get("direcao", (0,0))
        dx, dy = vetor

        if dx == 0 and dy == 0:
            return Accao("parar")

        # Lógica das Diagonais (a mesma que tinhas no agente)
        limiar = 0.3
        dir_v, dir_h = "", ""

        if dy < -limiar: dir_v = "norte"
        elif dy > limiar: dir_v = "sul"
        
        if dx > limiar: dir_h = "este"
        elif dx < -limiar: dir_h = "oeste"

        if dir_v and dir_h:
            # Combinar para diagonal
            mapa = {
                ("norte", "este"): "nordeste", ("norte", "oeste"): "noroeste",
                ("sul", "este"): "sudeste",   ("sul", "oeste"): "sudoeste"
            }
            comb = mapa.get((dir_v, dir_h))
            if comb: return Accao("mover", {"direcao": comb})

        # Cardinal fallback
        if abs(dx) > abs(dy):
            return Accao("mover", {"direcao": "este" if dx > 0 else "oeste"})
        else:
            return Accao("mover", {"direcao": "sul" if dy > 0 else "norte"})

    def atualizar(self, recompensa: float):
        pass # Não aprende, segue regra fixa