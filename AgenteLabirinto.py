import json
from AgenteRL import AgenteRL
from Modelos import Accao, Observacao
from Sensor import SensorDirecao, SensorProximidade

class AgenteLabirinto(AgenteRL):
    """
    Agente especializado para o Labirinto.
    Diferença principal: O estado combina Direção (onde está a saída) 
    com Proximidade (onde estão as paredes).
    """
    
    def age(self) -> Accao:
        # 1. Inicializar variáveis de perceção
        direcao_alvo = "desconhecida"
        # Lista de 8 posições: 1 se houver parede, 0 se estiver livre
        obstaculos_perto = [0] * 8

        # 2. Recolher dados dos sensores instalados
        for s in self.sensores:
            if isinstance(s, SensorDirecao):
                obs = s.detetar(self.ambiente, self)
                d = obs.dados.get("direcao", (0,0))
                direcao_alvo = self._vetor_para_cardinal(d[0], d[1])
            
            elif isinstance(s, SensorProximidade):
                obs = s.detetar(self.ambiente, self)
                dados_prox = obs.dados.get("proximidade_obstaculos", {})
                # Mapeamento para as 8 direções ao redor do agente
                direcoes = [(0, -1), (0, 1), (1, 0), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
                for i, (dx, dy) in enumerate(direcoes):
                    if dados_prox.get(f"obs_{dx}_{dy}"):
                        obstaculos_perto[i] = 1

        # 3. Construir o Estado Composto
        # O Q-Learning agora aprende: "Se a saída está a Norte MAS tenho parede a Norte, vou para Este"
        estado_rl = (direcao_alvo, tuple(obstaculos_perto))

        # 4. Preparar observação para a política de decisão
        obs_para_politica = Observacao({
            "estado_customizado": estado_rl,
            "posicao": self.posicao 
        })

        if self.politica:
            return self.politica.selecionar_accao(obs_para_politica)
        
        return Accao("parar")
