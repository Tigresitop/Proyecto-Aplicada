import sys
import subprocess
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from conexion import conectar  # Importa tu conexión existente
import mysql.connector
from PIL import Image, ImageTk

# Configuración de colores
COLOR_FONDO = "#e7f8e2"
COLOR_BOTON = "#d4f4c0"
COLOR_TEXTO_BOTON = "#0f5e2d"
# Intervalo de refresco automático (milisegundos)
INTERVALO_REFRESH_MS = 2000  # 5 segundos

def obtener_datos_humedad():
    """Obtiene los últimos 20 registros de humedad de la base de datos"""
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT fecha_hora, humedad_porcentaje FROM humedad_datos "
            "ORDER BY fecha_hora DESC LIMIT 20"
        )
        datos = cursor.fetchall()
        conexion.close()

        fechas = [d[0] for d in reversed(datos)]
        valores = [d[1] for d in reversed(datos)]
        return fechas, valores

    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        return [], []

def crear_ventana_monitoreo():
    root = tk.Tk()
    root.title("Monitoreo de Humedad")
    root.geometry("800x600")
    root.configure(bg=COLOR_FONDO)

    # Contenedor principal
    frame_principal = ttk.Frame(root)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Crear figura de matplotlib
    fig = plt.Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_title('Últimos Registros de Humedad', fontsize=14)
    ax.set_xlabel('Fecha y Hora', fontsize=10)
    ax.set_ylabel('Humedad (%)', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Integrar gráfico en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame_principal)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    # Función para (re)dibujar la gráfica
    def actualizar_grafica():
        ax.clear()
        fechas, valores = obtener_datos_humedad()

        if fechas and valores:
            ax.plot(fechas, valores, 'o-', color='#1f5c1a', linewidth=2, markersize=6)
            ax.set_title('Últimos Registros de Humedad', fontsize=14)
            ax.set_xlabel('Fecha y Hora', fontsize=10)
            ax.set_ylabel('Humedad (%)', fontsize=10)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, 'Sin datos disponibles',
                    ha='center', va='center', fontsize=12)

        fig.tight_layout()
        canvas.draw()

    # Llamada manual (botón) y automática
    actualizar_grafica()  # Dibujo inicial

    # Programar refresco automático
    def refrescar_periodicamente():
        actualizar_grafica()
        root.after(INTERVALO_REFRESH_MS, refrescar_periodicamente)

    root.after(INTERVALO_REFRESH_MS, refrescar_periodicamente)

    # Botón de actualización manual
    btn_actualizar = tk.Button(
        root,
        text="ACTUALIZAR GRÁFICA",
        font=("Arial", 12, "bold"),
        bg=COLOR_BOTON,
        fg=COLOR_TEXTO_BOTON,
        command=actualizar_grafica
    )
    btn_actualizar.pack(side=tk.RIGHT, padx=20, pady=10)

    # Función para volver al menú principal
    def volver_menu():
        root.destroy()
        subprocess.Popen([sys.executable, "ventana_principal.py"])

    # Botón de regreso
    btn_volver = tk.Button(
        root,
        text="VOLVER AL MENÚ",
        font=("Arial", 12),
        bg="#f0f0f0",
        command=volver_menu
    )
    btn_volver.pack(side=tk.LEFT, padx=20, pady=10)

    root.mainloop()

if __name__ == "__main__":
    crear_ventana_monitoreo()
