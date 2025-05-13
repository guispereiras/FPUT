import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import threading
import time
import os

# Importando nossa classe FPUTSimulation
from fput_simulation import FPUTSimulation

class FPUTSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador do Paradoxo FPUT")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Variáveis para armazenar a simulação
        self.simulation = None
        self.simulation_thread = None
        self.running = False
        
        # Estrutura principal
        self.setup_layout()
        self.setup_parameters_frame()
        self.setup_simulation_controls()
        self.setup_visualization_frame()
        self.setup_info_panel()
        
        # Inicializar plots
        self.setup_plots()
        
        # Estado inicial
        self.simulation_type.set("soliton")
        self.update_parameter_visibility()

    def setup_layout(self):
        
        # Adicione este código ao início da função setup_layout no arquivo fput_gui.py
        # para corrigir as cores dos textos:
        """Configurar o layout principal da interface"""
        # Configurar estilo para texto preto em vez de cinza
        style = ttk.Style()
        style.configure("TLabel", foreground="black")
        style.configure("TButton", foreground="black")
        style.configure("TLabelframe.Label", foreground="black")
        style.configure("TEntry", foreground="black")
        style.configure("TCombobox", foreground="black")
        
        # Frame de parâmetros à esquerda
        self.params_frame = ttk.LabelFrame(self.root, text="Parâmetros da Simulação")
        self.params_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Frame de visualização à direita
        self.viz_frame = ttk.LabelFrame(self.root, text="Visualização")
        self.viz_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Frame de informações na parte inferior
        self.info_frame = ttk.Frame(self.root)
        self.info_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Configurar pesos para redimensionamento
        self.root.grid_columnconfigure(0, weight=1, minsize=300)
        self.root.grid_columnconfigure(1, weight=3, minsize=700)
        self.root.grid_rowconfigure(0, weight=20)
        self.root.grid_rowconfigure(1, weight=1)
        """Configurar o layout principal da interface"""
        # Frame de parâmetros à esquerda
        self.params_frame = ttk.LabelFrame(self.root, text="Parâmetros da Simulação")
        self.params_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Frame de visualização à direita
        self.viz_frame = ttk.LabelFrame(self.root, text="Visualização")
        self.viz_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Frame de informações na parte inferior
        self.info_frame = ttk.Frame(self.root)
        self.info_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Configurar pesos para redimensionamento
        self.root.grid_columnconfigure(0, weight=1, minsize=300)
        self.root.grid_columnconfigure(1, weight=3, minsize=700)
        self.root.grid_rowconfigure(0, weight=20)
        self.root.grid_rowconfigure(1, weight=1)
        
    def setup_theory_tab(self, parent_notebook):
        """Configura a aba de teoria com as equações e explicações didáticas"""
        theory_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(theory_frame, text="Teoria")
        
        # Criar um canvas com barra de rolagem para o conteúdo teórico
        canvas_frame = ttk.Frame(theory_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuração da barra de rolagem
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas = tk.Canvas(canvas_frame, yscrollcommand=v_scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=canvas.yview)
        
        # Frame para o conteúdo
        content_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        
        # Adicionar título
        title_label = ttk.Label(content_frame, text="Fundamentos Teóricos do Paradoxo FPUT", 
                            font=("Arial", 16, "bold"))
        title_label.pack(pady=10, padx=10)
        
        # Introdução
        intro_text = """O Paradoxo de Fermi-Pasta-Ulam-Tsingou (FPUT) é um problema fundamental 
    na física de sistemas não-lineares, descoberto em 1955. Este simulador permite explorar 
    as propriedades deste sistema, incluindo o fenômeno de recorrência e a formação de sólitons."""
        
        intro_label = ttk.Label(content_frame, text=intro_text, wraplength=700, justify=tk.LEFT)
        intro_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # Separador
        ttk.Separator(content_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=10)
        
        # Equação do modelo FPUT
        eq_title = ttk.Label(content_frame, text="Equação do Modelo FPUT", font=("Arial", 12, "bold"))
        eq_title.pack(pady=5, padx=20, anchor=tk.W)
        
        eq_text = """O modelo FPUT consiste em uma cadeia de N partículas conectadas por molas com 
    comportamento não-linear. A equação de movimento para a partícula i é:"""
        
        eq_label = ttk.Label(content_frame, text=eq_text, wraplength=700, justify=tk.LEFT)
        eq_label.pack(pady=5, padx=20, anchor=tk.W)
        
        # Figura para a equação do FPUT
        fig_fput = Figure(figsize=(7, 2), dpi=100)
        ax_fput = fig_fput.add_subplot(111)
        ax_fput.axis('off')
        ax_fput.text(0.5, 0.5, r"$\frac{d^2q_i}{dt^2} = (q_{i+1} - q_i) - (q_i - q_{i-1}) + \alpha[(q_{i+1} - q_i)^2 - (q_i - q_{i-1})^2] + \beta[(q_{i+1} - q_i)^3 - (q_i - q_{i-1})^3]$",
                    horizontalalignment='center', verticalalignment='center', fontsize=12)
        
        canvas_fput = FigureCanvasTkAgg(fig_fput, master=content_frame)
        canvas_fput.draw()
        canvas_fput.get_tk_widget().pack(pady=10)
        
        # Explicação dos parâmetros
        param_title = ttk.Label(content_frame, text="Parâmetros do Modelo", font=("Arial", 12, "bold"))
        param_title.pack(pady=5, padx=20, anchor=tk.W)
        
        param_text = """• N (Número de Partículas): Define a discretização do sistema. Mais partículas 
    permitem observar fenômenos em escalas menores, mas aumentam o custo computacional.

    • α (Termo Quadrático): Controla a não-linearidade quadrática. Quando α > 0 e β = 0, 
    temos o sistema α-FPUT, que exibe o fenômeno de recorrência clássico.

    • β (Termo Cúbico): Controla a não-linearidade cúbica. Quando α = 0 e β > 0, 
    temos o sistema β-FPUT, que favorece a formação de sólitons.

    • Condições de Contorno: Podem ser periódicas (formando um anel fechado) ou fixas (extremidades imóveis)."""
        
        param_label = ttk.Label(content_frame, text=param_text, wraplength=700, justify=tk.LEFT)
        param_label.pack(pady=5, padx=20, anchor=tk.W)
        
        # Separador
        ttk.Separator(content_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=10)
        
        # Equação KdV e Sólitons
        kdv_title = ttk.Label(content_frame, text="Equação de Korteweg-de Vries (KdV) e Sólitons", 
                            font=("Arial", 12, "bold"))
        kdv_title.pack(pady=5, padx=20, anchor=tk.W)
        
        kdv_text = """No limite contínuo, o sistema β-FPUT pode ser aproximado pela equação de 
    Korteweg-de Vries (KdV), que é conhecida por admitir soluções do tipo sóliton:"""
        
        kdv_label = ttk.Label(content_frame, text=kdv_text, wraplength=700, justify=tk.LEFT)
        kdv_label.pack(pady=5, padx=20, anchor=tk.W)
        
        # Figura para a equação KdV
        fig_kdv = Figure(figsize=(7, 2), dpi=100)
        ax_kdv = fig_kdv.add_subplot(111)
        ax_kdv.axis('off')
        ax_kdv.text(0.5, 0.5, r"$\frac{\partial u}{\partial t} + u\frac{\partial u}{\partial x} + \delta^2\frac{\partial^3 u}{\partial x^3} = 0$",
                horizontalalignment='center', verticalalignment='center', fontsize=14)
        
        canvas_kdv = FigureCanvasTkAgg(fig_kdv, master=content_frame)
        canvas_kdv.draw()
        canvas_kdv.get_tk_widget().pack(pady=10)
        
        # Explicação sobre sólitons
        soliton_title = ttk.Label(content_frame, text="Formação de Sólitons", font=("Arial", 12, "bold"))
        soliton_title.pack(pady=5, padx=20, anchor=tk.W)
        
        soliton_text = """Sólitons são ondas solitárias estáveis que mantêm sua forma enquanto se propagam. 
    Eles emergem de um equilíbrio entre:

    • Dispersão: Tendência das ondas se espalharem (termo de terceira derivada na equação KdV)
    • Não-linearidade: Tendência de concentrar energia (termo não-linear na equação KdV)

    Para observar sólitons nesta simulação:
    1. Escolha o tipo de simulação 'soliton'
    2. Configure α = 0 e β > 0 (sistema β-FPUT)
    3. Ajuste a largura e amplitude inicial do sóliton
    4. Execute a simulação e observe o padrão de propagação estável"""
        
        soliton_label = ttk.Label(content_frame, text=soliton_text, wraplength=700, justify=tk.LEFT)
        soliton_label.pack(pady=5, padx=20, anchor=tk.W)
        
        # Separador
        ttk.Separator(content_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=10)
        
        # Visualizando a relação dispersão-não linearidade com uma figura
        disp_title = ttk.Label(content_frame, text="Visualização: Dispersão vs. Não-linearidade", 
                            font=("Arial", 12, "bold"))
        disp_title.pack(pady=5, padx=20, anchor=tk.W)
        
        # Figura para mostrar o equilíbrio dispersão-não linearidade
        fig_balance = Figure(figsize=(7, 4), dpi=100)
        ax_balance = fig_balance.add_subplot(111)
        
        # Criar dados para a figura
        x = np.linspace(0, 100, 500)
        
        # Onda dispersiva (sem não-linearidade)
        dispersive_wave = 0.5 * np.exp(-(x-30)**2/50) * np.cos(x/2)
        
        # Onda não-linear (sem dispersão)
        nonlinear_wave = np.zeros_like(x)
        mask = (x > 40) & (x < 60)
        nonlinear_wave[mask] = 0.7 * np.sin(np.pi * (x[mask] - 40) / 20)
        
        # Sóliton (equilíbrio entre dispersão e não-linearidade)
        soliton_wave = 0.7 / np.cosh((x-50)/7)**2
        
        # Plotar os três casos
        ax_balance.plot(x, dispersive_wave, 'b-', label='Apenas Dispersão')
        ax_balance.plot(x, nonlinear_wave, 'r-', label='Apenas Não-linearidade')
        ax_balance.plot(x, soliton_wave, 'g-', linewidth=2, label='Sóliton (Equilíbrio)')
        
        ax_balance.set_xlabel('Posição')
        ax_balance.set_ylabel('Amplitude')
        ax_balance.set_title('Comparação: Dispersão, Não-linearidade e Sólitons')
        ax_balance.legend()
        ax_balance.grid(True, linestyle='--', alpha=0.7)
        
        canvas_balance = FigureCanvasTkAgg(fig_balance, master=content_frame)
        canvas_balance.draw()
        canvas_balance.get_tk_widget().pack(pady=10, padx=20)
        
        # Texto explicativo para a figura
        fig_text = """A figura acima ilustra os três casos:
    • Azul: Uma onda apenas com dispersão tende a se espalhar
    • Vermelho: Uma onda apenas com não-linearidade tende a formar choques/quebras
    • Verde: Um sóliton mantém sua forma devido ao equilíbrio entre dispersão e não-linearidade"""
        
        fig_label = ttk.Label(content_frame, text=fig_text, wraplength=700, justify=tk.LEFT)
        fig_label.pack(pady=5, padx=20, anchor=tk.W)
        
        # Separador
        ttk.Separator(content_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=10)
        
        # Fenômeno de recorrência
        recurrence_title = ttk.Label(content_frame, text="Fenômeno de Recorrência FPUT", 
                                font=("Arial", 12, "bold"))
        recurrence_title.pack(pady=5, padx=20, anchor=tk.W)
        
        recurrence_text = """O paradoxo original de FPUT refere-se à observação surpreendente de que, 
    quando a energia é inicialmente concentrada em um único modo normal de vibração, ela não se 
    distribui uniformemente entre todos os modos como previsto pela mecânica estatística. Em vez disso, 
    a energia eventualmente retorna quase completamente ao modo inicial.

    Para observar o fenômeno de recorrência:
    1. Escolha o tipo de simulação 'recurrence'
    2. Configure α > 0 e β = 0 (sistema α-FPUT)
    3. Selecione um modo a excitar (geralmente o primeiro modo, 1)
    4. Execute a simulação e observe no gráfico de "Energia dos Modos" como a energia volta 
    periodicamente ao modo inicial"""
        
        recurrence_label = ttk.Label(content_frame, text=recurrence_text, wraplength=700, justify=tk.LEFT)
        recurrence_label.pack(pady=5, padx=20, anchor=tk.W)
        
        # Referências
        ref_title = ttk.Label(content_frame, text="Referências", font=("Arial", 12, "bold"))
        ref_title.pack(pady=10, padx=20, anchor=tk.W)
        
        ref_text = """1. Fermi, E., Pasta, J., Ulam, S., & Tsingou, M. (1955). "Studies of the Nonlinear Problems", Los Alamos Scientific Laboratory report LA-1940.

    2. Zabusky, N. J., & Kruskal, M. D. (1965). "Interaction of 'Solitons' in a Collisionless Plasma and the Recurrence of Initial States", Physical Review Letters, 15(6), 240-243.

    3. Dauxois, T., & Peyrard, M. (2006). "Physics of Solitons", Cambridge University Press."""
        
        ref_label = ttk.Label(content_frame, text=ref_text, wraplength=700, justify=tk.LEFT)
        ref_label.pack(pady=5, padx=20, anchor=tk.W)
        
        # Atualizar o scrollregion após a criação do conteúdo
        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))
        
        # Configurar evento de rolagem com o mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        return theory_frame

    def setup_parameters_frame(self):
        """Configurar o frame de parâmetros"""
        # Parâmetros do sistema
        ttk.Label(self.params_frame, text="Parâmetros do Sistema FPUT").grid(row=0, column=0, columnspan=2, sticky="w", pady=(10,5))
        
        # Tipo de simulação
        ttk.Label(self.params_frame, text="Tipo de Simulação:").grid(row=1, column=0, sticky="w", padx=(10,5), pady=2)
        self.simulation_type = tk.StringVar(value="soliton")
        sim_type_cb = ttk.Combobox(self.params_frame, textvariable=self.simulation_type, state="readonly")
        sim_type_cb['values'] = ("soliton", "recurrence")
        sim_type_cb.grid(row=1, column=1, sticky="ew", padx=(0,10), pady=2)
        sim_type_cb.bind("<<ComboboxSelected>>", lambda e: self.update_parameter_visibility())
        
        # Número de partículas
        ttk.Label(self.params_frame, text="Número de Partículas:").grid(row=2, column=0, sticky="w", padx=(10,5), pady=2)
        self.n_particles = tk.IntVar(value=128)
        ttk.Entry(self.params_frame, textvariable=self.n_particles).grid(row=2, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Parâmetro α (quadrático)
        ttk.Label(self.params_frame, text="α (termo quadrático):").grid(row=3, column=0, sticky="w", padx=(10,5), pady=2)
        self.alpha = tk.DoubleVar(value=0.0)
        ttk.Entry(self.params_frame, textvariable=self.alpha).grid(row=3, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Parâmetro β (cúbico)
        ttk.Label(self.params_frame, text="β (termo cúbico):").grid(row=4, column=0, sticky="w", padx=(10,5), pady=2)
        self.beta = tk.DoubleVar(value=1.0)
        ttk.Entry(self.params_frame, textvariable=self.beta).grid(row=4, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Condições de contorno
        ttk.Label(self.params_frame, text="Condições de Contorno:").grid(row=5, column=0, sticky="w", padx=(10,5), pady=2)
        self.boundary = tk.StringVar(value="periodic")
        boundary_cb = ttk.Combobox(self.params_frame, textvariable=self.boundary, state="readonly")
        boundary_cb['values'] = ("periodic", "fixed")
        boundary_cb.grid(row=5, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Separador
        ttk.Separator(self.params_frame, orient="horizontal").grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Parâmetros de sóliton
        ttk.Label(self.params_frame, text="Parâmetros do Sóliton:").grid(row=7, column=0, columnspan=2, sticky="w", pady=(5,5))
        
        # Posição do sóliton
        ttk.Label(self.params_frame, text="Posição (0-1):").grid(row=8, column=0, sticky="w", padx=(10,5), pady=2)
        self.soliton_position = tk.DoubleVar(value=0.25)
        ttk.Entry(self.params_frame, textvariable=self.soliton_position).grid(row=8, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Largura do sóliton
        ttk.Label(self.params_frame, text="Largura:").grid(row=9, column=0, sticky="w", padx=(10,5), pady=2)
        self.soliton_width = tk.DoubleVar(value=8.0)
        ttk.Entry(self.params_frame, textvariable=self.soliton_width).grid(row=9, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Amplitude do sóliton
        ttk.Label(self.params_frame, text="Amplitude:").grid(row=10, column=0, sticky="w", padx=(10,5), pady=2)
        self.soliton_amplitude = tk.DoubleVar(value=0.8)
        ttk.Entry(self.params_frame, textvariable=self.soliton_amplitude).grid(row=10, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Parâmetros de recorrência
        ttk.Label(self.params_frame, text="Parâmetros da Recorrência:").grid(row=11, column=0, columnspan=2, sticky="w", pady=(5,5))
        
        # Modo a excitar
        ttk.Label(self.params_frame, text="Modo a excitar:").grid(row=12, column=0, sticky="w", padx=(10,5), pady=2)
        self.mode = tk.IntVar(value=1)
        ttk.Entry(self.params_frame, textvariable=self.mode).grid(row=12, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Amplitude do modo
        ttk.Label(self.params_frame, text="Amplitude do modo:").grid(row=13, column=0, sticky="w", padx=(10,5), pady=2)
        self.mode_amplitude = tk.DoubleVar(value=0.1)
        ttk.Entry(self.params_frame, textvariable=self.mode_amplitude).grid(row=13, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Separador
        ttk.Separator(self.params_frame, orient="horizontal").grid(row=14, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Parâmetros da simulação
        ttk.Label(self.params_frame, text="Parâmetros da simulação:").grid(row=15, column=0, columnspan=2, sticky="w", pady=(5,5))
        
        # Tempo máximo
        ttk.Label(self.params_frame, text="Tempo máximo:").grid(row=16, column=0, sticky="w", padx=(10,5), pady=2)
        self.t_max = tk.DoubleVar(value=100.0)
        ttk.Entry(self.params_frame, textvariable=self.t_max).grid(row=16, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Passo de tempo
        ttk.Label(self.params_frame, text="Passo de tempo (dt):").grid(row=17, column=0, sticky="w", padx=(10,5), pady=2)
        self.dt = tk.DoubleVar(value=0.2)
        ttk.Entry(self.params_frame, textvariable=self.dt).grid(row=17, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Limiar para detecção de sólitons
        ttk.Label(self.params_frame, text="Limiar de detecção:").grid(row=18, column=0, sticky="w", padx=(10,5), pady=2)
        self.threshold = tk.DoubleVar(value=0.4)
        ttk.Entry(self.params_frame, textvariable=self.threshold).grid(row=18, column=1, sticky="ew", padx=(0,10), pady=2)
        
        # Fazer o frame expandir verticalmente
        self.params_frame.grid_columnconfigure(1, weight=1)
        for i in range(25):  # Adicionar mais linhas para expansão
            self.params_frame.grid_rowconfigure(i, weight=0)

    def setup_simulation_controls(self):
        """Configurar os controles da simulação"""
        # Frame para os botões
        control_frame = ttk.Frame(self.params_frame)
        control_frame.grid(row=19, column=0, columnspan=2, pady=15, sticky="ew")
        
        # Botão para executar simulação
        self.run_button = ttk.Button(control_frame, text="Executar Simulação", command=self.run_simulation)
        self.run_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Botão para parar simulação
        self.stop_button = ttk.Button(control_frame, text="Parar", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Botão para exportar resultados
        self.export_button = ttk.Button(control_frame, text="Exportar", command=self.export_results, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def setup_visualization_frame(self):
        """Configurar o frame de visualização"""
        # Notebook para diferentes tipos de visualização
        self.viz_notebook = ttk.Notebook(self.viz_frame)
        self.viz_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Abas para diferentes visualizações
        self.spacetime_frame = ttk.Frame(self.viz_notebook)
        self.energy_frame = ttk.Frame(self.viz_notebook)
        self.snapshot_frame = ttk.Frame(self.viz_notebook)
        
        self.viz_notebook.add(self.spacetime_frame, text="Espaço-Tempo")
        self.viz_notebook.add(self.energy_frame, text="Energia dos Modos")
        self.viz_notebook.add(self.snapshot_frame, text="Snapshots")
        
        # Adicionar a aba de teoria
        self.theory_frame = self.setup_theory_tab(self.viz_notebook)

    def setup_plots(self):
        """Inicializar os plots"""
        # Plot espaço-temporal
        self.spacetime_fig = Figure(figsize=(6, 5), dpi=100)
        self.spacetime_ax = self.spacetime_fig.add_subplot(111)
        self.spacetime_canvas = FigureCanvasTkAgg(self.spacetime_fig, master=self.spacetime_frame)
        self.spacetime_canvas.draw()
        self.spacetime_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Barra de ferramentas
        toolbar = NavigationToolbar2Tk(self.spacetime_canvas, self.spacetime_frame)
        toolbar.update()
        
        # Plot de energia dos modos
        self.energy_fig = Figure(figsize=(6, 5), dpi=100)
        self.energy_ax = self.energy_fig.add_subplot(111)
        self.energy_canvas = FigureCanvasTkAgg(self.energy_fig, master=self.energy_frame)
        self.energy_canvas.draw()
        self.energy_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Barra de ferramentas
        toolbar2 = NavigationToolbar2Tk(self.energy_canvas, self.energy_frame)
        toolbar2.update()
        
        # Plot de snapshots
        self.snapshot_fig = Figure(figsize=(6, 5), dpi=100)
        self.snapshot_fig.subplots_adjust(hspace=0.5)
        self.snapshot_axes = []
        for i in range(5):
            self.snapshot_axes.append(self.snapshot_fig.add_subplot(5, 1, i+1))
        
        self.snapshot_canvas = FigureCanvasTkAgg(self.snapshot_fig, master=self.snapshot_frame)
        self.snapshot_canvas.draw()
        self.snapshot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Barra de ferramentas
        toolbar3 = NavigationToolbar2Tk(self.snapshot_canvas, self.snapshot_frame)
        toolbar3.update()

    def setup_info_panel(self):
        """Configurar o painel de informações"""
        # Status da simulação
        status_frame = ttk.LabelFrame(self.info_frame, text="Status")
        status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        self.status_var = tk.StringVar(value="Pronto para simulação")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(padx=10, pady=5)
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

    def update_parameter_visibility(self):
        """Atualizar a visibilidade dos parâmetros baseado no tipo de simulação"""
        sim_type = self.simulation_type.get()
        
        # Configurar os valores adequados para cada tipo de simulação
        if sim_type == "soliton":
            # Sistema β-FPUT para sólitons
            self.alpha.set(0.0)
            self.beta.set(1.0)
            self.n_particles.set(128)
            self.t_max.set(200.0)
        else:  # recurrence
            # Sistema α-FPUT para recorrência
            self.alpha.set(0.25)
            self.beta.set(0.0)
            self.n_particles.set(32)
            self.t_max.set(100.0)

    def run_simulation(self):
        """Iniciar a simulação em uma thread separada"""
        # Verificar parâmetros
        try:
            n = int(self.n_particles.get())
            alpha = float(self.alpha.get())
            beta = float(self.beta.get())
            t_max = float(self.t_max.get())
            dt = float(self.dt.get())
            
            if n <= 0 or t_max <= 0 or dt <= 0:
                raise ValueError("Parâmetros devem ser positivos")
                
        except ValueError as e:
            messagebox.showerror("Erro", f"Parâmetros inválidos: {str(e)}")
            return
        
        # Desabilitar botão de execução e habilitar botão de parada
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.DISABLED)
        
        # Iniciar thread de simulação
        self.running = True
        self.simulation_thread = threading.Thread(target=self.simulation_worker)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
    
    def simulation_worker(self):
        """Função para executar a simulação em uma thread separada"""
        try:
            # Atualizar status
            self.status_var.set("Inicializando simulação...")
            self.progress_var.set(0)
            
            # Obter parâmetros
            n = int(self.n_particles.get())
            alpha = float(self.alpha.get())
            beta = float(self.beta.get())
            boundary = self.boundary.get()
            t_max = float(self.t_max.get())
            dt = float(self.dt.get())
            threshold = float(self.threshold.get())
            
            # Criar simulação
            self.simulation = FPUTSimulation(n_particles=n, alpha=alpha, beta=beta, boundary=boundary)
            
            # Configurar condições iniciais
            sim_type = self.simulation_type.get()
            if sim_type == "soliton":
                position = float(self.soliton_position.get())
                width = float(self.soliton_width.get())
                amplitude = float(self.soliton_amplitude.get())
                
                self.status_var.set("Configurando sóliton inicial...")
                self.simulation.set_soliton_initial_conditions(position=position, width=width, amplitude=amplitude)
            else:  # recurrence
                mode = int(self.mode.get())
                amplitude = float(self.mode_amplitude.get())
                
                self.status_var.set(f"Excitando modo {mode}...")
                self.simulation.set_initial_conditions(mode=mode, amplitude=amplitude)
            
            # Executar simulação
            self.status_var.set("Executando simulação...")
            
            # Número total de passos
            n_steps = int(t_max / dt)
            
            # Executar a simulação passo a passo para atualizar a barra de progresso
            t_span = (0, t_max)
            t_eval = np.linspace(0, t_max, n_steps)
            
            # Estado inicial combinando posições e momentos
            from scipy.integrate import solve_ivp # Certifique-se que esta linha está presente
            
            initial_state = np.concatenate([self.simulation.q, self.simulation.p])
            
            
            # Função de callback para atualizar o progresso
            last_update_time = time.time()
            
            def progress_callback(t, y):
                nonlocal last_update_time
                current_time = time.time()
                
                # Limitar atualizações para não sobrecarregar a interface
                if current_time - last_update_time > 0.1:
                    progress = (t / t_max) * 100
                    self.progress_var.set(progress)
                    self.status_var.set(f"Simulando... {progress:.1f}%")
                    last_update_time = current_time
                
                # Verificar se a simulação foi interrompida
                return not self.running
            
            # Resolvendo o sistema de EDOs
            solution = solve_ivp(
                self.simulation.system_ode, 
                t_span, 
                initial_state, 
                method='RK45', 
                t_eval=t_eval,
                events=progress_callback
            )
            
            # Se a simulação foi interrompida
            if not self.running:
                self.status_var.set("Simulação interrompida.")
                self.root.after(0, self.enable_run_button)
                return
            
            # Armazenando resultados
            self.simulation.times = solution.t
            self.simulation.history = []
            
            for i in range(len(solution.t)):
                q_vals = solution.y[:n, i]
                p_vals = solution.y[n:, i]
                self.simulation.history.append((q_vals, p_vals))
            
            # Calcular energias dos modos
            self.status_var.set("Calculando energias dos modos...")
            self.simulation.calculate_mode_energies()
            
            # Detectar sólitons
            self.status_var.set("Detectando sólitons...")
            soliton_positions = self.simulation.detect_solitons(threshold=threshold)
            
            # Atualizar visualizações
            self.status_var.set("Atualizando visualizações...")
            self.root.after(0, lambda: self.update_visualizations(soliton_positions))
            
        except Exception as e:
            self.status_var.set(f"Erro: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            self.root.after(0, self.enable_run_button)

    def stop_simulation(self):
        """Parar a simulação em execução"""
        self.running = False
        self.status_var.set("Parando simulação...")
        self.stop_button.config(state=tk.DISABLED)

    def enable_run_button(self):
        """Habilitar o botão de execução após a simulação"""
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Habilitar exportação apenas se a simulação foi bem-sucedida
        if self.simulation and hasattr(self.simulation, 'history') and self.simulation.history:
            self.export_button.config(state=tk.NORMAL)
            
    def setup_theory_tab(self, parent_notebook):
        """Configura a aba de teoria com as equações e explicações didáticas"""
        theory_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(theory_frame, text="Teoria")
        
        # Criar um canvas com barra de rolagem para o conteúdo teórico
        canvas_frame = ttk.Frame(theory_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuração da barra de rolagem
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas = tk.Canvas(canvas_frame, yscrollcommand=v_scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=canvas.yview)
        
        # Frame para o conteúdo
        content_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        
        # Conteúdo da aba de teoria...
        # [O resto do código da função setup_theory_tab aqui]
        
        # Atualizar o scrollregion após a criação do conteúdo
        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))
        
        # Configurar evento de rolagem com o mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
         
        return theory_frame

    def update_visualizations(self, soliton_positions):
        """Atualizar as visualizações com os resultados da simulação"""
        if not self.simulation or not hasattr(self.simulation, 'history') or not self.simulation.history:
            return
        
        # Limpar os plots existentes
        self.spacetime_ax.clear()
        self.energy_ax.clear()
        for ax in self.snapshot_axes:
            ax.clear()
        
        # Plot espaço-temporal
        space = np.arange(self.simulation.n)
        time = self.simulation.times
        
        # Criando matriz de dados
        data = np.zeros((len(time), len(space)))
        for t_idx, (q, _) in enumerate(self.simulation.history):
            data[t_idx, :] = q
        
        # Plotando como um heatmap
        im = self.spacetime_ax.imshow(data, aspect='auto', origin='lower', 
                   extent=[0, self.simulation.n, 0, self.simulation.times[-1]],
                   cmap='viridis')
        
        # Adicionar barra de cores
        self.spacetime_fig.colorbar(im, ax=self.spacetime_ax, label='Deslocamento')
        
        # Marcar posições dos sólitons detectados
        for t_idx, positions in enumerate(soliton_positions):
            t = self.simulation.times[t_idx]
            for pos in positions:
                self.spacetime_ax.plot(pos, t, 'r.', markersize=1)
        
        self.spacetime_ax.set_xlabel('Posição')
        self.spacetime_ax.set_ylabel('Tempo')
        sim_type = self.simulation_type.get()
        if sim_type == "soliton":
            self.spacetime_ax.set_title('Evolução de Sólitons no Sistema FPUT')
        else:
            self.spacetime_ax.set_title('Recorrência FPUT')
        
        self.spacetime_fig.tight_layout()
        self.spacetime_canvas.draw()
        
        # Plot de energia dos modos
        modes_to_plot = range(min(6, len(self.simulation.mode_energies)))
        for mode in modes_to_plot:
            if mode < len(self.simulation.mode_energies):
                self.energy_ax.semilogy(self.simulation.times, self.simulation.mode_energies[mode], label=f'Modo {mode}')
        
        self.energy_ax.set_xlabel('Tempo')
        self.energy_ax.set_ylabel('Energia (log)')
        if sim_type == "soliton":
            self.energy_ax.set_title('Energia dos Modos - Simulação de Sólitons')
        else:
            self.energy_ax.set_title('Energia dos Modos - Recorrência FPUT')
        self.energy_ax.legend()
        self.energy_ax.grid(True)
        
        self.energy_fig.tight_layout()
        self.energy_canvas.draw()
        
        # Plotar snapshots da evolução
        n_frames = len(self.snapshot_axes)
        indices = np.linspace(0, len(self.simulation.times)-1, n_frames, dtype=int)
        
        for i, idx in enumerate(indices):
            if idx < len(self.simulation.history):
                ax = self.snapshot_axes[i]
                ax.plot(np.arange(self.simulation.n), self.simulation.history[idx][0])
                ax.set_title(f'Tempo: {self.simulation.times[idx]:.1f}')
                ax.set_ylim([-1.0, 1.0])
                ax.grid(True)
                
                if i == n_frames - 1:
                    ax.set_xlabel('Posição')
                
                if i == n_frames // 2:
                    ax.set_ylabel('Deslocamento')
        
        self.snapshot_fig.tight_layout()
        self.snapshot_canvas.draw()
        
        # Atualizar status
        self.status_var.set("Simulação concluída.")
        self.progress_var.set(100.0)

    def export_results(self):
        """Exportar os resultados da simulação"""
        if not self.simulation or not hasattr(self.simulation, 'history') or not self.simulation.history:
            messagebox.showerror("Erro", "Não há resultados para exportar.")
            return
        
        # Pedir diretório para salvar
        export_dir = filedialog.askdirectory(title="Selecione o diretório para exportar os resultados")
        if not export_dir:
            return
        
        try:
            # Salvar gráfico espaço-temporal
            self.spacetime_fig.savefig(os.path.join(export_dir, "fput_spacetime.png"), dpi=300)
            
            # Salvar gráfico de energia dos modos
            self.energy_fig.savefig(os.path.join(export_dir, "fput_mode_energies.png"), dpi=300)
            
            # Salvar snapshots
            self.snapshot_fig.savefig(os.path.join(export_dir, "fput_snapshots.png"), dpi=300)
            
            # Salvar dados em CSV
            import csv
            
            # Salvar posições (q) em cada instante de tempo
            with open(os.path.join(export_dir, "fput_positions.csv"), 'w', newline='') as f:
                writer = csv.writer(f)
                # Cabeçalho
                header = ["tempo"] + [f"q_{i}" for i in range(self.simulation.n)]
                writer.writerow(header)
                
                # Dados
                for t_idx, (q, _) in enumerate(self.simulation.history):
                    row = [self.simulation.times[t_idx]] + list(q)
                    writer.writerow(row)
            
            # Salvar energia dos modos
            with open(os.path.join(export_dir, "fput_mode_energies.csv"), 'w', newline='') as f:
                writer = csv.writer(f)
                # Cabeçalho
                header = ["tempo"] + [f"modo_{i}" for i in range(len(self.simulation.mode_energies))]
                writer.writerow(header)
                
                # Dados
                for t_idx in range(len(self.simulation.times)):
                    row = [self.simulation.times[t_idx]]
                    for mode in range(len(self.simulation.mode_energies)):
                        row.append(self.simulation.mode_energies[mode][t_idx])
                    writer.writerow(row)
            
            # Salvar parâmetros da simulação
            with open(os.path.join(export_dir, "fput_parameters.txt"), 'w') as f:
                f.write("Parâmetros da Simulação FPUT\n")
                f.write("==========================\n\n")
                f.write(f"Tipo de simulação: {self.simulation_type.get()}\n")
                f.write(f"Número de partículas: {self.simulation.n}\n")
                f.write(f"α (termo quadrático): {self.simulation.alpha}\n")
                f.write(f"β (termo cúbico): {self.simulation.beta}\n")
                f.write(f"Condições de contorno: {self.simulation.boundary}\n")
                f.write(f"Tempo máximo: {self.simulation.times[-1]}\n")
                f.write(f"Passo de tempo: {self.dt.get()}\n")
                
                if self.simulation_type.get() == "soliton":
                    f.write("\nParâmetros do Sóliton:\n")
                    f.write(f"Posição: {self.soliton_position.get()}\n")
                    f.write(f"Largura: {self.soliton_width.get()}\n")
                    f.write(f"Amplitude: {self.soliton_amplitude.get()}\n")
                else:
                    f.write("\nParâmetros da Recorrência:\n")
                    f.write(f"Modo excitado: {self.mode.get()}\n")
                    f.write(f"Amplitude do modo: {self.mode_amplitude.get()}\n")
            
            messagebox.showinfo("Exportação", f"Resultados exportados com sucesso para {export_dir}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar resultados: {str(e)}")

# Código principal para executar a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = FPUTSimulatorGUI(root)
    root.mainloop()