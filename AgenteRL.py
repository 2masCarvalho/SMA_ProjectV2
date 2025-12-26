import json
from Agente import Agente
from Modelos import Accao, Observacao
from Politica import PoliticaQLearning
from Sensor import SensorDirecao, SensorProximidade

class AgenteRL(Agente):
    def __init__(self, nome: str, posicao: tuple, ficheiro_config: str):
        super().__init__(nome)
        self.cor = "red"
        self.posicao = posicao 
        
        # --- CORREÇÃO DO ERRO DE CAMINHO ---
        # Removemos as barras do início ('/' ou '\') para garantir que 
        # o Python procura na pasta do projeto e não na raiz do PC.
        caminho_limpo = ficheiro_config.lstrip('/').lstrip('\\')
        
        self.ficheiro_config = caminho_limpo
        # Agora o ficheiro de memória também fica com o caminho correto
        self.ficheiro_memoria = caminho_limpo.replace(".json", ".pkl")
        
        # Carregar política usando o caminho limpo
        self.politica = self._criar_politica_do_ficheiro(self.ficheiro_config)
        
        # Tentar carregar memória existente
        if self.politica:
            self.politica.carregar(self.ficheiro_memoria)
    # --- MÉTODOS PRIVADOS ---
    def _criar_politica_do_ficheiro(self, caminho: str):
        try:
            caminho_limpo = caminho.lstrip('/') if caminho.startswith('/') else caminho
            with open(caminho_limpo, 'r') as f:
                params = json.load(f)
            
            accoes = params.get("accoes", ["norte", "sul", "este", "oeste", 
                                          "nordeste", "sudeste", "sudoeste", "noroeste"])
            
            return PoliticaQLearning(
                accoes_possiveis=accoes,
                alpha=params.get("alpha", 0.1),
                gamma=params.get("gamma", 0.9),
                epsilon=params.get("epsilon", 0.1)
            )
        except Exception as e:
            print(f"ERRO: {e}")
            return None 

    def _vetor_para_cardinal(self, dx, dy):
        if dx == 0 and dy == 0: return "parado"
        limiar = 0.3
        v, h = "", ""
        if dy < -limiar: v = "norte"
        elif dy > limiar: v = "sul"
        if dx > limiar: h = "este"
        elif dx < -limiar: h = "oeste"
        
        mapa = {
            ("norte", "este"): "nordeste", ("norte", "oeste"): "noroeste",
            ("sul", "este"): "sudeste", ("sul", "oeste"): "sudoeste"
        }
        return mapa.get((v, h), v or h)

    # ==========================================================
    # IMPLEMENTAÇÃO OBRIGATÓRIA (NOMES CORRIGIDOS)
    # ==========================================================

    def instala(self, sensor):
        super().instala(sensor)

    def observacao(self, obs: Observacao):
        super().observacao(obs)

    # CORREÇÃO 1: Nome exato igual à classe mãe (snake_case)
    def avaliacao_estado_atual(self, recompensa: float):
        super().avaliacao_estado_atual(recompensa)
        
        if self.politica:
            self.politica.atualizar(recompensa)
            if self.passos % 100 == 0:
                self.politica.salvar(self.ficheiro_memoria)

    # CORREÇÃO 2: Adicionado o método comunica que estava em falta
    def comunica(self, mensagem: str, de_agente):
        pass

    def age(self) -> Accao:
        # 1. Construir o Estado
        direcao_farol = "desconhecida"
        obstaculos_perto = tuple([0]*8)

        # DEBUG: Verificar se tem sensores
        if not self.sensores:
            print(f"[ALERTA] {self.nome} NÃO TEM SENSORES INSTALADOS!")

        for s in self.sensores:
            if isinstance(s, SensorDirecao):
                obs = s.detetar(self.ambiente, self)
                d = obs.dados.get("direcao", (0,0))
                direcao_farol = self._vetor_para_cardinal(d[0], d[1])
            elif isinstance(s, SensorProximidade):
                obs = s.detetar(self.ambiente, self)
                dados_prox = obs.dados.get("proximidade_obstaculos", {})
                chaves_ordem = [
                    (0, -1), (0, 1), (1, 0), (-1, 0), 
                    (1, -1), (1, 1), (-1, 1), (-1, -1)
                ]
                obstaculos_perto = tuple(
                    1 if dados_prox.get(f"obs_{x}_{y}") else 0 
                    for x, y in chaves_ordem
                )

        estado_rl = (direcao_farol, obstaculos_perto)

        # DEBUG: O que é que ele está a ver?
        # print(f"ESTADO: Dir={direcao_farol} | Obs={obstaculos_perto}")

        obs_para_politica = Observacao({
            "estado_customizado": estado_rl,
            "posicao": self.posicao 
        })

        if self.politica:
            accao = self.politica.selecionar_accao(obs_para_politica)
            # DEBUG: O que é que ele decidiu?
            # print(f"DECISÃO: {accao.parametros.get('direcao')} (Epsilon atual: {self.politica.epsilon})")
            return accao
        
        return Accao("parar")

    def stop(self):
        if self.politica:
            self.politica.salvar(self.ficheiro_memoria)