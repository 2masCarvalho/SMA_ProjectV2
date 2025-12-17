from Motor import MotorDeSimulacao
from visualizador import VisualizadorTk
import time
import tkinter as tk

if __name__ == "__main__":
    # 1. Definir o nome do ficheiro numa variável (boa prática)
    caminho_ficheiro = "JSONFILES/farol1copy.json"
    
    motor = MotorDeSimulacao.cria(caminho_ficheiro)

    #--- BLOCO DE DIAGNÓSTICO ---
    print(f"Total de agentes criados: {len(motor.agentes)}")
    for i, a in enumerate(motor.agentes):
        print(f"Agente {i}: {a.nome} | Tipo: {type(a).__name__}")
        print(f"   -> Posição: {a.posicao} (Tipo: {type(a.posicao)})")
        # Verifica se tem cor (o visualizador costuma precisar disto)
        if hasattr(a, 'cor'):
            print(f"   -> Cor: {a.cor}")
        else:
            print("   -> AVISO: Este agente NÃO tem cor definida!")
    print("-------------------------")
    # ----------------------------
    
    #print(f"Dimensões: {motor.largura} x {motor.altura}")
    viz = VisualizadorTk(motor.largura, motor.altura, tamanho_celula=30)

    print("Iniciando simulação com Visualização...")

    MAX_PASSOS = 100

    try:
        for i in range(MAX_PASSOS):
            # 1. Executar lógica
            motor.executa()
            
            # 2. Atualizar Visualização
            try:
                # Nota: Verifica se o método no teu visualizador é 'desenhar' 
                # ou se tens de chamar métodos separados como 'limpar_agentes' e 'desenhar_agentes'
                viz.desenhar(motor.ambiente, motor.agentes)
                
                # É essencial atualizar a janela do Tkinter aqui
                viz.root.update_idletasks()
                viz.root.update()
                
            except tk.TclError:
                print("A janela foi fechada pelo utilizador.")
                break
            
            # 3. Pausa
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("Interrompido pelo utilizador (Ctrl+C).")
        
    finally:
        print("\n=== Fim do Teste ===")
        
        # Parar threads dos agentes (Limpeza segura)
        #Garanto que o programa fecha corretamente.
        for a in motor.agentes:
            if hasattr(a, 'running'): # Verifica se o agente tem esta flag
                a.running = False
            if hasattr(a, 'start_step_event'):
                a.start_step_event.set() # Liberta o agente se estiver preso num wait()