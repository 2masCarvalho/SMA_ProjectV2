import time
import os
import sys
from Motor import MotorDeSimulacao

# ==================================================================================
# CONFIGURAÇÃO: Associa cada cenário a um ficheiro de memória específico
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
    print("\n=== MODO DE TREINO SUPER-RÁPIDO (SEM VISUALIZADOR) ===")
    print("1. Farol (Básico)")
    print("2. Labirinto (Zig-Zag)")
    print("3. Labirinto (Novo Teste)")
    print("4. Labirinto (Hardcore Snake)")
    print("5. Labirinto (Mini Snake 8x8)")
    escolha = input("Escolha o cenário (1-5): ").strip()
    return CENARIOS.get(escolha, CENARIOS["1"])

def treinar_agente(n_episodios=1000):
    # 1. Escolher Cenário
    config = escolher_cenario()
    ficheiro_cenario = config["caminho"]
    ficheiro_memoria = config["nome_memoria"]
    
    print(f"\n--- A INICIAR TREINO ---")
    print(f"Cenário: {ficheiro_cenario}")
    print(f"Memória alvo: {ficheiro_memoria}")
    
    start_time = time.time()

    # 2. Criar o motor (UMA VEZ SÓ para ser rápido)
    motor = MotorDeSimulacao.cria(ficheiro_cenario)

    # 3. OVERRIDE DA MEMÓRIA: Configurar os agentes para usar o ficheiro correto
    print("-> A configurar agentes...")
    for agente in motor.agentes:
        if hasattr(agente, 'ficheiro_memoria') and hasattr(agente, 'politica'):
            # Define o nome do ficheiro específico para este cenário
            agente.ficheiro_memoria = ficheiro_memoria
            
            # Tenta carregar memória existente (para continuar treino anterior)
            if os.path.exists(ficheiro_memoria):
                try:
                    agente.politica.carregar(ficheiro_memoria)
                    print(f"   [{agente.nome}] Memória carregada: {ficheiro_memoria}")
                except:
                    print(f"   [{agente.nome}] Criando nova memória em: {ficheiro_memoria}")
            else:
                 print(f"   [{agente.nome}] Iniciando treino do zero em: {ficheiro_memoria}")

    # 4. CICLO DE EPISÓDIOS
    for i in range(1, n_episodios + 1):
        
        # A. Reset do Ambiente e Agentes (essencial porque não recriamos o motor)
        if hasattr(motor.ambiente, 'reset'):
            motor.ambiente.reset()
        
        for agente in motor.agentes:
            if hasattr(agente, 'reset_estado'):
                agente.reset_estado()

        # B. Executar Episódio
        passos = 0
        max_passos = 200 # Limite para evitar loops infinitos
        
        while passos < max_passos:
            motor.executa()
            passos += 1
            
            if motor.ambiente.simulacao_concluida():
                # Se chegou ao objetivo, o AgenteRL já recebeu a recompensa grande internamente
                break
        
        # C. Guardar periodicamente e no último episódio
        if i % 100 == 0 or i == n_episodios:
            print(f"Episódio {i}/{n_episodios} concluído... (A salvar progresso)")
            for agente in motor.agentes:
                if hasattr(agente, "politica") and hasattr(agente.politica, "salvar"):
                    agente.politica.salvar(agente.ficheiro_memoria)

    total_time = time.time() - start_time
    print(f"\n--- TREINO CONCLUÍDO EM {total_time:.2f} SEGUNDOS ---")
    print(f"Memória guardada em: {ficheiro_memoria}")
    for agente in motor.agentes:
        agente.running = False          # Diz ao agente para parar o loop
        agente.start_step_event.set()   # "Acorda" o agente caso ele esteja à espera
        agente.join()                   # Espera que ele feche de vez
    
    print("Agora podes correr o 'main.py' para ver o resultado!")
    sys.exit(0) # Força o fecho do programa

if __name__ == "__main__":
    # Podes ajustar o número de episódios aqui
    treinar_agente(n_episodios=1000)