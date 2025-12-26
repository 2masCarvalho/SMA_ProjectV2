import json
from typing import List
from Agente import Agente
from AmbienteFarol import AmbienteFarol
from AgenteRL import AgenteRL
from AgenteNormal import AgenteNormal
from Agente import AgenteDirecional as AgenteFarol
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
        print(f"DEBUG: A ler ficheiro: {nome_do_ficheiro_parametros}")
        
        with open(nome_do_ficheiro_parametros, 'r') as f:
            params = json.load(f)

        tipo = params.get("tipo")
        print(f"DEBUG: Tipo de ambiente encontrado no JSON: '{tipo}'")
        
        ambiente = None
        agentes = []

        # Variáveis auxiliares para evitar duplicar código de criação de agentes
        env_params = params["ambiente"]
        lista_agentes_json = params.get("agentes", [])

        # ==========================================
        # LÓGICA 1: AMBIENTE FAROL
        # ==========================================
        if tipo == "farol":
            print("DEBUG: Entrou na lógica 'farol'.")
            ambiente = AmbienteFarol(
                farol_pos=tuple(env_params["pos_farol"]),
                dimensoes=tuple(env_params["dimensao"]),
                obstaculos=[tuple(o) for o in env_params.get("obstaculos", [])]
            )

        # ==========================================
        # LÓGICA 2: AMBIENTE LABIRINTO (NOVO)
        # ==========================================
        elif tipo == "labirinto":
            print("DEBUG: Entrou na lógica 'labirinto'.")
            ambiente = AmbienteLabirinto(
                pos_saida=tuple(env_params["pos_saida"]), # JSON usa "pos_saida"
                dimensoes=tuple(env_params["dimensao"]),
                obstaculos=[tuple(o) for o in env_params.get("obstaculos", [])]
            )
        
        else:
            print(f"DEBUG: ERRO - Tipo '{tipo}' desconhecido.")
            return None

        # ==========================================
        # CRIAÇÃO COMUM DOS AGENTES
        # ==========================================
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
                
                # Instalação de Sensores
                # DIREÇÃO: Obrigatório (saber para onde ir)
                novo_agente.instala(SensorDirecao())
                
                # PROXIMIDADE: CRÍTICO NO LABIRINTO
                # No labirinto, precisamos MESMO de saber onde estão as paredes
                novo_agente.instala(SensorProximidade())
                
                # Visão: Opcional
                # novo_agente.instala(SensorVisao(raio_visao=3.0))
                
            elif nome_classe.strip() == "AgenteNormal":
                novo_agente = AgenteNormal(nome, posicao, caminho_config)
                
                # Agente Normal precisa de direção para o modo 'guloso'
                novo_agente.instala(SensorDirecao())
                novo_agente.instala(SensorProximidade()) # Útil se quiseres que ele evite bater
                
            else:
                print(f"   -> AVISO: Classe desconhecida.")

            if novo_agente:
                ambiente.adicionar_agente(novo_agente, posicao)
                if hasattr(novo_agente, 'posicao'): novo_agente.posicao = posicao
                agentes.append(novo_agente)
                print(f"   -> Agente {nome} adicionado.")

        print(f"DEBUG FINAL: Motor criado com {len(agentes)} agentes.")
        return MotorDeSimulacao(ambiente, agentes)