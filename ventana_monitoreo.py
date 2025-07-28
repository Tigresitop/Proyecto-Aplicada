import sys
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from conexion import conectar
from datetime import datetime
import subprocess
# Configuración de la conexión a la base de datos
actualizacion_activa = True
if conectar() is None:
    exit()
# Función para obtener el último ID de la tabla para obtener nuevos datos en tiempo real
def obtener_ultimo_id(conexion):
    """Obtiene ultimo ID"""
# El try y except maneja errores de conexión y consulta
    try:
# el cursor se usa para ejecutar consultas SQL, que lo definimos con la función cursor()
        cursor = conexion.cursor()
# Consulta para obtener el máximo ID de la tabla, utilizamos SELECT para listar.
        cursor.execute("SELECT MAX(id) FROM humedad_datos")
# fetchone() obtiene el primer resultado de la consulta
# Con un condicional se verifica si el resultado es None o 0 y devolvemos
        resultado = cursor.fetchone()
        return resultado[0] if resultado and resultado[0] else 0
    except Error as e:
        print("Error al obtener último id:", e)
        return 0
    finally:
        if cursor: cursor.close()
# Función para obtener nuevos datos desde un ID específico
# Esta función recibe un ID y devuelve todos los registros con ID mayor al especificado
def obtener_datos_nuevos(conexion, desde_id):
    """Obtener datos especificos"""
    try:
# El cursor se usa para ejecutar consultas SQL
        cursor = conexion.cursor()
# Usamos una consulta con una nueva variable, ordenamos los resultados por ID ascendente con ORDER BY
# y WHERE filtra los resultados para obtener solo aquellos con ID mayor al especificado
        query = "SELECT id, fecha_hora, humedad_porcentaje, estado FROM humedad_datos WHERE id > %s ORDER BY id ASC"
# Ejecutamos la consulta con el ID proporcionado, pasando el parametro de la consulta y el id
        cursor.execute(query, (desde_id,))
# fetchall() obtiene todos los resultados de la consulta
        return cursor.fetchall()
    except Error as e:
        print("Error al consultar MySQL:", e)
        return []
    finally:
        if cursor: cursor.close()

def cargar_datos_iniciales(tree, insertar_fila):
    """Carga los datos iniciales en la tabla con separadores"""
    conexion = conectar()
    if not conexion:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos")
        return 0

    try:
        cursor = conexion.cursor()
# Ejecutamos una consulta para obtener los últimos 100 registros de la tabla humedad_datos
        cursor.execute("SELECT id, fecha_hora, humedad_porcentaje, estado FROM humedad_datos ORDER BY id DESC LIMIT 100")
# fetchall() obtiene todos los resultados de la consulta
        datos = cursor.fetchall()
# Si no hay datos, mostramos un mensaje y devolvemos 0
# Si hay datos, los insertamos en la tabla
        for item in tree.get_children():
# eliminamos los elementos existentes en el árbol para evitar duplicados
            tree.delete(item)
# Recorremos los datos en orden inverso para que el último registro aparezca al final
# Usamos reversed() para invertir el orden de los datos
# y llamamos a la función insertar_fila para insertar cada fila en el árbol
        for fila in reversed(datos):
            insertar_fila(fila)
# Movemos la vista del árbol al final para mostrar los registros más recientes
        return datos[0][0] if datos else 0
    except Error as e:
        print("Error al cargar datos iniciales:", e)
        return 0
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

# Sirve para refrescar los datos de la tabla manualmente
# Se puede usar un botón para llamar a esta función
def refrescar_datos(tree, ultimo_id_label, status_label, insertar_fila):
    """Actualiza la tabla con nuevos datos"""
    conexion = conectar()
    if not conexion:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos")
        return 0

    try:
# Obtenemos el último ID actual de la etiqueta llamando a la función obtener_ultimo_id
        nuevo_ultimo_id = obtener_ultimo_id(conexion)
# Obtenemos el último ID mostrado en la etiqueta 
        ultimo_id = int(ultimo_id_label.cget("text").split(": ")[1])
# Esta condición verifica si hay nuevos datos y si el nuevo ID es mayor al último ID mostrado
# Si es así, obtenemos los nuevos datos desde la base de datos
        if nuevo_ultimo_id > ultimo_id:
            nuevos_datos = obtener_datos_nuevos(conexion, ultimo_id)
            if nuevos_datos:
# Si hay nuevos datos, los insertamos en la tabla
                for fila in nuevos_datos:
                    insertar_fila(fila)
