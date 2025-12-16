import sys
import os
import time
import tkinter as tk

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from AmbienteFarol import AmbienteFarol
from AgenteRL import AgenteRL
from Politica import PoliticaQLearning
from Motor import MotorDeSimulacao
from visualizador import VisualizadorTk
from Sensor import SensorDirecao, SensorVisao

def testar_farol_visual_rl():
    print("=== Teste Visual: Problema do Farol (Agente Treinado) ===")
    
    Q_TABLE_FILE = "qtable_farol.pkl"
    if not os.path.exists(Q_TABLE_FILE):
        print(f"ERRO: Ficheiro de política {Q_TABLE_FILE} não encontrado. Execute treinar_farol.py primeiro.")
        return

    # 1. Configurar Política
    accoes_possiveis = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    politica = PoliticaQLearning(accoes_possiveis, epsilon=0.1) 
    politica.carregar(Q_TABLE_FILE)
    
    # 2. Configurar Ambiente (10x10 conforme definido anteriormente)
    largura, altura = 10, 10
    ambiente = AmbienteFarol(
        farol_pos=(8, 8), 
        dimensoes=(largura, altura),
        obstaculos=[(5, 5), (2, 2)]
    )
    
    # 3. Configurar Agente
    agente = AgenteRL("AgenteTreinado", politica)
    # Criar um sensor que sabe calcular a direção
    sensor_bussola = SensorDirecao()
    sensor_visão = SensorVisao(raio_visao=1.5)
    agente.instala(sensor_visão)
    agente.instala(sensor_bussola)
    ambiente.adicionar_agente(agente, (0, 0))
    
    motor = MotorDeSimulacao(ambiente, [agente])
    
    # 4. Inicializar Visualizador
    viz = VisualizadorTk(largura, altura, tamanho_celula=50) # Células maiores para 10x10
    
    print("Iniciando simulação com Visualização...")
    MAX_PASSOS = 50
    
    try:
        for i in range(MAX_PASSOS):
            # Executar passo da simulação
            motor.executa()
            
            # Atualizar Visualização
            viz.desenhar(ambiente, [agente])
            
            # Verificar se chegou
            dist = ambiente.observacaoPara(agente).dados['distancia']
            if dist < 1.0:
                print("!!! SUCESSO: O agente chegou ao farol! !!!")
                # Mostrar estado final por um momento
                viz.desenhar(ambiente, [agente])
                time.sleep(1)
                break
                
            time.sleep(0.2) # Pausa para animação
            
    except tk.TclError:
        print("Janela fechada pelo utilizador.")
    except KeyboardInterrupt:
        print("Interrompido pelo utilizador.")
    finally:
        print("\n=== Fim do Teste ===")
        # Parar threads
        agente.running = False
        agente.start_step_event.set()
        
        # Opcional: Manter janela aberta no fim
        # viz.root.mainloop()
        try:
            viz.fechar()
        except:
            pass

if __name__ == "__main__":
    testar_farol_visual_rl()
