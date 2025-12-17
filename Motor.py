import json
from typing import List
from agente import Agente
from AmbienteFarol import AmbienteFarol
from AgenteRL import AgenteRL
from AgenteNormal import AgenteNormal
from agente import AgenteDirecional as AgenteFarol
from Sensor import SensorVisao, SensorDirecao, SensorProximidade

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

        # VERIFICAÇÃO 1: O tipo coincide?
        if tipo == "farol":
            print("DEBUG: Entrou na lógica 'farol'.")
            env_params = params["ambiente"]
            
            # 1. Criar o Ambiente
            ambiente = AmbienteFarol(
                farol_pos=tuple(env_params["pos_farol"]),
                dimensoes=tuple(env_params["dimensao"]),
                obstaculos=[tuple(o) for o in env_params.get("obstaculos", [])]
            )
            
            lista_agentes_json = params.get("agentes", [])
            print(f"DEBUG: Encontrei {len(lista_agentes_json)} configurações de agentes no JSON.")

            # 2. Criar os Agentes
            for i, agente_info in enumerate(lista_agentes_json):
                nome_classe = agente_info.get("classe", "AgenteFarol")
                nome = agente_info.get("nome", "Agente")
                pos_raw = agente_info.get("posicao", [0, 0])
                posicao = tuple(pos_raw)
                caminho_config = agente_info.get("ficheiro_config", "")
                
                print(f"DEBUG: A processar Agente {i} | Classe: '{nome_classe}' | Nome: {nome}")

                novo_agente = None

                # VERIFICAÇÃO 2: Instanciar e CONFIGURAR SENSORES
                if nome_classe.strip() == "AgenteRL":
                    print("   -> A criar AgenteRL...")
                    novo_agente = AgenteRL(nome, posicao, caminho_config)
                    
                    # --- INSTALAÇÃO DE SENSORES (NOVO) ---
                    print("   -> Instalando sensores no AgenteRL...")
                    # Visão: Para detetar o farol quando estiver a 3 metros ou menos
                    #novo_agente.instala(SensorVisao(raio_visao=3.0))
                    # Direção: Bússola que aponta para o farol (essencial para ele aprender rápido)
                    novo_agente.instala(SensorDirecao())
                    # Proximidade: (Opcional) Para detetar paredes
                    #novo_agente.instala(SensorProximidade())
                    
                elif nome_classe.strip() == "AgenteNormal":
                    print("   -> A criar AgenteNormal...")
                    novo_agente = AgenteNormal(nome, posicao, caminho_config)
                    
                    # --- ALTERAÇÃO AQUI ---
                    # 1. OBRIGATÓRIO: Sem isto ele não sabe onde está o farol
                    novo_agente.instala(SensorDirecao())
                    
                    # 3. Opcional: Se quiseres que ele também tenha "visão" de perto
                    #novo_agente.instala(SensorVisao(raio_visao=3.0))
                    
                else:
                    print(f"   -> AVISO: Classe '{nome_classe}' não corresponde a nenhum IF known.")

                # 3. Adicionar ao Ambiente e à Lista
                if novo_agente:
                    ambiente.adicionar_agente(novo_agente, posicao)
                    
                    # Garantir que a posição interna está correta
                    if hasattr(novo_agente, 'posicao'):
                        novo_agente.posicao = posicao
                        
                    agentes.append(novo_agente)
                    print(f"   -> Agente adicionado com sucesso. Total atual: {len(agentes)}")
                else:
                    print("   -> ERRO: Agente não foi criado (ficou None).")

        elif tipo == "labirinto":
            # Podes adicionar lógica de labirinto aqui se precisares
            pass
        else:
            print(f"DEBUG: ERRO - Tipo '{tipo}' não é 'farol' nem 'labirinto'.")

        print(f"DEBUG FINAL: Motor criado com {len(agentes)} agentes.")
        return MotorDeSimulacao(ambiente, agentes)