# Movemos la vista del árbol al final para mostrar los nuevos registros
                tree.yview_moveto(1)
                ultimo_id_label.config(text=f"Último ID: {nuevo_ultimo_id}")
# Actualizamos la etiqueta de estado con la hora actual y el número de nuevos registros, esto se hace con datetime.now().strftime('%H:%M:%S')
# y devolvemos el nuevo último ID
                status_label.config(text=f"Actualizado manual: {datetime.now().strftime('%H:%M:%S')} | +{len(nuevos_datos)} registros")
                return nuevo_ultimo_id
# Si no hay nuevos datos, actualizamos la etiqueta de estado con la hora actual
        status_label.config(text=f"No hay nuevos datos | {datetime.now().strftime('%H:%M:%S')}")
        return ultimo_id
    except Error as e:
        print("Error al refrescar datos:", e)
# Actualizamos la etiqueta de estado con el error
        status_label.config(text=f"Error al actualizar: {e}")
        return ultimo_id
    finally:
        if conexion: conexion.close()
# Todo esto esta hecho con IA, no sabia como hacerlo a tiempo real 
def actualizacion_automatica(tree, ultimo_id_label, status_label, insertar_fila):
    """Actualización automática cada 2 segundos"""
    global actualizacion_activa

    if actualizacion_activa:
        status_label.config(text=f"Actualizando... {datetime.now().strftime('%H:%M:%S')}")
        conexion = conectar()
        if not conexion:
            status_label.config(text="Error de conexión")
            tree.after(2000, lambda: actualizacion_automatica(tree, ultimo_id_label, status_label, insertar_fila))
            return

        try:
            nuevo_ultimo_id = obtener_ultimo_id(conexion)
            ultimo_id = int(ultimo_id_label.cget("text").split(": ")[1])

            if nuevo_ultimo_id > ultimo_id:
                nuevos_datos = obtener_datos_nuevos(conexion, ultimo_id)
                if nuevos_datos:
                    for fila in nuevos_datos:
                        insertar_fila(fila)
                    tree.yview_moveto(1)
                    ultimo_id_label.config(text=f"Último ID: {nuevo_ultimo_id}")
                    status_label.config(text=f"Actualizado auto: {datetime.now().strftime('%H:%M:%S')} | +{len(nuevos_datos)} registros")
            else:
                status_label.config(text=f"Esperando datos... {datetime.now().strftime('%H:%M:%S')}")
        except Error as e:
            print("Error en actualización automática:", e)
            status_label.config(text=f"Error: {e}")
        finally:
            if conexion: conexion.close()

        tree.after(4000, lambda: actualizacion_automatica(tree, ultimo_id_label, status_label, insertar_fila))

def limpiar_registros(tree, ultimo_id_label, status_label):
    """Limpia todos los registros de la tabla"""
    if not messagebox.askyesno("Confirmar", "¿Está seguro que desea limpiar todos los registros?"):
        return

    for item in tree.get_children():
        tree.delete(item)
    status_label.config(text="Registros limpiados")
    current_id = ultimo_id_label.cget("text").split(": ")[1]
    status_label.after(3000, lambda: status_label.config(text=f"Listo | Último ID: {current_id}"))

def toggle_actualizacion(boton_toggle, tree, ultimo_id_label, status_label, insertar_fila):
    """Activa/desactiva la actualización automática"""
    global actualizacion_activa
    actualizacion_activa = not actualizacion_activa

    if actualizacion_activa:
        boton_toggle.config(text="⏸ Pausar Actualización")
        actualizacion_automatica(tree, ultimo_id_label, status_label, insertar_fila)
        status_label.config(text="Actualización automática reanudada")
    else:
        boton_toggle.config(text="▶ Reanudar Actualización")
        status_label.config(text="Actualización automática pausada")

def on_closing(root):
    global actualizacion_activa
    actualizacion_activa = False
    root.destroy()
# Esta función se llama al cerrar la ventana, detiene la actualización automática y cierra la ventana
# Ademas pasa un parametro root de la ventana actual para poder destruirla
# Luego intenta abrir la ventana principal de nuevo
# root.destroy() cierra la ventana actual
def volver_a_principal(root):
    global actualizacion_activa
    actualizacion_activa = False  # Detener actualización automática
    root.destroy()
    try:
        subprocess.Popen([sys.executable, "ventana_principal.py"])
    except Exception as e:
        subprocess.Popen(["python", "ventana_principal.py"])

