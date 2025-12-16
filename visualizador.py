import tkinter as tk
import math

class VisualizadorTk:
    def __init__(self, largura, altura, tamanho_celula=30):
        self.largura = largura
        self.altura = altura
        self.tamanho_celula = tamanho_celula
        
        self.root = tk.Tk()
        self.root.title("Simulação SMA - Farol")
        
        canvas_width = largura * tamanho_celula
        canvas_height = altura * tamanho_celula
        self.canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack()
        
    def desenhar(self, ambiente, agentes):
        self.canvas.delete("all")
        
        # Desenhar Grelha (Opcional)
        for i in range(self.largura + 1):
            x = i * self.tamanho_celula
            self.canvas.create_line(x, 0, x, self.altura * self.tamanho_celula, fill="#ddd")
        for i in range(self.altura + 1):
            y = i * self.tamanho_celula
            self.canvas.create_line(0, y, self.largura * self.tamanho_celula, y, fill="#ddd")
            
        # Desenhar Obstáculos
        # Desenhar Obstáculos / Paredes
        if hasattr(ambiente, 'obstaculos'):
            for obs in ambiente.obstaculos:
                x, y = obs
                self._desenhar_celula(x, y, "gray", "wall")
        elif hasattr(ambiente, 'paredes'):
            for parede in ambiente.paredes:
                x, y = parede
                self._desenhar_celula(x, y, "black", "")

        # Desenhar Farol / Saída
        if hasattr(ambiente, 'farol_pos'):
            fx, fy = ambiente.farol_pos
            self._desenhar_celula(fx, fy, "yellow", "F")
        elif hasattr(ambiente, 'saida'):
            sx, sy = ambiente.saida
            self._desenhar_celula(sx, sy, "green", "S")
        
        # Desenhar Agentes
        colors = ["red", "blue", "green", "orange", "purple"]
        for i, agente in enumerate(agentes):
            if agente in ambiente.agentes_posicoes:
                pos = ambiente.agentes_posicoes[agente]
                color = colors[i % len(colors)]
                self._desenhar_agente(pos[0], pos[1], color, agente.nome)
                
        self.root.update()

    def _desenhar_celula(self, x, y, cor, texto=None):
        cx = x * self.tamanho_celula
        cy = y * self.tamanho_celula
        self.canvas.create_rectangle(cx, cy, cx + self.tamanho_celula, cy + self.tamanho_celula, fill=cor, outline="black")
        if texto:
            self.canvas.create_text(cx + self.tamanho_celula/2, cy + self.tamanho_celula/2, text=texto)

    def _desenhar_agente(self, x, y, cor, nome):
        cx = x * self.tamanho_celula
        cy = y * self.tamanho_celula
        # Desenhar circulo
        padding = 5
        self.canvas.create_oval(cx + padding, cy + padding, cx + self.tamanho_celula - padding, cy + self.tamanho_celula - padding, fill=cor)
        # Nome (primeira letra)
        self.canvas.create_text(cx + self.tamanho_celula/2, cy + self.tamanho_celula/2, text=nome[0], fill="white", font=("Arial", 10, "bold"))

    def fechar(self):
        self.root.destroy()
