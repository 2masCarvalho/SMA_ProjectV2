import time
import os
from Motor import MotorDeSimulacao
import sys

# Configuração dos Cenários Disponíveis
CENARIOS = {
    "1": "JSONFILES/farol1copy.json",
    "2": "JSONFILES/labirinto1.json"
}

def escolher_cenario():
    print("\n=== ESCOLHA O CENÁRIO ===")
    print("1. Farol (Básico)")
    print("2. Labirinto (Zig-Zag)")
    
    escolha = input("Opção (1 ou 2): ").strip()
    
    # Retorna o caminho ou o Farol por defeito se falhar
    return CENARIOS.get(escolha, CENARIOS["1"])

def treinar_agente(n_episodios=1000):
    # 1. Perguntar qual o cenário
    ficheiro_cenario = escolher_cenario()
    
    print(f"--- A INICIAR TREINO NO CENÁRIO: {ficheiro_cenario} ---")
    start_time = time.time()

    # Caminho do ficheiro de configuração
    ficheiro_cenario = "JSONFILES/farol1copy.json"

    for i in range(1, n_episodios + 1):
        # 1. Criar o motor (isto reinicia o ambiente e carrega o agente)
        # O AgenteRL vai carregar automaticamente o .pkl existente e continuar a aprender
        motor = MotorDeSimulacao.cria(ficheiro_cenario)
        
        # 2. Executar até ao fim (sem visualizador)
        # Precisamos de um ciclo que faça o motor andar passo a passo até acabar
        # Como o teu motor.executa() faz apenas um passo, fazemos um loop:
        passos = 0
        max_passos = 200 # Limite para ele não ficar preso em loop infinito
        
        while passos < max_passos:
            motor.executa()
            passos += 1
            
            # Critério de paragem: Precisas de saber se o agente chegou
            # Podes verificar a recompensa do agente ou se a distância é 0
            # Para simplificar, assumimos que ele corre max_passos e aprende com isso
        
        # 3. Importante: Forçar o agente a salvar o cérebro no final do episódio
        for agente in motor.agentes:
            if hasattr(agente, "stop"):
                agente.stop() # Isto chama o método salvar() que criámos antes

        if i % 100 == 0:
            print(f"Episódio {i}/{n_episodios} concluído...")

    total_time = time.time() - start_time
    print(f"--- TREINO CONCLUÍDO EM {total_time:.2f} SEGUNDOS ---")
    print("Agora podes correr o 'main.py' para ver o resultado!")

if __name__ == "__main__":
    treinar_agente(500) # Tenta 500 episódios para começar