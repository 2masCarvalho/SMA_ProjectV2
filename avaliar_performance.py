import time
import sys
import os
import statistics
from Motor import MotorDeSimulacao

# ================= CONFIGURAÇÕES DE TESTE =================
NUM_EPISODIOS = 100      # Quantos testes queres correr para tirar a média?
MAX_PASSOS = 1000        # Limite de passos para considerar que o agente falhou
# ==========================================================

# CONFIGURAÇÃO DOS CENÁRIOS (Igual ao teu ficheiro visual)
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
    print("\n=== AVALIAÇÃO DE PERFORMANCE (MODO ESTATÍSTICO) ===")
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
    
    print(f"\n-> A carregar cenário: {caminho_ficheiro}")
    print(f"-> A testar memória: {nome_memoria_alvo}")
    print(f"-> Executando {NUM_EPISODIOS} episódios sem pausa visual...\n")

    # Criar o motor
    motor = MotorDeSimulacao.cria(caminho_ficheiro)

    # 2. CONFIGURAR AGENTES (Carregar Memória e Desligar Aprendizagem)
    memoria_encontrada = False
    for agente in motor.agentes:
        if hasattr(agente, 'politica'):
            # Força o caminho correto da memória
            agente.ficheiro_memoria = nome_memoria_alvo
            
            # --- MODO TESTE (IMPORTANTE) ---
            if hasattr(agente, 'learning_mode'):
                agente.learning_mode = False # Desliga a exploração (Epsilon = 0) e updates
            
            # Carregar Q-Table
            if os.path.exists(nome_memoria_alvo):
                agente.politica.carregar(nome_memoria_alvo)
                memoria_encontrada = True
            else:
                print(f"   [AVISO] Memória '{nome_memoria_alvo}' não encontrada para {agente.nome}.")

    if not memoria_encontrada:
        print("\n--- ATENÇÃO: Nenhum cérebro treinado foi carregado. O teste será aleatório. ---")
        time.sleep(2)

    # 3. LOOP DE AVALIAÇÃO
    sucessos = 0
    lista_passos = []
    start_time_total = time.time()

    print(f"Iniciando bateria de {NUM_EPISODIOS} testes...")
    
    try:
        for ep in range(1, NUM_EPISODIOS + 1):
            # Resetar o ambiente para o estado inicial (posição inicial, limpar flags)
            motor.ambiente.reset()
            
            passos_episodio = 0
            concluido = False
            
            # Loop do Episódio Individual
            for _ in range(MAX_PASSOS):
                motor.executa()
                passos_episodio += 1
                
                if motor.ambiente.simulacao_concluida():
                    concluido = True
                    break
            
            # Registar dados
            if concluido:
                sucessos += 1
                lista_passos.append(passos_episodio)
            
            # Barra de progresso simples (imprime a cada 10%)
            if ep % (NUM_EPISODIOS // 10) == 0:
                print(f" > Progresso: {ep}/{NUM_EPISODIOS} episódios concluídos.")

    except KeyboardInterrupt:
        print("\nAvaliação interrompida pelo utilizador.")
        
    finally:
        # 4. CALCULAR E APRESENTAR ESTATÍSTICAS
        total_tempo = time.time() - start_time_total
        taxa_sucesso = (sucessos / NUM_EPISODIOS) * 100
        
        media_passos = statistics.mean(lista_passos) if lista_passos else 0
        desvio_padrao = statistics.stdev(lista_passos) if len(lista_passos) > 1 else 0
        melhor_caso = min(lista_passos) if lista_passos else 0
        pior_caso = max(lista_passos) if lista_passos else 0

        print("\n" + "="*50)
        print(f" RELATÓRIO DE PERFORMANCE: {caminho_ficheiro}")
        print("="*50)
        print(f" Agente treinado:    {'SIM' if memoria_encontrada else 'NÃO (Aleatório)'}")
        print(f" Memória usada:      {nome_memoria_alvo}")
        print("-" * 50)
        print(f" Total Episódios:    {NUM_EPISODIOS}")
        print(f" TAXA DE SUCESSO:    {taxa_sucesso:.2f}%")
        print("-" * 50)
        
        if sucessos > 0:
            print(f" Passos Médios:      {media_passos:.2f}")
            print(f" Desvio Padrão:      {desvio_padrao:.2f}")
            print(f" Melhor volta:       {melhor_caso} passos")
            print(f" Pior volta:         {pior_caso} passos")
        else:
            print(" (O agente nunca atingiu o objetivo dentro do limite de passos)")
            
        print("-" * 50)
        print(f" Tempo computacional: {total_tempo:.4f} segundos")
        print("="*50)

        # Parar threads se existirem
        if hasattr(motor, 'parar_agentes'):
            motor.parar_agentes()
        else:
            # Fallback para parar threads manuais
            for a in motor.agentes:
                if hasattr(a, 'end_step_event'): a.end_step_event.set()
                if hasattr(a, 'start_step_event'): a.start_step_event.set()