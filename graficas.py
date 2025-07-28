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

def obtener_datos_humedad(start=None, end=None):
    """Obtiene registros de humedad de la base de datos.
    Si start y end están dados (strings 'YYYY-MM-DD HH:MM:SS'),
    filtra entre esas fechas; si no, toma los últimos 20."""
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        if start and end:
            query = (
                "SELECT fecha_hora, humedad_porcentaje "
                "FROM humedad_datos "
                "WHERE fecha_hora BETWEEN %s AND %s "
                "ORDER BY fecha_hora ASC"
            )
            cursor.execute(query, (start, end))
            datos = cursor.fetchall()
            # ya vienen ordenados ascendente, no invertimos
            fechas = [d[0] for d in datos]
            valores = [d[1] for d in datos]
        else:
            query = (
                "SELECT fecha_hora, humedad_porcentaje "
                "FROM humedad_datos "
                "ORDER BY fecha_hora DESC "
                "LIMIT 20"
            )
            cursor.execute(query)
            datos = cursor.fetchall()
            # invertimos para orden ascendente
            fechas = [d[0] for d in reversed(datos)]
            valores = [d[1] for d in reversed(datos)]
        conexion.close()
        return fechas, valores

    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        return [], []

def crear_ventana_monitoreo():
    root = tk.Tk()
    root.title("Monitoreo de Humedad")
    root.geometry("800x650")
    root.configure(bg=COLOR_FONDO)

    # --- Sección de filtro ---
    frame_filtro = ttk.LabelFrame(root, text="Filtrar por fecha y hora", padding=10)
    frame_filtro.pack(fill=tk.X, padx=20, pady=(20, 10))

    lbl_inicio = ttk.Label(frame_filtro, text="Desde (YYYY-MM-DD HH:MM:SS):")
    ent_inicio = ttk.Entry(frame_filtro, width=20)
    lbl_fin = ttk.Label(frame_filtro, text="Hasta (YYYY-MM-DD HH:MM:SS):")
    ent_fin = ttk.Entry(frame_filtro, width=20)
    btn_filtrar = tk.Button(
        frame_filtro,
        text="FILTRAR",
        font=("Arial", 10, "bold"),
        bg=COLOR_BOTON,
        fg=COLOR_TEXTO_BOTON,
        command=lambda: actualizar_grafica(ent_inicio.get(), ent_fin.get())
    )

    lbl_inicio.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    ent_inicio.grid(row=0, column=1, padx=5, pady=5)
    lbl_fin.grid(row=0, column=2, padx=5, pady=5, sticky="e")
    ent_fin.grid(row=0, column=3, padx=5, pady=5)
    btn_filtrar.grid(row=0, column=4, padx=10, pady=5)

    # Contenedor principal para gráfica
    frame_principal = ttk.Frame(root)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))

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
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Función para (re)dibujar la gráfica, opcionalmente con filtro
    def actualizar_grafica(start=None, end=None):
        ax.clear()
        fechas, valores = obtener_datos_humedad(start, end)

        if fechas and valores:
            ax.plot(fechas, valores, 'o-', color='#1f5c1a', linewidth=2, markersize=6)
            ax.set_title('Registros de Humedad', fontsize=14)
            ax.set_xlabel('Fecha y Hora', fontsize=10)
            ax.set_ylabel('Humedad (%)', fontsize=10)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, 'Sin datos disponibles',
                    ha='center', va='center', fontsize=12)

        fig.tight_layout()
        canvas.draw()

    # Dibujo inicial sin filtro
    actualizar_grafica()

    # Botón de actualización manual (usa el mismo método sin parámetros)
    btn_actualizar = tk.Button(
        root,
        text="ACTUALIZAR GRÁFICA",
        font=("Arial", 12, "bold"),
        bg=COLOR_BOTON,
        fg=COLOR_TEXTO_BOTON,
        command=lambda: actualizar_grafica(
            ent_inicio.get() or None,
            ent_fin.get() or None
        )
    )
    btn_actualizar.pack(side=tk.RIGHT, padx=20, pady=10)

    # Botón de regreso al menú
    def volver_menu():
        root.destroy()
        subprocess.Popen([sys.executable, "ventana_principal.py"])

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
