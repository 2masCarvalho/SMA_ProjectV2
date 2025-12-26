import json
import os
from AmbienteLabirinto import AmbienteLabirinto
from AgenteLabirinto import AgenteLabirinto
from Sensor import SensorDirecao, SensorProximidade
from Motor import MotorDeSimulacao

def treinar_labirinto():
    print("=== Iniciando Treino: Problema do Labirinto ===")
    
    # 1. Carregar Configurações do Mapa
    with open("JSONFILES/labirinto1.json", "r") as f:
        config = json.load(f)
    
    amb_cfg = config["ambiente"]
    ambiente = AmbienteLabirinto(
        pos_saida=tuple(amb_cfg["pos_saida"]),
        dimensoes=tuple(amb_cfg["dimensao"]),
        obstaculos=[tuple(o) for o in amb_cfg["obstaculos"]]
    )
    
    # 2. Configurar o Agente Especializado
    agente_cfg = config["agentes"][0]
    agente = AgenteLabirinto(
        nome=agente_cfg["nome"],
        posicao=tuple(agente_cfg["posicao"]),
        ficheiro_config=agente_cfg["ficheiro_config"]
    )
    
    # Instalar os dois sensores fundamentais para o labirinto
    agente.instala(SensorDirecao())
    agente.instala(SensorProximidade())
    
    motor = MotorDeSimulacao(ambiente, [agente])
    
    # 3. Parâmetros de Treino
    EPISODIOS = 1000  # Labirintos exigem mais episódios que o farol
    MAX_PASSOS = 200  # Limite de passos para o agente não ficar perdido para sempre
    Q_TABLE_FILE = "qtable_labirinto.pkl"
    
    print(f"Treinando por {EPISODIOS} episódios...")
    
    for ep in range(EPISODIOS):
        # Reset do ambiente para o início do labirinto
        ambiente.adicionar_agente(agente, tuple(agente_cfg["posicao"]))
        ambiente._alvo_atingido = False
        agente.passos = 0
        
        # Estratégia de Exploração (Epsilon-Greedy Decay)
        # Começa em 0.6 (muita exploração) e desce até 0.1 (mais decisão)
        if agente.politica:
            agente.politica.epsilon = max(0.1, 0.6 * (0.996 ** ep))
        
        for passo in range(MAX_PASSOS):
            motor.executa()
            if ambiente.simulacao_concluida():
                break
        
        # Feedback de progresso e salvamento periódico
        if (ep + 1) % 100 == 0:
            print(f"Episódio {ep+1}/{EPISODIOS} | Epsilon: {agente.politica.epsilon:.2f}")
            agente.politica.salvar(Q_TABLE_FILE)

    print(f"\nTreino concluído! Memória guardada em: {Q_TABLE_FILE}")

if __name__ == "__main__":
    treinar_labirinto()
