from typing import Dict, Any

class Observacao:
    """Estrutura de dados para a observação do ambiente pelo agente."""
    def __init__(self, dados: Dict[str, Any]):
        self.dados = dados

    def __repr__(self):
        return f"Observacao({self.dados})"

    def get(self, key, default=None):
        return self.dados.get(key, default)

class Accao:
    """Estrutura de dados para a ação do agente."""
    def __init__(self, tipo: str, parametros: Dict[str, Any] = None):
        self.tipo = tipo
        self.parametros = parametros or {}

    def __repr__(self):
        return f"Accao(tipo='{self.tipo}', params={self.parametros})"
