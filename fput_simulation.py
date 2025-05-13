import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from matplotlib.animation import FuncAnimation

class FPUTSimulation:
    """
    Simulador do modelo Fermi-Pasta-Ulam-Tsingou (FPUT) com detecção de sólitons.
    """
    
    def __init__(self, n_particles=64, alpha=0.25, beta=0.0, boundary='periodic'):
        """
        Inicializa a simulação FPUT.
        
        Parâmetros:
        - n_particles: número de partículas na cadeia
        - alpha: parâmetro para o termo não-linear quadrático
        - beta: parâmetro para o termo não-linear cúbico
        - boundary: condições de contorno ('fixed' ou 'periodic')
        """
        self.n = n_particles
        self.alpha = alpha
        self.beta = beta
        self.boundary = boundary
        
        # Posições e momentos iniciais das partículas
        self.q = np.zeros(n_particles)
        self.p = np.zeros(n_particles)
        
        # Histórico para análise
        self.history = []
        self.times = []
        self.energy_history = []
        self.mode_energies = []
        
    def set_initial_conditions(self, mode=1, amplitude=0.1):
        """
        Define as condições iniciais excitando um único modo normal.
         
        Parâmetros:
        - mode: número do modo a ser excitado (1 é o primeiro modo)
        - amplitude: amplitude da excitação inicial
        """
        for i in range(self.n):
            # Excitando um único modo senoidal
            self.q[i] = amplitude * np.sin(mode * np.pi * i / self.n)
            self.p[i] = 0.0
    
    def set_soliton_initial_conditions(self, position=0.25, width=5.0, amplitude=0.8):
        """
        Define condições iniciais na forma de um pulso solitário (sóliton).
        
        Parâmetros:
        - position: posição central do sóliton (fração do comprimento total)
        - width: largura do sóliton
        - amplitude: amplitude do sóliton
        """
        x = np.linspace(0, 1, self.n)
        center = position
        
        # Criando um perfil sech^2, característico de sólitons
        self.q = amplitude * (1/np.cosh((x - center) * self.n / width))**2
        self.p = np.zeros(self.n)
    
    def compute_acceleration(self, q):
        """
        Calcula as acelerações para cada partícula com base nas posições.
        """
        accelerations = np.zeros(self.n)
        
        for i in range(self.n):
            if self.boundary == 'periodic':
                prev_idx = (i - 1) % self.n
                next_idx = (i + 1) % self.n
            else:  # fixed boundary
                if i == 0:
                    # Primeira partícula
                    accelerations[i] = (q[i+1] - q[i]) + self.alpha * ((q[i+1] - q[i])**2) + self.beta * ((q[i+1] - q[i])**3)
                    continue
                elif i == self.n - 1:
                    # Última partícula
                    accelerations[i] = (q[i-1] - q[i]) + self.alpha * ((q[i-1] - q[i])**2) + self.beta * ((q[i-1] - q[i])**3)
                    continue
                prev_idx = i - 1
                next_idx = i + 1
                
            # Forças das molas com termos não-lineares
            force_prev = (q[prev_idx] - q[i]) + self.alpha * ((q[prev_idx] - q[i])**2) + self.beta * ((q[prev_idx] - q[i])**3)
            force_next = (q[next_idx] - q[i]) + self.alpha * ((q[next_idx] - q[i])**2) + self.beta * ((q[next_idx] - q[i])**3)
            
            accelerations[i] = force_prev + force_next
            
        return accelerations
    
    def system_ode(self, t, state):
        """
        Define o sistema de EDOs para integração.
        """
        q = state[:self.n]
        p = state[self.n:]
        
        dqdt = p
        dpdt = self.compute_acceleration(q)
        
        return np.concatenate([dqdt, dpdt])
    
    def run_simulation(self, t_max=100.0, dt=0.1):
        """
        Executa a simulação até o tempo t_max.
        """
        t_span = (0, t_max)
        t_eval = np.arange(0, t_max, dt)
        
        # Estado inicial combinando posições e momentos
        initial_state = np.concatenate([self.q, self.p])
        
        # Resolvendo o sistema de EDOs
        solution = solve_ivp(
            self.system_ode, 
            t_span, 
            initial_state, 
            method='RK45', 
            t_eval=t_eval
        )
        
        # Armazenando resultados
        self.times = solution.t
        self.history = []
        
        for i in range(len(solution.t)):
            q_vals = solution.y[:self.n, i]
            p_vals = solution.y[self.n:, i]
            self.history.append((q_vals, p_vals))
            
        # Calculando energias dos modos
        self.calculate_mode_energies()
        
        return self.history, self.times
    
    def calculate_energy(self, q, p):
        """
        Calcula a energia total do sistema.
        """
        kinetic = 0.5 * np.sum(p**2)
        
        potential = 0
        for i in range(self.n):
            if self.boundary == 'periodic':
                next_idx = (i + 1) % self.n
            else:
                if i == self.n - 1:
                    continue
                next_idx = i + 1
                
            dx = q[next_idx] - q[i]
            potential += 0.5 * dx**2 + (self.alpha/3) * dx**3 + (self.beta/4) * dx**4
            
        return kinetic + potential
    
    def calculate_mode_energies(self):
        """
        Calcula a energia em cada modo normal ao longo do tempo.
        """
        n_modes = self.n // 2  # Analisamos metade dos modos
        n_times = len(self.times)
        
        mode_energies = np.zeros((n_modes, n_times))
        
        for t_idx in range(n_times):
            q, p = self.history[t_idx]
            
            # Transformada de Fourier para encontrar amplitudes dos modos
            q_fft = np.fft.fft(q) / self.n
            p_fft = np.fft.fft(p) / self.n
            
            # Calculando energia por modo
            for mode in range(n_modes):
                # A energia de cada modo é proporcional ao quadrado da amplitude
                mode_energies[mode, t_idx] = np.abs(q_fft[mode])**2 + np.abs(p_fft[mode])**2
        
        self.mode_energies = mode_energies
        return mode_energies
    
    def detect_solitons(self, threshold=0.3):
        """
        Detecta sólitons na simulação baseado em picos localizados de energia.
        
        Parâmetros:
        - threshold: limiar para detecção de picos
        
        Retorna:
        - Lista de posições dos sólitons ao longo do tempo
        """
        soliton_positions = []
        
        for t_idx, (q, _) in enumerate(self.history):
            # Calculando energia potencial local
            energy_density = np.zeros(self.n)
            
            for i in range(self.n):
                if self.boundary == 'periodic':
                    next_idx = (i + 1) % self.n
                else:
                    if i == self.n - 1:
                        continue
                    next_idx = i + 1
                    
                dx = q[next_idx] - q[i]
                energy_density[i] = 0.5 * dx**2 + (self.alpha/3) * dx**3 + (self.beta/4) * dx**4
            
            # Normalizando
            if np.max(energy_density) > 0:
                energy_density = energy_density / np.max(energy_density)
            
            # Encontrando picos (potenciais sólitons)
            peaks = []
            for i in range(1, self.n-1):
                if (energy_density[i] > energy_density[i-1] and 
                    energy_density[i] > energy_density[i+1] and 
                    energy_density[i] > threshold):
                    peaks.append(i)
            
            soliton_positions.append(peaks)
        
        return soliton_positions
    
    def plot_spacetime(self, title="Evolução Espaço-Temporal"):
        """
        Gera um gráfico espaço-temporal da simulação.
        """
        plt.figure(figsize=(10, 8))
        
        # Preparando dados para visualização
        space = np.arange(self.n)
        time = self.times
        
        # Criando matriz de dados
        data = np.zeros((len(time), len(space)))
        for t_idx, (q, _) in enumerate(self.history):
            data[t_idx, :] = q
        
        # Plotando como um heatmap
        plt.imshow(data, aspect='auto', origin='lower', 
                   extent=[0, self.n, 0, self.times[-1]],
                   cmap='viridis')
        
        plt.colorbar(label='Deslocamento')
        plt.xlabel('Posição')
        plt.ylabel('Tempo')
        plt.title(title)
        plt.tight_layout()
        
        return plt.gcf()
    
    def plot_mode_energies(self, modes_to_plot=None, title="Energias dos Modos"):
        """
        Plota a evolução temporal da energia dos modos.
        
        Parâmetros:
        - modes_to_plot: lista de modos para plotar (default: [0, 1, 2, 3])
        """
        if modes_to_plot is None:
            modes_to_plot = [0, 1, 2, 3]
            
        plt.figure(figsize=(10, 6))
        
        for mode in modes_to_plot:
            if mode < len(self.mode_energies):
                plt.semilogy(self.times, self.mode_energies[mode], label=f'Modo {mode}')
        
        plt.xlabel('Tempo')
        plt.ylabel('Energia (log)')
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        return plt.gcf()
    
    def animate_simulation(self, interval=50, save_path=None):
        """
        Cria uma animação da simulação.
        
        Parâmetros:
        - interval: intervalo entre frames em ms
        - save_path: caminho para salvar a animação (ex: 'fput_animation.mp4')
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(self.n)
        line, = ax.plot(x, self.history[0][0], 'o-', lw=1, markersize=3)
        
        ax.set_ylim([-1.5, 1.5])
        ax.set_xlim([0, self.n-1])
        ax.set_xlabel('Posição')
        ax.set_ylabel('Deslocamento')
        ax.set_title('Simulação FPUT')
        
        time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
        
        def animate(i):
            if i < len(self.history):
                line.set_ydata(self.history[i][0])
                time_text.set_text(f'Tempo: {self.times[i]:.1f}')
            return line, time_text
        
        ani = FuncAnimation(fig, animate, frames=len(self.history),
                            interval=interval, blit=True)
        
        if save_path:
            ani.save(save_path, writer='ffmpeg')
        
        plt.close()
        return ani

# Função para demonstração
def demo_fput_simulation():
    """
    Demonstração da simulação FPUT com detecção de sólitons.
    """
    # Configuração da simulação com parâmetros para sólitons
    # Na versão α-FPUT (beta=0), sólitons são mais difíceis de ver
    # Na versão β-FPUT (alpha=0, beta>0), sólitons são mais estáveis
    sim = FPUTSimulation(n_particles=128, alpha=0.0, beta=1.0, boundary='periodic')
    
    # Configurando condição inicial para sóliton
    sim.set_soliton_initial_conditions(position=0.25, width=8.0, amplitude=0.8)
    
    # Executando a simulação
    sim.run_simulation(t_max=200.0, dt=0.2)
    
    # Detectando sólitons
    soliton_positions = sim.detect_solitons(threshold=0.4)
    
    # Plotando o diagrama espaço-temporal
    plt.figure(figsize=(12, 10))
    
    # Preparando dados para visualização
    space = np.arange(sim.n)
    time = sim.times
    
    # Criando matriz de dados
    data = np.zeros((len(time), len(space)))
    for t_idx, (q, _) in enumerate(sim.history):
        data[t_idx, :] = q
    
    # Plotando como um heatmap
    plt.imshow(data, aspect='auto', origin='lower', 
               extent=[0, sim.n, 0, sim.times[-1]],
               cmap='viridis')
    
    # Marcando posições dos sólitons detectados
    for t_idx, positions in enumerate(soliton_positions):
        t = sim.times[t_idx]
        for pos in positions:
            plt.plot(pos, t, 'r.', markersize=1)
    
    plt.colorbar(label='Deslocamento')
    plt.xlabel('Posição')
    plt.ylabel('Tempo')
    plt.title('Evolução de Sólitons no Sistema FPUT')
    
    # Plotando alguns frames da evolução temporal
    n_frames = 5
    plt.figure(figsize=(15, 12))
    indices = np.linspace(0, len(sim.times)-1, n_frames, dtype=int)
    
    for i, idx in enumerate(indices):
        plt.subplot(n_frames, 1, i+1)
        plt.plot(space, sim.history[idx][0])
        plt.title(f'Tempo: {sim.times[idx]:.1f}')
        plt.ylim([-1.0, 1.0])
        plt.grid(True)
    
    plt.tight_layout()
    
    # Plotando energia dos modos
    sim.plot_mode_energies(modes_to_plot=[0, 1, 2, 3, 4, 5])
    
    return sim

# Para executar a demonstração:
# sim = demo_fput_simulation()
# plt.show()

# Exemplo de uso interativo
if __name__ == "__main__":
    print("Simulação do paradoxo de Fermi-Pasta-Ulam-Tsingou (FPUT)")
    print("Escolha o tipo de simulação:")
    print("1. Recorrência FPUT (excitar um único modo)")
    print("2. Simulação de Sólitons")
    
    choice = input("Sua escolha (1 ou 2): ")
    
    if choice == "1":
        # Simulação clássica FPUT para demonstrar recorrência
        sim = FPUTSimulation(n_particles=32, alpha=0.25, beta=0.0)
        sim.set_initial_conditions(mode=1, amplitude=0.1)
        sim.run_simulation(t_max=100.0)
        
        # Plotando evolução dos modos
        sim.plot_mode_energies(modes_to_plot=[0, 1, 2, 3])
        plt.show()
        
        # Diagrama espaço-temporal
        sim.plot_spacetime(title="Recorrência FPUT")
        plt.show()
        
    elif choice == "2":
        # Simulação para visualizar sólitons
        sim = FPUTSimulation(n_particles=128, alpha=0.0, beta=1.0, boundary='periodic')
        sim.set_soliton_initial_conditions(position=0.25, width=8.0, amplitude=0.8)
        sim.run_simulation(t_max=200.0)
        
        # Detectando sólitons
        soliton_positions = sim.detect_solitons(threshold=0.4)
        
        # Diagrama espaço-temporal com marcação de sólitons
        fig = sim.plot_spacetime(title="Evolução de Sólitons no Sistema FPUT")
        
        # Marcando posições dos sólitons detectados
        for t_idx, positions in enumerate(soliton_positions):
            t = sim.times[t_idx]
            for pos in positions:
                plt.plot(pos, t, 'r.', markersize=1)
        
        plt.show()
        
        # Animação da simulação
        ani = sim.animate_simulation(interval=50)
        plt.show()
    
    else:
        print("Escolha inválida!")