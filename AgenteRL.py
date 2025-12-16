from agente import Agente
from Modelos import Accao, Observacao
from Politica import Politica

class AgenteRL(Agente):
    """Agente que usa uma política (ex: Q-Learning) para tomar decisões."""
    def __init__(self, nome: str, politica: Politica):
        super().__init__(nome)
        self.politica = politica

    def observacao(self, obs: Observacao):
        super().observacao(obs)
        # A política pode precisar da observação, mas a decisão é feita em age()
        # Aqui apenas guardamos se necessário, mas o Agente base já guarda self.ultima_observacao

    def age(self) -> Accao:
        # 1. Verificar Sensores Visuais PRIMEIRO (Prioridade ao Reflexo)
        if self.sensores:
            # Itera sobre sensores à procura do SensorVisao
            for sensor in self.sensores:
                # Nota: Num código ideal, verificaria se é instância de SensorVisao
                obs = sensor.detetar(self.ambiente, self)
                
                if obs.get("farol_visto"):
                    print(f"[{self.nome}] Contacto visual! A iniciar aproximação final...")
                    # Retorna imediatamente a ação de ir para o farol
                    direcao = obs.get("direcao_visual")
                    return Accao("mover", {"direcao": direcao})

        # 2. Se não viu nada, usa a Memória (Q-Learning)
        if self.ultima_observacao:
            return self.politica.selecionar_accao(self.ultima_observacao)
        return Accao("parar")

    def avaliacao_estado_atual(self, recompensa: float):
        super().avaliacao_estado_atual(recompensa)
        self.politica.atualizar(recompensa)
    
    def comunica(self, mensagem: str, de_agente: Agente):
        pass
