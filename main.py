from Motor import MotorDeSimulacao
from visualizador import VisualizadorTk
import time
import tkinter as tk
import sys
import os

# CONFIGURAÇÃO IGUAL AO TREINAR.PY (Para lerem os mesmos ficheiros)
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
    print("\n=== VISUALIZAÇÃO (TESTE DO AGENTE TREINADO) ===")
    print("1. Farol (Básico)")
    print("2. Labirinto (Zig-Zag)")
    print("3. Labirinto (Novo Teste)")
    print("4. Labirinto (Hardcore Snake)")
    print("5. Labirinto (Mini Snake 8x8)")
    
    escolha = input("Opção (1-5): ").strip()
    return CENARIOS.get(escolha, CENARIOS["1"])

if __name__ == "__main__":

    # 1. Escolher Cenário
    config_cenario = escolher_cenario()
    caminho_ficheiro = config_cenario["caminho"]
    nome_memoria_alvo = config_cenario["nome_memoria"]
    
    print(f"-> A carregar cenário: {caminho_ficheiro}")
    print(f"-> A procurar memória treinada: {nome_memoria_alvo}\n")

    motor = MotorDeSimulacao.cria(caminho_ficheiro)

    # 2. INJETAR A MEMÓRIA CORRETA (IGUAL AO TREINO)
    memoria_encontrada = False
    for agente in motor.agentes:
        if hasattr(agente, 'ficheiro_memoria') and hasattr(agente, 'politica'):
            # Força o agente a usar o ficheiro específico deste cenário
            # Força o agente a usar o ficheiro específico deste cenário
            agente.ficheiro_memoria = nome_memoria_alvo
            
            # --- MODO TESTE ATIVADO ---
            # Desliga a aprendizagem para vermos apenas o que ele já sabe
            if hasattr(agente, 'learning_mode'):
                agente.learning_mode = False
                print(f"   [{agente.nome}] Modo de Aprendizagem: DESLIGADO (Teste Puro)")
            
            # Tenta carregar
            if os.path.exists(nome_memoria_alvo):
                agente.politica.carregar(nome_memoria_alvo)
                print(f"   [{agente.nome}] SUCESSO: Memória '{nome_memoria_alvo}' carregada.")
                memoria_encontrada = True
            else:
                print(f"   [{agente.nome}] AVISO: Ficheiro '{nome_memoria_alvo}' não existe.")
                print("             O agente vai comportar-se como 'burro' (aleatório).")
                print("             Executa primeiro o 'treinar.py' para este cenário!")

    if not memoria_encontrada:
        print("\n--- ATENÇÃO: Nenhum cérebro treinado foi encontrado. ---")
        input("Pressiona ENTER para continuar mesmo assim (ou Ctrl+C para sair)...")

    # 3. Visualização Normal
    largura = getattr(motor, 'largura', getattr(motor.ambiente, 'largura', 20))
    altura = getattr(motor, 'altura', getattr(motor.ambiente, 'altura', 20))
    viz = VisualizadorTk(largura, altura, tamanho_celula=30)

    print("\nIniciando simulação...")
    MAX_PASSOS = 1000 

    try:
        passos = 0
        for i in range(MAX_PASSOS):
            motor.executa()
            passos += 1
            
            # DEBUG: Imprimir posição do primeiro agente
            if motor.agentes:
                print(f"Passo {passos}: Pos {motor.agentes[0].posicao}")
            
            if motor.ambiente.simulacao_concluida():
                print(f"\n>>> SUCESSO! Objetivo atingido em {passos} passos. <<<")
                viz.desenhar(motor.ambiente, motor.agentes)
                viz.root.update()
                time.sleep(3) 
                break

            try:
                viz.desenhar(motor.ambiente, motor.agentes)
                viz.root.update_idletasks()
                viz.root.update()
            except tk.TclError:
                break
            
            # Velocidade de visualização (ajusta a gosto)
            time.sleep(0.1) 
            
    except KeyboardInterrupt:
        print("\nInterrompido.")
        
    finally:
        print("Fim.")
        if hasattr(motor, 'parar_agentes'):
            motor.parar_agentes()
        else:
            for a in motor.agentes:
                if hasattr(a, 'running'): a.running = False
                if hasattr(a, 'start_step_event'): a.start_step_event.set()