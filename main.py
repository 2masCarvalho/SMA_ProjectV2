from Motor import MotorDeSimulacao
from visualizador import VisualizadorTk
import time
import tkinter as tk
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


if __name__ == "__main__":

    # Em vez de hardcoded, perguntamos ao utilizador
    caminho_ficheiro = escolher_cenario()
    print(f"-> A carregar: {caminho_ficheiro}\n")

    motor = MotorDeSimulacao.cria(caminho_ficheiro)

    # --- BLOCO DE DIAGNÓSTICO (Para debug inicial) ---
    print(f"Total de agentes criados: {len(motor.agentes)}")
    for i, a in enumerate(motor.agentes):
        print(f"Agente {i}: {a.nome} | Tipo: {type(a).__name__}")
        print(f"   -> Posição: {a.posicao}")
        if hasattr(a, 'cor'):
            print(f"   -> Cor: {a.cor}")
        else:
            print("   -> AVISO: Este agente NÃO tem cor definida!")
    print("-------------------------")
    # ----------------------------
    
    # Inicializar Visualizador
    # Nota: Certifica-te que motor.largura/altura estão disponíveis
    largura = getattr(motor, 'largura', getattr(motor.ambiente, 'largura', 20))
    altura = getattr(motor, 'altura', getattr(motor.ambiente, 'altura', 20))
    viz = VisualizadorTk(largura, altura, tamanho_celula=30)

    print("Iniciando simulação com Visualização...")

    # Aumentei para 500 para dar tempo ao agente de chegar se estiver longe
    MAX_PASSOS = 500 

    try:
        for i in range(MAX_PASSOS):
            # 1. Executar lógica do Motor
            motor.executa()
            
            # --- NOVA VERIFICAÇÃO DE PARAGEM ---
            # Verifica se o objetivo foi cumprido (Farol encontrado ou Labirinto resolvido)
            if motor.ambiente.simulacao_concluida():
                print("\n>>> SUCESSO! Objetivo atingido. A terminar simulação... <<<")
                
                # Desenha o último frame para vermos o agente no alvo
                viz.desenhar(motor.ambiente, motor.agentes)
                viz.root.update()
                
                # Pequena pausa para celebrar a vitória antes de fechar
                time.sleep(2) 
                break
            # -----------------------------------

            # 2. Atualizar Visualização
            try:
                viz.desenhar(motor.ambiente, motor.agentes)
                
                # Atualizar a janela do Tkinter
                viz.root.update_idletasks()
                viz.root.update()
                
            except tk.TclError:
                print("A janela foi fechada pelo utilizador.")
                break
            
            # 3. Pausa para controlar a velocidade da animação
            time.sleep(0.1) # 0.1 é mais fluido, 0.2 é mais lento
            
    except KeyboardInterrupt:
        print("\nInterrompido pelo utilizador (Ctrl+C).")
        
    finally:
        print("\n=== Fim do Teste ===")
        
        # Limpeza segura usando o método que criámos no Motor
        if hasattr(motor, 'parar_agentes'):
            motor.parar_agentes()
        else:
            # Fallback caso o método não exista no Motor
            for a in motor.agentes:
                if hasattr(a, 'running'): a.running = False
                if hasattr(a, 'start_step_event'): a.start_step_event.set()