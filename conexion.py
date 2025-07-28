import mysql.connector

def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="proyectofinal_aplicada"
    )
    return conexion

