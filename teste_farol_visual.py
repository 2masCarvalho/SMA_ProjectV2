import sys
import os
import time
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Motor import MotorDeSimulacao
from visualizador import VisualizadorTk

def teste_cenario_farol_visual():
    print("=== Cenário de Teste Visual: Problema do Farol ===")
    
    # Criar ficheiro JSON de configuração
    config = {
        "tipo": "farol",
        "ambiente": {
            "dimensao": [10, 10],
            "pos_farol": [8, 8],
            "obstaculos": [[5, 5], [2, 2]]
        },
        "agentes": [
            {"nome": "Navegador1", "posicao": [0, 0], "energia": 100},
            #{"nome": "Navegador2", "posicao": [10, 0], "energia": 100},
            #{"nome": "Navegador3", "posicao": [0, 10], "energia": 100}
        ]
    }
    
    json_file = "config_farol_visual.json"
    with open(json_file, "w") as f:
        json.dump(config, f)
    
    # 1. Criar Motor via Factory
    motor = MotorDeSimulacao.cria(json_file)
    
    # 2. Inicializar Visualizador
    largura, altura = config["ambiente"]["dimensao"]
    viz = VisualizadorTk(largura, altura, tamanho_celula=30)
    
    print("Iniciando simulação com Visualização...")
    
    # Executar X passos
    MAX_PASSOS = 100
    import tkinter as tk
    try:
        for i in range(MAX_PASSOS):
            motor.executa()
            
            # Atualizar Visualização
            try:
                viz.desenhar(motor.ambiente, motor.agentes)
            except tk.TclError:
                print("Janela visual fechada.")
                break
            
            time.sleep(0.2) # Pausa para animação
            
    except KeyboardInterrupt:
        print("Interrompido pelo utilizador.")
    finally:
        print("\n=== Fim do Teste ===")
        # Parar threads
        for a in motor.agentes:
            a.running = False
            a.start_step_event.set()
        
        # Limpeza
        if os.path.exists(json_file):
            os.remove(json_file)
            
        # Manter janela aberta por uns segundos ou fechar
        # viz.fechar() 
        # viz.root.mainloop() # Se quiséssemos manter aberta

if __name__ == "__main__":
    teste_cenario_farol_visual()