# Esta función es la carga principal de la ventana, es facil de hacer, solo se define el diseño y los botones
# y se llama a las funciones de carga de datos y actualización automática
def main():
    root = tk.Tk()
    root.title("Monitoreo")
    root.geometry("800x500")
    root.configure(bg="#f0fff0")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#f0fff0")
    style.configure("TLabel", background="#f0fff0", foreground="#1B5E20")
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"),
                    background="#4CAF50", foreground="white")
    style.configure("Treeview", rowheight=25, font=("Helvetica", 9),
                    fieldbackground="#e8f5e9", background="#e8f5e9")
    style.map("Treeview", background=[('selected', '#2E7D32')])
    style.map("Treeview.Heading", background=[('active', '#388E3C')])
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    # header = ttk.Label(main_frame, text="Monitoreo", font=("Helvetica", 14, "bold"))
    # header.pack(anchor="w", pady=(0,10))
    header = ttk.Label(
    main_frame,
    text="MONITOREO",
    font=("Helvetica", 16, "bold"),
    foreground="#0000FF",    # azul puro
    background="#f0fff0"     # mismo fondo que tu ventana
    )
    header.pack(pady=(0, 10))
    table_frame = ttk.Frame(main_frame)
    table_frame.pack(fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(table_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree = ttk.Treeview(
        table_frame,
        columns=("ID", "Fecha y Hora", "Humedad (%)", "Estado"),
        show='headings',
        yscrollcommand=scrollbar.set,
        selectmode="none"
    )
    scrollbar.config(command=tree.yview)

    for col, width in [("ID",50), ("Fecha y Hora",180), ("Humedad (%)",100), ("Estado",100)]:
        tree.heading(col, text=col, anchor=tk.CENTER)
        tree.column(col, width=width, anchor=tk.CENTER)

    tree.pack(fill=tk.BOTH, expand=True)
    info_frame = ttk.Frame(main_frame)
    info_frame.pack(fill=tk.X, pady=5)
    ultimo_id_label = ttk.Label(info_frame, text="Último ID: 0", font=("Helvetica", 9))
    ultimo_id_label.pack(side=tk.LEFT)
    status_label = ttk.Label(info_frame, text="Estado: Conectando...", font=("Helvetica", 9))
    status_label.pack(side=tk.LEFT, padx=20)

    def insertar_fila_con_separador(fila):
        tree.insert("", tk.END, values=fila)
        tree.insert("", tk.END, values=("—"*5, "—"*20, "—"*10, "—"*10), tags=('separador',))

    tree.tag_configure('separador', background="#f0fff0", foreground="#A5D6A7", font=('Courier', 8, 'italic'))
    last_id = cargar_datos_iniciales(tree, insertar_fila_con_separador)
    ultimo_id_label.config(text=f"Último ID: {last_id}")
    status_label.config(text="Estado: Conectado")

    bottom_controls = ttk.Frame(main_frame)
    bottom_controls.pack(fill=tk.X, side=tk.BOTTOM, anchor="e", pady=5, padx=10)

    try:
        img = tk.PhotoImage(file="refresh_icon.png")
        icon_devolver = tk.PhotoImage(file="assets/devolver.png")
        icon_devolver = icon_devolver.subsample(12, 12)
        img = img.subsample(10, 10) 
    except:
        img = None  
    boton_volver = tk.Button(
    bottom_controls,
    image=icon_devolver,
    bg="#AED581",
    relief=tk.FLAT,
    command=lambda: volver_a_principal(root)
    )
    boton_volver.image = icon_devolver
    boton_volver.pack(side=tk.LEFT, padx=5, pady=5)

    boton_toggle = tk.Button(
        bottom_controls,
        image=img,
        compound="left",
        bg="white",
        fg="#1B5E20",
        font=("Helvetica", 9, "bold"),
        relief=tk.FLAT,
        command=lambda: refrescar_datos(tree, ultimo_id_label, status_label, insertar_fila_con_separador)
    )

    boton_toggle.image = img
    boton_toggle.pack(side=tk.RIGHT, padx=5, ipadx=5, ipady=3)

    boton_limpiar = tk.Button(
        bottom_controls,
        text="Limpiar",
        bg="#FF9800",
        fg="white",
        font=("Helvetica", 9, "bold"),
        relief=tk.FLAT,
        command=lambda: limpiar_registros(tree, ultimo_id_label, status_label)
    )
    boton_limpiar.pack(side=tk.RIGHT, padx=5, ipadx=5, ipady=3)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    actualizacion_automatica(tree, ultimo_id_label, status_label, insertar_fila_con_separador)
    root.mainloop()

if __name__ == "__main__":
    main()
