import os
from fastapi import HTTPException
from database import create_connection
from models.vehiculo import VehiculoCreate
import mysql.connector
from datetime import datetime

def create_vehiculo(auto: VehiculoCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()
    fecha_registro = datetime.now()
    try:
        cursor.execute('''INSERT INTO vehiculo(placa, marca, modelo, color, fecha_registro, estado)
                          VALUES (%s, %s, %s, %s, %s, %s)''',
                       (auto.placa, auto.marca, auto.modelo, auto.color, fecha_registro, auto.estado))
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
                       (auto.placa, auto.marca, auto.modelo, auto.color, fecha_registro, auto.estado, idvehiculo))
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