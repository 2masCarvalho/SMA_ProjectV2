import time
import os
import sys
import csv
import math
from Motor import MotorDeSimulacao

# ==================================================================================
# PARÂMETROS DE APRENDIZAGEM
# ==================================================================================
epsilon_inicial = 1.0   # 100% aleatório no início
epsilon_final = 0.01    # 1% aleatório no fim
decay_rate = 0.005      # Velocidade de decaimento da exploração

# ==================================================================================
# CONFIGURAÇÃO DE CENÁRIOS
# ==================================================================================
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

def treinar_agente(n_episodios=2000):
    # 1. Escolher Cenário
    config = escolher_cenario()
    ficheiro_cenario = config["caminho"]
    ficheiro_memoria = config["nome_memoria"]
    
    print(f"\n--- A INICIAR TREINO ---")
    print(f"Cenário: {ficheiro_cenario}")
    print(f"Memória alvo: {ficheiro_memoria}")
    
    start_time = time.time()

    # 2. Criar o motor 
    motor = MotorDeSimulacao.cria(ficheiro_cenario)

    # Preparar ficheiro de Log
    log_filename = f"logs_treino_{config['nome_memoria'].split('/')[-1].replace('.pkl', '.csv')}"
    
    # Cria o cabeçalho do CSV
    with open(log_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Adicionei 'Sucesso' para saberes se ele completou o nível ou não
        writer.writerow(["Episodio", "Passos", "RecompensaTotal", "Sucesso", "Epsilon"])

    # Buffer para guardar dados em memória antes de escrever no disco (Performance I/O)
    dados_buffer = []

    # 3. CONFIGURAR AGENTES
    print("-> A configurar agentes...")
    for agente in motor.agentes:
        if hasattr(agente, 'ficheiro_memoria') and hasattr(agente, 'politica'):
            agente.ficheiro_memoria = ficheiro_memoria
            
            if hasattr(agente, 'learning_mode'):
                agente.learning_mode = True
                print(f"   [{agente.nome}] Modo de Aprendizagem: LIGADO")
            
            # Tratamento de erros melhorado para carregamento
            if os.path.exists(ficheiro_memoria):
                try:
                    agente.politica.carregar(ficheiro_memoria)
                    print(f"   [{agente.nome}] Memória carregada: {ficheiro_memoria}")
                except Exception as e:
                    print(f"   [{agente.nome}] ERRO ao carregar memória: {e}")
                    print(f"   [{agente.nome}] Criando nova memória do zero.")
            else:
                 print(f"   [{agente.nome}] Iniciando treino do zero em: {ficheiro_memoria}")

    # 4. CICLO DE EPISÓDIOS
    for i in range(1, n_episodios + 1):
        
        # A. Cálculo do Epsilon (Decaimento Exponencial)
        novo_epsilon = epsilon_final + (epsilon_inicial - epsilon_final) * math.exp(-decay_rate * i)

        # Atualizar epsilon em todos os agentes
        for agente in motor.agentes:
            if hasattr(agente, 'set_epsilon'):
                agente.set_epsilon(novo_epsilon)
        
        # B. Reset do Ambiente e Agentes
        if hasattr(motor.ambiente, 'reset'):
            motor.ambiente.reset()
        
        for agente in motor.agentes:
            if hasattr(agente, 'reset_estado'):
                agente.reset_estado()

        # C. Executar Episódio
        passos = 0
        max_passos = 200 
        sucesso = 0 # 0 = Falhou/Tempo Esgotado, 1 = Sucesso
        
        while passos < max_passos:
            motor.executa()
            passos += 1
            
            if motor.ambiente.simulacao_concluida():
                sucesso = 1
                break
        
        # D. Recolha de Métricas
        recompensa_total_episodio = sum([a.recompensa_total for a in motor.agentes])
        # Reset recompensa acumulada nos agentes
        for a in motor.agentes: a.recompensa_total = 0.0

        # Adicionar ao Buffer (MUITO MAIS RÁPIDO DO QUE ABRIR O FICHEIRO AGORA)
        dados_buffer.append([i, passos, recompensa_total_episodio, sucesso, f"{novo_epsilon:.4f}"])

        # E. Guardar periodicamente (Checkpoint e Flush do Buffer)
        if i % 100 == 0 or i == n_episodios:
            print(f"Episódio {i}/{n_episodios} | Epsilon: {novo_epsilon:.3f} | Rec: {recompensa_total_episodio:.1f} (A salvar...)")
            
            # 1. Salvar memória dos agentes
            for agente in motor.agentes:
                if hasattr(agente, "politica") and hasattr(agente.politica, "salvar"):
                    agente.politica.salvar(agente.ficheiro_memoria)
            
            # 2. Despejar o buffer no CSV (Write Batch)
            if dados_buffer:
                with open(log_filename, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(dados_buffer)
                dados_buffer = [] # Limpar buffer após escrita

    # F. Escrita final (caso sobrem dados no buffer)
    if dados_buffer:
        with open(log_filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(dados_buffer)

    total_time = time.time() - start_time
    print(f"\n--- TREINO CONCLUÍDO EM {total_time:.2f} SEGUNDOS ---")
    
    # Encerramento seguro das threads
    for agente in motor.agentes:
        agente.running = False          
        agente.start_step_event.set()   
        agente.join()                   
    
    print("Agora podes correr o 'main.py' para ver o resultado!")
    sys.exit(0)

if __name__ == "__main__":
    treinar_agente(n_episodios=1000)