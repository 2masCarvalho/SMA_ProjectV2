import json
from agente import Agente
from Modelos import Accao
from Sensor import SensorDirecao
from Politica import PoliticaAleatoria, PoliticaGulosa

class AgenteNormal(Agente):
    def __init__(self, nome: str, posicao: tuple, ficheiro_config: str = None):
        super().__init__(nome)
        self.posicao = posicao
        self.cor = "blue"
        
        self.accoes_possiveis = [
            "norte", "sul", "este", "oeste", 
            "nordeste", "sudeste", "sudoeste", "noroeste"
        ]
        
        self.politica = PoliticaAleatoria(self.accoes_possiveis) 

        if ficheiro_config:
            self._carregar_e_definir_politica(ficheiro_config)

    def _carregar_e_definir_politica(self, caminho):
        try:
            caminho_limpo = caminho.lstrip('/') if caminho.startswith('/') else caminho
            with open(caminho_limpo, 'r') as f:
                cfg = json.load(f)
                modo = cfg.get("modo", "aleatorio")
                
                print(f"[{self.nome}] Modo configurado: {modo}")

                if modo == "seguidor" or modo == "guloso":
                    self.politica = PoliticaGulosa(self.accoes_possiveis)
                else:
                    self.politica = PoliticaAleatoria(self.accoes_possiveis)

        except Exception as e:
            print(f"Erro config AgenteNormal: {e}")

    def age(self):
        obs = None
        
        if isinstance(self.politica, PoliticaGulosa):
            sensor_dir = next((s for s in self.sensores if isinstance(s, SensorDirecao)), None)
            if sensor_dir:
                obs = sensor_dir.detetar(self.ambiente, self)
        
        if obs is None:
            obs = self.ultima_observacao if self.ultima_observacao else {}

        return self.politica.selecionar_accao(obs)

    def observacao(self, obs):
        self.ultima_observacao = obs

    def avaliacao_estado_atual(self, recompensa: float):
        super().avaliacao_estado_atual(recompensa)
        self.politica.atualizar(recompensa)

    def comunica(self, mensagem: str, de_agente):
        pass