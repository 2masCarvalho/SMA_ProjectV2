import sys
import os
import time
import random

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from AmbienteFarol import AmbienteFarol
from AgenteRL import AgenteRL
from Politica import PoliticaQLearning
from Motor import MotorDeSimulacao

from Sensor import SensorDirecao, SensorVisao

def treinar_farol():
    print("=== Treino: Problema do Farol (Q-Learning) ===")
    
    # Parâmetros de Treino
    NUM_EPISODIOS = 100
    MAX_PASSOS_POR_EPISODIO = 50
    Q_TABLE_FILE = "qtable_farol.pkl"
    
    # 1. Configurar Política
    accoes_possiveis = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)] # 8 direções
    politica = PoliticaQLearning(accoes_possiveis, alpha=0.1, gamma=0.9, epsilon=0.1)
    
    # Carregar política existente se houver (para continuar treino)
    if os.path.exists(Q_TABLE_FILE):
        politica.carregar(Q_TABLE_FILE)

    for episodio in range(NUM_EPISODIOS):
        # 2. Configurar Ambiente e Agente para este episódio
        # Resetar posições
        pos_inicial_agente = (0, 0)
        ambiente = AmbienteFarol(
            farol_pos=(8, 8), 
            dimensoes=(10, 10),
            obstaculos=[(5, 5), (2, 2)]
        )
        
        agente = AgenteRL("AgenteAprendiz", politica)
        
        # Instalar sensores para consistência com o teste
        sensor_bussola = SensorDirecao()
        sensor_visao = SensorVisao(raio_visao=1.5)
        agente.instala(sensor_visao)
        agente.instala(sensor_bussola)
        
        ambiente.adicionar_agente(agente, pos_inicial_agente)
        
        motor = MotorDeSimulacao(ambiente, [agente])
        
        # Reduzir epsilon ao longo do tempo (Exploration Decay)
        politica.epsilon = max(0.01, politica.epsilon * 0.99)
        
        # Loop do Episódio
        passos = 0
        chegou = False
        while passos < MAX_PASSOS_POR_EPISODIO:
            motor.executa()
            passos += 1
            
            # Verificar se chegou (distancia < 1.0)
            obs = ambiente.observacaoPara(agente)
            if obs.dados['distancia'] < 1.0:
                chegou = True
                break
        
        # Feedback
        if (episodio + 1) % 10 == 0:
            print(f"Episódio {episodio+1}/{NUM_EPISODIOS} - Passos: {passos} - Recompensa Total: {agente.recompensa_total:.2f} - Epsilon: {politica.epsilon:.4f}")

        # Parar thread do agente deste episódio
        agente.running = False
        agente.start_step_event.set()
        agente.join() # Esperar que a thread termine

    print("\n=== Treino Concluído ===")
    politica.salvar(Q_TABLE_FILE)

if __name__ == "__main__":
    treinar_farol()
