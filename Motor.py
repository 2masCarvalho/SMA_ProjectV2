import json
from typing import List
from agente import Agente
from AmbienteFarol import AmbienteFarol
from agente import AgenteDirecional as AgenteFarol

class MotorDeSimulacao:
    def __init__(self, ambiente , agentes):
        self.ambiente = ambiente
        self.agentes = agentes
        for agente in self.agentes:
            agente.set_ambiente(self.ambiente)
            agente.start()

    #O método executa() faz um ciclo completo: todos os agentes observam, 
    # processam, decidem ação e o ambiente executa. Depois atualiza o ambiente
    def executa(self):
        # 1. Trigger all agents to start their step
        for agente in self.agentes:
            agente.end_step_event.clear()
            agente.start_step_event.set()
        
        # 2. Wait for all agents to finish their step
        for agente in self.agentes:
            agente.end_step_event.wait()
            
        # 3. Update environment
        self.ambiente.atualizacao()

    def listaAgentes(self) -> List[Agente]:
        return self.agentes

    @staticmethod
    def cria(nome_do_ficheiro_parametros: str) -> 'MotorDeSimulacao': 
        with open(nome_do_ficheiro_parametros, 'r') as f: 
            params = json.load(f)

        tipo = params["tipo"]
        ambiente = None
        agentes = []

        if tipo == "farol":
            # Extract environment params
            env_params = params["ambiente"]
            ambiente = AmbienteFarol(
                farol_pos=tuple(env_params["pos_farol"]),
                dimensoes=tuple(env_params["dimensao"]),
                obstaculos=[tuple(o) for o in env_params.get("obstaculos", [])]
            )
            
            for agente_info in params["agentes"]:
                # Map JSON keys to constructor args
                agente = AgenteFarol(
                    nome=agente_info.get("nome", "Agente"),
                    posicao=tuple(agente_info.get("posicao", [0,0])),
                    energia=agente_info.get("energia", 100)
                )
                ambiente.adicionar_agente(agente, agente.posicao)
                agentes.append(agente)
                
        elif tipo == "labirinto":
            env_params = params["ambiente"]
            # Extrair parâmetros do ambiente
            dimensoes = tuple(env_params.get("dimensao", [10, 10]))
            paredes = [tuple(p) for p in env_params.get("paredes", [])]
            saida = tuple(env_params.get("saida", [9, 9]))
            inicio = tuple(env_params.get("inicio", [0, 0]))
            
            ambiente = AmbienteLabirinto(dimensoes, paredes, saida, inicio)
            
            for agente_info in params["agentes"]:
                agente_tipo = agente_info.get("subtipo", "explorador")
                nome = agente_info.get("nome", "Agente")
                posicao = tuple(agente_info.get("posicao", inicio))
                
                if agente_tipo == "explorador":
                    agente = AgenteLabirinto(nome, posicao)
                elif agente_tipo == "inteligente":
                    # Assumindo que AgenteInteligente tem construtor similar
                    from agente import AgenteInteligente
                    agente = AgenteInteligente(nome, posicao)
                else:
                    # Default
                    agente = AgenteLabirinto(nome, posicao)
                    
                ambiente.adicionar_agente(agente, posicao)
                agentes.append(agente)
        
        return MotorDeSimulacao(ambiente, agentes)