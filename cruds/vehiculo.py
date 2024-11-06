import os
from fastapi import HTTPException,UploadFile,File
from database import create_connection
from models.vehiculo import VehiculoCreate
import mysql.connector
from datetime import datetime
from typing import Optional
def create_vehiculo(auto: VehiculoCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()
    fecha_registro = datetime.now()
    try:
        cursor.execute('''INSERT INTO vehiculo(placa, marca, modelo, color, fecha_registro, estado)
                          VALUES (%s, %s, %s, %s, %s, %s)''',
                       (auto.placa, auto.marca, auto.modelo, auto.color, fecha_registro,1))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error en la base de datos: {str(err)}")
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        conn.close()
    return {"message": "Vehículo creado con éxito"}


def read_vehiculos():
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vehiculo WHERE estado = 1;")
    vehiculos = cursor.fetchall()
    conn.close()
    return vehiculos

def select_vehiculoid(idvehiculo: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vehiculo WHERE idvehiculo = %s", (idvehiculo,))
    vehiculo = cursor.fetchone()
    conn.close()

    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo


def update_vehiculo(idvehiculo: int, auto: VehiculoCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()
    fecha_registro = datetime.now()
    try:
        cursor.execute('''UPDATE vehiculo SET placa = %s, marca = %s, modelo = %s, color = %s, fecha_registro = %s, estado = %s
                          WHERE idvehiculo = %s''',
                       (auto.placa, auto.marca, auto.modelo, auto.color, fecha_registro, 1, idvehiculo))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        conn.close()

    return {"message": "Vehículo actualizado con éxito"}


def delete_vehiculo(idvehiculo: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()
    try:
        # Actualiza el estado del idvehiculo de 1 a 0 (desactivado)
        cursor.execute('''UPDATE vehiculo SET estado = 0 WHERE idvehiculo = %s''', (idvehiculo,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        conn.close()

    return {"message": "El vehículo se eliminó con éxito"}


def Extraer_Data( file: Optional[UploadFile]):
    try:
        print("LLegó el archivo correctamente al método Extraer_Data")
       
        # Procesa la imagen con OCR para obtener el texto de la placa
        plate_text = "000-000-000 "
        
        # Aquí puedes limpiar o validar el texto detectado según tus necesidades
        plate_text = plate_text.strip()  # Elimina espacios en blanco




        # Devuelve la placa detectada
        if not plate_text:
            raise ValueError("No se pudo extraer la placa del archivo")
        return plate_text
    except Exception as e:
        print(f"Error procesando el archivo en Extraer_Data: {e}")
        raise HTTPException(status_code=500, detail="No se detectó el archivo")
    


