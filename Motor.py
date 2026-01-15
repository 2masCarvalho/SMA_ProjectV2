import json
from typing import List
from agente import Agente
from AmbienteFarol import AmbienteFarol
from AgenteRL import AgenteRL
from AgenteNormal import AgenteNormal
from AgenteLabirinto import AgenteLabirinto
from agente import AgenteDirecional as AgenteFarol
from Sensor import SensorVisao, SensorDirecao, SensorProximidade
from AmbienteLabirinto import AmbienteLabirinto

class MotorDeSimulacao:
    def __init__(self, ambiente , agentes):
        self.ambiente = ambiente
        self.agentes = agentes
        
        self.largura, self.altura = ambiente.dimensoes

        for agente in self.agentes:
            agente.set_ambiente(self.ambiente)
            agente.start()
    
    def executa(self):
        for agente in self.agentes:
            agente.end_step_event.clear()
            agente.start_step_event.set()
        
        for agente in self.agentes:
            agente.end_step_event.wait()
            
        self.ambiente.atualizacao()

    def listaAgentes(self) -> List[Agente]:
        return self.agentes

    @staticmethod
    def cria(nome_do_ficheiro_parametros: str) -> 'MotorDeSimulacao': 
        print(f"DEBUG: A ler ficheiro: {nome_do_ficheiro_parametros}")
        
        with open(nome_do_ficheiro_parametros, 'r') as f:
            params = json.load(f)

        tipo = params.get("tipo")
        print(f"DEBUG: Tipo de ambiente encontrado no JSON: '{tipo}'")
        
        ambiente = None
        agentes = []

        env_params = params["ambiente"]
        lista_agentes_json = params.get("agentes", [])

        if tipo == "farol":
            print("DEBUG: Entrou na lógica 'farol'.")
            ambiente = AmbienteFarol(
                farol_pos=tuple(env_params["pos_farol"]),
                dimensoes=tuple(env_params["dimensao"]),
                obstaculos=[tuple(o) for o in env_params.get("obstaculos", [])]
            )

        elif tipo == "labirinto":
            print("DEBUG: Entrou na lógica 'labirinto'.")
            ambiente = AmbienteLabirinto(
                pos_saida=tuple(env_params["pos_saida"]), 
                dimensoes=tuple(env_params["dimensao"]),
                obstaculos=[tuple(o) for o in env_params.get("obstaculos", [])]
            )
        
        else:
            print(f"DEBUG: ERRO - Tipo '{tipo}' desconhecido.")
            return None

        print(f"DEBUG: Encontrei {len(lista_agentes_json)} agentes.")

        for i, agente_info in enumerate(lista_agentes_json):
            nome_classe = agente_info.get("classe", "AgenteFarol")
            nome = agente_info.get("nome", "Agente")
import json
from typing import List
from agente import Agente
from AmbienteFarol import AmbienteFarol
from AgenteRL import AgenteRL
from AgenteNormal import AgenteNormal
from AgenteLabirinto import AgenteLabirinto
from agente import AgenteDirecional as AgenteFarol
from Sensor import SensorVisao, SensorDirecao, SensorProximidade
from AmbienteLabirinto import AmbienteLabirinto

class MotorDeSimulacao:
    def __init__(self, ambiente , agentes):
        self.ambiente = ambiente
        self.agentes = agentes
        
        self.largura, self.altura = ambiente.dimensoes

        for agente in self.agentes:
            agente.set_ambiente(self.ambiente)
            agente.start()
    
    def executa(self):
        for agente in self.agentes:
            agente.end_step_event.clear()
            agente.start_step_event.set()
        
        for agente in self.agentes:
            agente.end_step_event.wait()
            
        self.ambiente.atualizacao()

    def listaAgentes(self) -> List[Agente]:
        return self.agentes

    @staticmethod
    def cria(nome_do_ficheiro_parametros: str) -> 'MotorDeSimulacao': 
        print(f"DEBUG: A ler ficheiro: {nome_do_ficheiro_parametros}")
        
        with open(nome_do_ficheiro_parametros, 'r') as f:
            params = json.load(f)

        tipo = params.get("tipo")
        print(f"DEBUG: Tipo de ambiente encontrado no JSON: '{tipo}'")
        
        ambiente = None
        agentes = []

        env_params = params["ambiente"]
        lista_agentes_json = params.get("agentes", [])

        if tipo == "farol":
            print("DEBUG: Entrou na lógica 'farol'.")
            ambiente = AmbienteFarol(
                farol_pos=tuple(env_params["pos_farol"]),
                dimensoes=tuple(env_params["dimensao"]),
                obstaculos=[tuple(o) for o in env_params.get("obstaculos", [])]
            )

        elif tipo == "labirinto":
            print("DEBUG: Entrou na lógica 'labirinto'.")
            ambiente = AmbienteLabirinto(
                pos_saida=tuple(env_params["pos_saida"]), 
                dimensoes=tuple(env_params["dimensao"]),
                obstaculos=[tuple(o) for o in env_params.get("obstaculos", [])]
            )
        
        else:
            print(f"DEBUG: ERRO - Tipo '{tipo}' desconhecido.")
            return None

        print(f"DEBUG: Encontrei {len(lista_agentes_json)} agentes.")

        for i, agente_info in enumerate(lista_agentes_json):
            nome_classe = agente_info.get("classe", "AgenteFarol")
            nome = agente_info.get("nome", "Agente")
            posicao = tuple(agente_info.get("posicao", [0, 0]))
            caminho_config = agente_info.get("ficheiro_config", "")
            
            print(f"DEBUG: A processar Agente {i} | {nome_classe}")
            novo_agente = None

            if nome_classe.strip() == "AgenteRL":
                novo_agente = AgenteRL(nome, posicao, caminho_config)
                novo_agente.instala(SensorDirecao())
                #novo_agente.instala(SensorProximidade())

            elif nome_classe.strip() == "AgenteNormal":
                novo_agente = AgenteNormal(nome, posicao, caminho_config)
                novo_agente.instala(SensorDirecao())
                novo_agente.instala(SensorProximidade())

            elif nome_classe.strip() == "AgenteLabirinto":
                novo_agente = AgenteLabirinto(nome, posicao, caminho_config)
                novo_agente.instala(SensorDirecao())
                novo_agente.instala(SensorProximidade())

            else:
                print(f"   -> AVISO: Classe desconhecida.")

            if novo_agente:
                ambiente.adicionar_agente(novo_agente, posicao)
                if hasattr(novo_agente, 'posicao'): novo_agente.posicao = posicao
                agentes.append(novo_agente)
                print(f"   -> Agente {nome} adicionado.")

        print(f"DEBUG FINAL: Motor criado com {len(agentes)} agentes.")
        return MotorDeSimulacao(ambiente, agentes)