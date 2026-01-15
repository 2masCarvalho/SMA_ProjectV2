import time
import os
import sys
import csv
import math
from Motor import MotorDeSimulacao

epsilon_inicial = 1.0
epsilon_final = 0.01
decay_rate = 0.005

CENARIOS = {
    "1": {
        "caminho": "JSONFILES/farol1copy.json", 
        "nome_memoria": "Qlearning/memoria_cenario_1_farol.pkl"
    },
    "2": {
        "caminho": "JSONFILES/labirinto2.json", 
        "nome_memoria": "Qlearning/memoria_cenario_2_zigzag.pkl"
    },
    "3": {
        "caminho": "JSONFILES/labirinto3.json", 
        "nome_memoria": "Qlearning/memoria_cenario_3_novo.pkl"
    },
    "4": {
        "caminho": "JSONFILES/labirinto4.json", 
        "nome_memoria": "Qlearning/memoria_cenario_4_hardcore.pkl"
    },
    "5": {
        "caminho": "JSONFILES/labirinto5.json", 
        "nome_memoria": "Qlearning/memoria_cenario_5_mini.pkl"
    }
}

def escolher_cenario():
    print("\n=== MODO DE TREINO SUPER-RÁPIDO (OTIMIZADO) ===")
    print("1. Farol (Básico)")
    print("2. Labirinto (Zig-Zag)")
    print("3. Labirinto (Novo Teste)")
    print("4. Labirinto (Hardcore Snake)")
    print("5. Labirinto (Mini Snake 8x8)")
    escolha = input("Escolha o cenário (1-5): ").strip()
    return CENARIOS.get(escolha, CENARIOS["1"])

def treinar_agente(n_episodios=1000):
    config = escolher_cenario()
    ficheiro_cenario = config["caminho"]
    ficheiro_memoria = config["nome_memoria"]
    
    print(f"\n--- A INICIAR TREINO ---")
    print(f"Cenário: {ficheiro_cenario}")
    print(f"Memória alvo: {ficheiro_memoria}")
    
    start_time = time.time()

    motor = MotorDeSimulacao.cria(ficheiro_cenario)

    log_filename = f"logs_treino_{config['nome_memoria'].split('/')[-1].replace('.pkl', '.csv')}"
    
    with open(log_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Episodio", "Passos", "RecompensaTotal", "Sucesso", "Epsilon"])

    dados_buffer = []

    print("-> A configurar agentes...")
    for agente in motor.agentes:
        if hasattr(agente, 'ficheiro_memoria') and hasattr(agente, 'politica'):
            agente.ficheiro_memoria = ficheiro_memoria
            
            if hasattr(agente, 'learning_mode'):
                agente.learning_mode = True
                print(f"   [{agente.nome}] Modo de Aprendizagem: LIGADO")
            
            if os.path.exists(ficheiro_memoria):
                try:
                    agente.politica.carregar(ficheiro_memoria)
                    print(f"   [{agente.nome}] Memória carregada: {ficheiro_memoria}")
                except Exception as e:
                    print(f"   [{agente.nome}] ERRO ao carregar memória: {e}")
                    print(f"   [{agente.nome}] Criando nova memória do zero.")
            else:
                 print(f"   [{agente.nome}] Iniciando treino do zero em: {ficheiro_memoria}")

    for i in range(1, n_episodios + 1):
        
        novo_epsilon = epsilon_final + (epsilon_inicial - epsilon_final) * math.exp(-decay_rate * i)

        for agente in motor.agentes:
            if hasattr(agente, 'set_epsilon'):
                agente.set_epsilon(novo_epsilon)
        
        if hasattr(motor.ambiente, 'reset'):
            motor.ambiente.reset()
        
        for agente in motor.agentes:
            if hasattr(agente, 'reset_estado'):
                agente.reset_estado()

        passos = 0
        max_passos = 200 
        sucesso = 0
        
        while passos < max_passos:
            motor.executa()
            passos += 1
            
            if motor.ambiente.simulacao_concluida():
                sucesso = 1
                break
        
        recompensa_total_episodio = sum([a.recompensa_total for a in motor.agentes])
        for a in motor.agentes: a.recompensa_total = 0.0

        dados_buffer.append([i, passos, recompensa_total_episodio, sucesso, f"{novo_epsilon:.4f}"])

        if i % 100 == 0 or i == n_episodios:
            print(f"Episódio {i}/{n_episodios} | Epsilon: {novo_epsilon:.3f} | Rec: {recompensa_total_episodio:.1f} (A salvar...)")
            
            for agente in motor.agentes:
                if hasattr(agente, "politica") and hasattr(agente.politica, "salvar"):
                    agente.politica.salvar(agente.ficheiro_memoria)
            
            if dados_buffer:
                with open(log_filename, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(dados_buffer)
                dados_buffer = []

    if dados_buffer:
        with open(log_filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(dados_buffer)

    total_time = time.time() - start_time
    print(f"\n--- TREINO CONCLUÍDO EM {total_time:.2f} SEGUNDOS ---")
    
    for agente in motor.agentes:
        agente.running = False          
        agente.start_step_event.set()   
        agente.join()                   
    
    print("Agora podes correr o 'main.py' para ver o resultado!")
    sys.exit(0)

if __name__ == "__main__":
    treinar_agente(n_episodios=1000)