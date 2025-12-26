import time
import json
import os
import tkinter as tk
from AmbienteLabirinto import AmbienteLabirinto
from AgenteLabirinto import AgenteLabirinto
from Sensor import SensorDirecao, SensorProximidade
from Motor import MotorDeSimulacao
from visualizador import VisualizadorTk

def testar_labirinto_visual():
    print("=== Iniciando Teste Visual: Agente no Labirinto ===")
    
    # 1. Carregar Configuração do Mapa
    with open("JSONFILES/labirinto1.json", "r") as f:
        config = json.load(f)
    
    amb_cfg = config["ambiente"]
    largura, altura = amb_cfg["dimensao"]
    
    ambiente = AmbienteLabirinto(
        pos_saida=tuple(amb_cfg["pos_saida"]),
        dimensoes=(largura, altura),
        obstaculos=[tuple(o) for o in amb_cfg["obstaculos"]]
    )
    
    # 2. Configurar o Agente e Carregar a Memória
    agente_cfg = config["agentes"][0]
    agente = AgenteLabirinto(
        nome="Agente_Expert",
        posicao=tuple(agente_cfg["posicao"]),
        ficheiro_config=agente_cfg["ficheiro_config"]
    )
    
    # Carregar a Q-Table específica que gerámos no Passo 3
    Q_TABLE_FILE = "qtable_labirinto.pkl"
    if os.path.exists(Q_TABLE_FILE):
        agente.politica.carregar(Q_TABLE_FILE)
        agente.politica.epsilon = 0.0  # Desligar exploração: o agente usa apenas o conhecimento
        print(f"Memória {Q_TABLE_FILE} carregada com sucesso.")
    else:
        print(f"AVISO: {Q_TABLE_FILE} não encontrado. O agente agirá sem treino.")

    # Instalar os sensores
    agente.instala(SensorDirecao())
    agente.instala(SensorProximidade())
    
    ambiente.adicionar_agente(agente, agente.posicao)
    motor = MotorDeSimulacao(ambiente, [agente])
    
    # 3. Inicializar Visualizador Gráfico
    # Ajustamos o tamanho da célula para o mapa 15x15 caber bem no ecrã
    viz = VisualizadorTk(largura, altura, tamanho_celula=40)
    
    print("Simulação em curso... Observa a janela do visualizador.")
    MAX_PASSOS = 150
    
    try:
        for i in range(MAX_PASSOS):
            # Executar um passo da lógica
            motor.executa()
            
            # Atualizar o desenho no ecrã
            viz.desenhar(ambiente, [agente])
            
            # Verificar se o agente conseguiu sair
            if ambiente.simulacao_concluida():
                print("!!! SUCESSO: O agente encontrou a saída do labirinto! !!!")
                time.sleep(2) # Pausa para celebrar o sucesso
                break
                
            time.sleep(0.1) # Velocidade da animação
            
    except tk.TclError:
        print("Janela fechada pelo utilizador.")
    finally:
        print("=== Fim do Teste Visual ===")
        try:
            viz.fechar()
        except:
            pass

if __name__ == "__main__":
    testar_labirinto_visual()
