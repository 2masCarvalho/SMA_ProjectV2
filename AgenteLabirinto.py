import json
import random
from AgenteRL import AgenteRL
from Modelos import Accao, Observacao
from Sensor import SensorDirecao, SensorProximidade


class AgenteLabirinto(AgenteRL):
    def age(self) -> Accao:
        # 1. Inicializar variáveis de perceção
        direcao_alvo = "desconhecida"
        obstaculos_perto = [0] * 8

        # 2. Recolher dados dos sensores instalados
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

        # 3. Construir o estado RL
        estado_rl = (direcao_alvo, tuple(obstaculos_perto))

        # 4. Criar observação para a política
        obs_para_politica = Observacao({
            "estado_customizado": estado_rl,
            "posicao": self.posicao
        })

        # 5. Delegar decisão à política
        if self.politica:
            accao = self.politica.selecionar_accao(obs_para_politica)
            if accao:
                return accao
            else:
                print(f"AVISO: A política retornou None para o estado {estado_rl}")
        else:
            print(f"AVISO: Nenhuma política carregada para {self.nome}")

        # 6. Fallback obrigatório → explorar
        # Obter ações válidas diretamente do ambiente
        accoes_validas = self.ambiente.accoes_validas(self)
        return Accao("mover", {"direcao": random.choice(accoes_validas)})

