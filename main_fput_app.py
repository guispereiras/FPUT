#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicativo para Simulação do Paradoxo de Fermi-Pasta-Ulam-Tsingou (FPUT)
com Interface Gráfica para Visualização de Sólitons

Este aplicativo permite explorar o paradoxo FPUT de forma interativa,
visualizando sólitons em sistemas não-lineares e o fenômeno de recorrência.

Autor: Guilherme Pereira
Data: 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Definir backend antes de importar pyplot

# Importar os módulos do nosso projeto
try:
    from fput_simulation import FPUTSimulation
    from fput_gui import FPUTSimulatorGUI
except ImportError:
    messagebox.showerror("Erro", "Não foi possível importar os módulos necessários. "
                         "Verifique se os arquivos fput_simulation.py e fput_gui.py "
                         "estão no mesmo diretório que este script.")
    sys.exit(1)

def main():
    """Função principal para iniciar o aplicativo"""
    # Configurar tema da interface
    try:
        # Tentar usar um tema moderno
        import ttkthemes
        root = ttkthemes.ThemedTk()
        root.set_theme("arc")  # Outros temas disponíveis: 'equilux', 'breeze', etc.
    except ImportError:
        # Se o pacote ttkthemes não estiver disponível, usar tkinter padrão
        root = tk.Tk()
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')  # Tema um pouco melhor que o padrão
    
    # Configurar janela principal
    root.title("Simulador do Paradoxo FPUT - Visualização de Sólitons")
    root.geometry("1280x800")
    
    # Definir ícone do aplicativo se disponível
    try:
        if os.path.exists("icon.png"):
            icon = tk.PhotoImage(file="icon.png")
            root.iconphoto(True, icon)
    except Exception:
        pass  # Ignorar erros com o ícone
    
    # Criar a interface do simulador
    app = FPUTSimulatorGUI(root)
    
    # Exibir mensagem de boas-vindas
    messagebox.showinfo(
        "Simulador FPUT",
        "Bem-vindo ao Simulador do Paradoxo de Fermi-Pasta-Ulam-Tsingou!\n\n"
        "Este aplicativo permite visualizar sólitons e o fenômeno de recorrência "
        "em um sistema não-linear. Você pode ajustar os parâmetros à esquerda e "
        "executar a simulação para observar os resultados.\n\n"
        "Para visualizar sólitons, escolha o tipo 'soliton' com β > 0 e α = 0.\n"
        "Para visualizar recorrência FPUT, escolha o tipo 'recurrence' com α > 0 e β = 0."
    )
    
    # Iniciar o loop principal da aplicação
    root.mainloop()

def verificar_requisitos():
    """Verificar se todos os pacotes necessários estão instalados"""
    pacotes_necessarios = ['numpy', 'scipy', 'matplotlib', 'tkinter']
    pacotes_faltantes = []
    
    for pacote in pacotes_necessarios:
        try:
            if pacote == 'tkinter':
                import tkinter
            elif pacote == 'numpy':
                import numpy
            elif pacote == 'scipy':
                import scipy
            elif pacote == 'matplotlib':
                import matplotlib
        except ImportError:
            pacotes_faltantes.append(pacote)
    
    if pacotes_faltantes:
        print("ERRO: Os seguintes pacotes necessários não estão instalados:")
        for pacote in pacotes_faltantes:
            print(f"  - {pacote}")
        print("\nPor favor, instale os pacotes faltantes usando pip:")
        print(f"pip install {' '.join(pacotes_faltantes)}")
        return False
    
    return True

if __name__ == "__main__":
    # Verificar requisitos antes de iniciar o aplicativo
    if verificar_requisitos():
        main()
    else: 
        sys.exit(1)