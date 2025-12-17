import matplotlib.pyplot as plt
import numpy as np
from Motor import MotorDeSimulacao

def media_movel(dados, janela=50):
    """Suaviza o gráfico para não ficar muito 'tremido'."""
    if len(dados) < janela: return dados
    return np.convolve(dados, np.ones(janela)/janela, mode='valid')

def correr_teste(parametro_nome, valores_teste, n_episodios=2000):
    print(f"\n--- A INICIAR ESTUDO DE: {parametro_nome} ---")
    print(f"Valores a testar: {valores_teste}")
    print(f"Episódios por teste: {n_episodios} (Isto vai demorar um pouco...)")
    
    # Dicionário para guardar os resultados de cada valor
    resultados = {} 
    arquivo_cenario = "JSONFILES/labirinto1.json"

    for valor in valores_teste:
        print(f"\n> A testar {parametro_nome} = {valor}...")
        
        historico_passos = []
        
        # 1. Preparação Inicial: Criar motor para aceder ao agente e limpar memória
        motor = MotorDeSimulacao.cria(arquivo_cenario)
        # Encontra o primeiro AgenteRL na lista
        agente_rl_ref = next(a for a in motor.agentes if "AgenteRL" in str(type(a)))
        
        # RESET DA MEMÓRIA (Tabula Rasa) para cada valor testado
        if agente_rl_ref.politica:
            agente_rl_ref.politica.q_table = {} 
            
            # Injetar o valor do parâmetro que queremos testar na referência
            if hasattr(agente_rl_ref.politica, parametro_nome):
                setattr(agente_rl_ref.politica, parametro_nome, valor)

        # 2. Loop de Episódios
        for episodio in range(n_episodios):
            # Reiniciar ambiente e posições para novo episódio
            motor = MotorDeSimulacao.cria(arquivo_cenario)
            agente_ativo = next(a for a in motor.agentes if "AgenteRL" in str(type(a)))
            
            # IMPORTANTE: Passar a memória ("cérebro") da referência para o agente atual
            agente_ativo.politica.q_table = agente_rl_ref.politica.q_table
            
            # Garantir que o parâmetro testado se mantém
            if hasattr(agente_ativo.politica, parametro_nome):
                setattr(agente_ativo.politica, parametro_nome, valor)
            
            # --- CORREÇÃO CRÍTICA PARA O GRÁFICO ---
            # Se NÃO estamos a testar o 'epsilon', forçamos um valor alto (0.6)
            # para garantir que ele explora e encontra a saída.
            if parametro_nome != "epsilon" and hasattr(agente_ativo.politica, 'epsilon'):
                agente_ativo.politica.epsilon = 0.6

            passos = 0
            # AUMENTADO PARA 1000: Dá tempo ao agente de encontrar a saída nas primeiras vezes
            max_passos = 1000 
            
            while passos < max_passos:
                motor.executa()
                passos += 1
                if motor.ambiente.simulacao_concluida():
                    break
            
            # Guardar resultado
            historico_passos.append(passos)
            
            # Atualizar a memória de referência com o que ele aprendeu neste episódio
            agente_rl_ref.politica.q_table = agente_ativo.politica.q_table
            
            # Print de progresso a cada 100 episódios para saberes que não encravou
            if episodio % 500 == 0:
                print(f"   Episódio {episodio}/{n_episodios}...")

        resultados[valor] = historico_passos
        # Mostra a média dos últimos 50 episódios para ver se aprendeu
        media_final = np.mean(historico_passos[-50:])
        print(f"  Concluído. Média final de passos: {media_final:.2f}")

    return resultados

def plotar_grafico(resultados, parametro_nome):
    plt.figure(figsize=(10, 6))
    
    for valor, dados in resultados.items():
        # Aplicar suavização para o gráfico ficar legível
        dados_suaves = media_movel(dados)
        plt.plot(dados_suaves, label=f"{parametro_nome} = {valor}")
    
    plt.title(f'Comparação de Performance: {parametro_nome}')
    plt.xlabel('Episódios')
    plt.ylabel('Passos para chegar ao Objetivo (Média Móvel)')
    plt.legend()
    plt.grid(True)
    nome_arquivo = f"grafico_comparacao_{parametro_nome}.png"
    plt.savefig(nome_arquivo)
    print(f"Gráfico guardado como '{nome_arquivo}'")
    plt.show()

if __name__ == "__main__":
    # --- TESTE 1: Taxa de Aprendizagem (Alpha) ---
    # Recomendado: 2000 episódios para o labirinto
    dados_alpha = correr_teste("alpha", [0.1, 0.5, 0.9], n_episodios=2000)
    plotar_grafico(dados_alpha, "Taxa de Aprendizagem (Alpha)")

    # --- (Opcional) TESTE 2: Gamma ---
    # Se quiseres testar o Gamma, descomenta as linhas abaixo:
    # dados_gamma = correr_teste("gamma", [0.5, 0.9, 0.99], n_episodios=2000)
    # plotar_grafico(dados_gamma, "Fator de Desconto (Gamma)")