import json
from agente import Agente
from Modelos import Accao, Observacao
from Politica import PoliticaQLearning

class AgenteRL(Agente):
    """Agente que usa uma política (ex: Q-Learning) para tomar decisões."""
    
    # --- MUDANÇA 1: A assinatura do init agora aceita o que vem do JSON ---
    def __init__(self, nome: str, posicao: tuple, ficheiro_config: str):
        super().__init__(nome)
        self.cor = "red"
        self.posicao = posicao # Guardar a posição inicial
        
        # --- MUDANÇA 2: Carregar a configuração e criar a política ---
        self.politica = self._criar_politica_do_ficheiro(ficheiro_config)

    def _criar_politica_do_ficheiro(self, caminho: str):
        """Lê o JSON e instancia a política QLearning."""
        try:
            # Limpeza do caminho se necessário
            caminho_limpo = caminho.lstrip('/') if caminho.startswith('/') else caminho
            
            with open(caminho_limpo, 'r') as f:
                params = json.load(f)
                
            print(f"[{self.nome}] A carregar política de {caminho_limpo}...")
            
            # Aqui crias a tua política com os dados do JSON
            # Exemplo de como o JSON pode ser usado:
            return PoliticaQLearning(
                accoes_possiveis=params.get("accoes", ["norte", "sul", "este", "oeste"]),
                alpha=params.get("alpha", 0.1),   # Taxa de aprendizagem
                gamma=params.get("gamma", 0.9),   # Fator de desconto
                epsilon=params.get("epsilon", 0.1) # Exploração
            )
            
        except Exception as e:
            print(f"ERRO CRÍTICO: Não foi possível carregar a política para {self.nome}: {e}")
            # Retorna uma política vazia ou default para não crashar
            return None 

    def observacao(self, obs: Observacao):
        super().observacao(obs)

    def age(self) -> Accao:
        # 1. Verificar Sensores Visuais (Prioridade)
        if self.sensores:
            for sensor in self.sensores:
                obs = sensor.detetar(self.ambiente, self)
                # Nota: Garante que 'obs' aqui é um dicionário ou que Observacao tem .get()
                val = obs.get("farol_visto") if isinstance(obs, dict) else getattr(obs, "dados", {}).get("farol_visto")
                
                if val:
                    print(f"[{self.nome}] Contacto visual! A iniciar aproximação final...")
                    # Assume-se que a info da direção está na observação
                    direcao = obs.get("direcao_visual") if isinstance(obs, dict) else getattr(obs, "dados", {}).get("direcao_visual")
                    return Accao("mover", {"direcao": direcao})

        # 2. Se não viu nada, usa a Memória (Q-Learning)
        if self.politica and self.ultima_observacao:
            return self.politica.selecionar_accao(self.ultima_observacao)
        
        return Accao("parar")

    def avaliacao_estado_atual(self, recompensa: float):
        super().avaliacao_estado_atual(recompensa)
        if self.politica:
            self.politica.atualizar(recompensa)
    
    def comunica(self, mensagem: str, de_agente: Agente):
        pass