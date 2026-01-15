from abc import ABC, abstractmethod
import json
import threading

from Modelos import Observacao, Accao
from Sensor import Sensor

class Agente(ABC, threading.Thread):
    """Interface base para todos os agentes."""
    def __init__(self, nome: str):
        threading.Thread.__init__(self)
        self.nome = nome
        self.recompensa_total = 0.0
        self.passos = 0
        self.sensores = []
        self.ultima_observacao = None
        self.running = False
        self.ambiente = None 
        self.start_step_event = threading.Event()
        self.end_step_event = threading.Event()

    def set_ambiente(self, ambiente):
        self.ambiente = ambiente
        if hasattr(self, 'posicao'):
            self.posicao_inicial = self.posicao        

    def run(self):
        self.running = True
        while self.running:
            self.start_step_event.wait()
            if not self.running: break
            self.start_step_event.clear()

            if self.ambiente:
                if self.sensores:
                    dados_combinados = {}
                    for sensor in self.sensores:
                        obs_sensor = sensor.detetar(self.ambiente, self)
                        dados_combinados.update(obs_sensor.dados)
                    observacao= Observacao(dados_combinados)
                else:
                    observacao = self.ambiente.observacaoPara(self)

                self.observacao(observacao)
                accao = self.age()
                self.ambiente.agir(accao, self)
            
            self.end_step_event.set()

    @abstractmethod
    def observacao(self, obs: 'Observacao'):
        """Recebe a observação do ambiente. Atualiza o estado interno do agente."""
        self.ultima_observacao = obs

    @abstractmethod
    def age(self) -> 'Accao':
        """Decide e retorna a ação a ser executada."""
        pass

    @abstractmethod
    def avaliacao_estado_atual(self, recompensa: float):
        """Recebe a recompensa e atualiza o estado interno/política."""
        self.recompensa_total += recompensa
        self.passos += 1

    def instala(self, sensor: Sensor):
        """Instala um sensor no agente."""
        self.sensores.append(sensor)

    @abstractmethod
    def comunica(self, mensagem: str, de_agente: 'Agente'):
        """Recebe info de uma mensagem de um agente."""
        pass

    @staticmethod
    def cria(nome_do_ficheiro_parametros: str):
        
        return agentes

class AgenteDirecional(Agente):
    def __init__(self, nome, posicao, energia):
        super().__init__(nome)
        self.posicao = posicao
        self.energia = energia
        self.direcao_alvo = None

    def observacao(self, obs):
        super().observacao(obs)
        self.direcao_alvo = obs.get("direcao")

    def age(self):
        return Accao("mover", {"direcao": self.direcao_alvo})
    
    def comunica(self, mensagem: str, de_agente: 'Agente'):
        pass

    def avaliacao_estado_atual(self, recompensa: float):
        super().avaliacao_estado_atual(recompensa)


