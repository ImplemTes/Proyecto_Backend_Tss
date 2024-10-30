import os
from fastapi import HTTPException
from database import create_connection
from models.abastecimiento import AbastecimientoCreate
import mysql.connector

def create_abastecimiento(detalle: AbastecimientoCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO abastecimiento(idproveedor,idalmacen,idproducto,cantidad_abastecimiento,fecha_abastecimiento,estado ) 
                          VALUES (%s,%s,%s,%s,%s,%s)''',
                       (detalle.idproveedor,detalle.idalmacen,detalle.idproducto,detalle.cantidad_abastecimiento,detalle.fecha_abastecimiento,detalle.estado))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error en la base de datos: {str(err)}")
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        conn.close()
    return {"message": "detalle creado con exito"}


def read_abastecimiento():
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
                    SELECT * FROM abastecimiento a
                    WHERE a.estado = 1;
                   """)
    detalles = cursor.fetchall()
    conn.close()
    return detalles


def select_detalleid(iddetalle: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM abastecimiento WHERE idabastecimiento = %s", (iddetalle,))
    detalle = cursor.fetchone()
    conn.close()

    if detalle is None:
        raise HTTPException(status_code=404, detail="detalle no encontrado")
    return detalle


def update_detalle(iddetalle: int, abastece: AbastecimientoCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()
    try:
        cursor.execute('''UPDATE abastecimiento SET idproveedor = %s, idalmacen = %s, idproducto = %s, cantidad_abastecimiento = %s,fecha_abastecimiento = %s
                          WHERE idabastecimiento = %s''',
                       (abastece.idproveedor, abastece.idalmacen, abastece.idproducto, abastece.cantidad_abastecimiento, abastece.fecha_abastecimiento))
        conn.commit()  # Confirmar los cambios en la base de datos
    except mysql.connector.Error as err:
        conn.rollback()  # Revertir cambios en caso de error
        raise HTTPException(status_code=400, detail=str(err))  # Lanzar una excepción HTTP
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

    return {"message": "detalle actualizado  con éxito"}


def delete_detalle(iddetalle: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()
    try:
        # Actualiza el estado de 1 a 0 (desactivado)
        cursor.execute('''UPDATE abastecimiento SET estado = 0
                          WHERE idabastecimiento = %s
                        ''', (iddetalle,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        conn.close()

    return {"message": "El detalle se eliminó con éxito"}

