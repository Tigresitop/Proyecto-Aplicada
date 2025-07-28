import tkinter as tk
from tkinter import messagebox, font
import subprocess
import sys
from PIL import Image, ImageTk

COLOR_FONDO = "#e7f8e2"
COLOR_BOTON = "#d4f4c0"
COLOR_TEXTO_BOTON = "#0f5e2d"
COLOR_TITULO = "#1f5c1a"
COLOR_SECCION = "#0096D6"

root = tk.Tk()
root.title("Control de Riego")
root.geometry("600x400")
root.configure(bg=COLOR_FONDO)
try:
    custom_font = font.Font(family="Segoe UI", size=12)
except:
    custom_font = font.Font(family="Arial", size=12)

imagen_fondo = Image.open("assets/cesped.png")
esquina_size = (int(600*0.3), int(400*0.3))
imagen_fondo = imagen_fondo.resize(esquina_size, Image.Resampling.LANCZOS)
imagen_fondo = ImageTk.PhotoImage(imagen_fondo)

label_fondo = tk.Label(root, image=imagen_fondo, bg=COLOR_FONDO)
label_fondo.place(relx=0.0, rely=1.0, anchor='sw')

def cerrar():
    if messagebox.askokcancel("Salir", "¿Cerrar la aplicación?"):
        root.destroy()

def abrir_monitoreo():
    root.destroy()
    try:
        subprocess.Popen([sys.executable, "ventana_monitoreo.py"])
    except Exception as e:
        subprocess.Popen(["python", "ventana_monitoreo.py"])
def ir_a_graficas():
    # cierra esta ventana y lanza graficas.py
    root.destroy()
    subprocess.Popen([sys.executable, "graficas.py"])
titulo = tk.Label(
    root, 
    text="CONTROL DE RIEGO", 
    font=("Arial Black", 24, "bold"), 
    bg=COLOR_FONDO, 
    fg=COLOR_TITULO
)
titulo.pack(pady=10)


frame_izquierda = tk.Frame(root, bg=COLOR_FONDO)
frame_izquierda.place(x=50, y=100)

# Sección en mayúsculas
seccion1 = tk.Label(
    frame_izquierda, 
    text="PANTALLA DE\nMONITOREO", 
    font=("Arial", 16, "bold"), 
    bg=COLOR_FONDO, 
    fg=COLOR_SECCION
)
seccion1.pack()

btn_monitoreo = tk.Button(
    frame_izquierda, 
    text="MONITOREO", 
    font=("Arial", 14, "bold"), 
    bg=COLOR_BOTON, 
    fg=COLOR_TEXTO_BOTON, 
    width=15, 
    height=2,
    command=abrir_monitoreo 
)
btn_monitoreo.pack(pady=10)

frame_derecha = tk.Frame(root, bg=COLOR_FONDO)
frame_derecha.place(x=350, y=100)

seccion2 = tk.Label(
    frame_derecha, 
    text="GRÁFICOS", 
    font=("Arial", 20, "bold"), 
    bg=COLOR_FONDO, 
    fg=COLOR_SECCION
)
seccion2.pack()

# Función para cargar iconos con transparencia
def cargar_icono_transparente(ruta, size):
    img = Image.open(ruta).convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    img = img.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

icon_size = (20, 20)
icon_humedad = cargar_icono_transparente("analitica.png", icon_size)
icon_rendimiento = cargar_icono_transparente("beneficios.png", icon_size)

btn_humedad = tk.Button(
    frame_derecha, 
    text=" HUMEDAD", 
    image=icon_humedad, 
    compound="left",
    font=("Arial", 14, "bold"), 
    bg=COLOR_BOTON, 
    fg=COLOR_TEXTO_BOTON, 
    width=160, 
    anchor="w"
)
btn_humedad.image = icon_humedad
btn_humedad.pack(pady=5)

btn_rendimiento = tk.Button(
    frame_derecha, 
    text=" RENDIMIENTO", 
    image=icon_rendimiento, 
    compound="left",
    font=("Arial", 14, "bold"), 
    bg=COLOR_BOTON, 
    fg=COLOR_TEXTO_BOTON, 
    width=160, 
    anchor="w"
)
btn_rendimiento.image = icon_rendimiento
btn_rendimiento.pack(pady=5)

btn_estado = tk.Button(
    frame_derecha, 
    text="ESTADO ACTUAL", 
    font=("Arial", 14, "bold"), 
    bg=COLOR_BOTON, 
    fg=COLOR_TEXTO_BOTON, 
    width=15,
    height=1,
    command=ir_a_graficas
)
btn_estado.pack(pady=5)


btn_cerrar = tk.Button(
    root, 
    text="❌", 
    command=cerrar, 
    font=("Arial", 14, "bold"), 
    fg="red", 
    bg=COLOR_FONDO, 
    bd=0,
    padx=5,
    pady=0
)
btn_cerrar.place(x=560, y=5)

root.mainloop()