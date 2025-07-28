import serial
import mysql.connector
from mysql.connector import Error
import re
from conexion import conectar
puerto_serial = 'COM9'    
baud_rate = 9600
# Llama a la función conectar desde el módulo conexion.py
conexion = conectar()
if conexion is None:
    exit()

cursor = conexion.cursor()

try:
    ser = serial.Serial(puerto_serial, baud_rate, timeout=1)
    print(f"Puerto serial {puerto_serial} abierto")
except Exception as e:
    print(f"No se pudo abrir puerto serial {puerto_serial}: {e}")
    exit()
# Lee datos del puerto serial y los inserta en la base de datos
try:
    while True:
        # Espera a que haya datos disponibles en el puerto serial
        if ser.in_waiting > 0:
            linea = ser.readline().decode('utf-8').strip()
            # Procesa la línea recibida usando expresiones regulares en vez de un condicional
            m = re.match(r'Humedad:\s*([\d\.]+)%, Estado:\s*(\w+)', linea)
            if m:
                # Extrae los valores de humedad y estado
                humedad = float(m.group(1))
                estado = m.group(2)
                # Imprime los valores y los inserta en la base de datos esto para verificar que se están recibiendo correctamente
                print(f"Humedad: {humedad:.2f}%, Estado: {estado}")
                # Inserta los datos en la base de datos, se define segun el nombre de la tabla y los campos
                consulta = "INSERT INTO humedad_datos (humedad_porcentaje, estado) VALUES (%s, %s)"
                cursor.execute(consulta, (humedad, estado))
                conexion.commit()
            else:
                print(f"Línea no reconocida: {linea}")

except KeyboardInterrupt:
    # Usa un KeyboardInterrupt para terminar el programa 
    print("Programa terminado por el usuario")

finally:
    ser.close()
    cursor.close()
    conexion.close()
    print("Conexiones cerradas")

