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
        self.ultima_observacao = None # Guarda sempre a última observação
        self.running = False
        self.ambiente = None # Referência para o ambiente
        self.start_step_event = threading.Event()
        self.end_step_event = threading.Event()

    def set_ambiente(self, ambiente):
        self.ambiente = ambiente

    def run(self):
        self.running = True
        while self.running:
            # Wait for "Start Step" signal
            self.start_step_event.wait()
            if not self.running: break
            self.start_step_event.clear()

            # Cycle: Observe -> Act
            if self.ambiente:
                # Se houver sensores, usar os sensores para obter a observação
                if self.sensores:
                    dados_combinados = {}
                    for sensor in self.sensores:
                        # Cada sensor recolhe info 
                        obs_sensor = sensor.detetar(self.ambiente, self)
                        #Junta os dados de vários sensores
                        dados_combinados.update(obs_sensor.dados)
                        #Sprint("A usar sensor instalado")
                    observacao= Observacao(dados_combinados)
                else:
                    observacao = self.ambiente.observacaoPara(self)

                self.observacao(observacao)
                accao = self.age()
                self.ambiente.agir(accao, self)
            
            # Signal that we are done with this step
            self.end_step_event.set()

    @abstractmethod
    def observacao(self, obs: 'Observacao'):
        """Recebe a observação do ambiente. Atualiza o estado interno do agente."""
        self.ultima_observacao = obs # Atualiza a última observação

    @abstractmethod
    def age(self) -> 'Accao':
        """Decide e retorna a ação a ser executada."""
        pass

    @abstractmethod
    def avaliacao_estado_atual(self, recompensa: float):
        """Recebe a recompensa e atualiza o estado interno/política."""
        self.recompensa_total += recompensa
        self.passos += 1

    def instala(self, sensor: Sensor): # Tipificação melhorada
        """Instala um sensor no agente."""
        self.sensores.append(sensor)

    @abstractmethod
    def comunica(self, mensagem: str, de_agente: 'Agente'):
        """Recebe info de uma mensagem de um agente."""
        pass

    @staticmethod
    def cria(nome_do_ficheiro_parametros: str):
        with open(nome_do_ficheiro_parametros, "r") as f:
            params = json.load(f)

        tipo = params["tipo"]
        agentes_info = params["agentes"]
        agentes = []

        if tipo == "farol":
            for agente_data in agentes_info:
                # Assuming AgenteDirecional is defined or imported
                agentes.append(AgenteDirecional(agente_data.get("nome", "Agente"), agente_data.get("posicao"), agente_data.get("energia", 100)))
        elif tipo == "labirinto":
            for agente_data in agentes_info:
                agente_tipo = agente_data.get("subtipo", "explorador")
                if agente_tipo == "explorador":
                    # Assuming AgenteExplorador is defined or imported
                    agentes.append(AgenteExplorador(agente_data.get("nome", "Agente"), agente_data.get("posicao")))
                elif agente_tipo == "inteligente":
                    # Assuming AgenteInteligente is defined or imported
                    agentes.append(AgenteInteligente(agente_data.get("nome", "Agente"), agente_data.get("posicao")))
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

class AgenteExplorador(Agente):
    def __init__(self, nome, posicao):
        super().__init__(nome)
        self.posicao = posicao
        self.opcoes = []

    def observacao(self, obs):
        super().observacao(obs)
        self.opcoes = obs.get("caminhos", [])

    def age(self):
        if self.opcoes:
            return Accao("mover", {"direcao": self.opcoes[0]})
        return Accao("parar")

    def comunica(self, mensagem: str, de_agente: 'Agente'):
        pass

    def avaliacao_estado_atual(self, recompensa: float):
        super().avaliacao_estado_atual(recompensa)

class AgenteInteligente(Agente):
    def __init__(self, nome, posicao):
        super().__init__(nome)
        self.posicao = posicao

    def observacao(self, obs):
        super().observacao(obs)

    def age(self):
        return Accao("pensar")

    def comunica(self, mensagem: str, de_agente: 'Agente'):
        pass

    def avaliacao_estado_atual(self, recompensa: float):
        super().avaliacao_estado_atual(recompensa)
