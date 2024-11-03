import os
from fastapi import HTTPException
from database import create_connection
from models.abastecimiento import AbastecimientoCreate
from cruds import producto
import mysql.connector
from datetime import datetime

def create_abastecimiento(detalle: AbastecimientoCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    productoDet = producto.get_producto(detalle.idproducto)
    if not productoDet:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    
    stock_actualizado = productoDet['stock_producto'] + detalle.cantidad_abastecimiento

    # Genera la fecha actual en formato YYYY-MM-DD
    fecha_abastecimiento = datetime.now()

    try:

        cursor.execute("UPDATE Producto SET stock_producto = %s WHERE idproducto = %s", (stock_actualizado, detalle.idproducto))

        cursor.execute(
            '''INSERT INTO abastecimiento(idproveedor, idalmacen, idproducto, cantidad_abastecimiento, fecha_abastecimiento, estado) 
               VALUES (%s, %s, %s, %s, %s, %s)''',
            (detalle.idproveedor, detalle.idalmacen, detalle.idproducto, detalle.cantidad_abastecimiento, fecha_abastecimiento, detalle.estado)
        )

        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error en la base de datos: {str(err)}")
    finally:
        cursor.close()
        conn.close()

    return {"message": "Detalle creado con éxito"}


def read_abastecimiento():
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
                    SELECT  
                    a.idabastecimiento,
                    pr.idproveedor,  
                    pr.nombre_proveedor,  
                    al.idalmacen,
                    al.nombre_almacen,
                    p.idproducto,
                    p.nombre_producto,
                    a.cantidad_abastecimiento,
                    a.fecha_abastecimiento FROM abastecimiento a
                   join proveedor pr on a.idproveedor = pr.idproveedor
                   join almacen al on a.idalmacen = al.idalmacen
                   join producto p on a.idproducto = p.idproducto
                    WHERE a.estado = 1;
                   """)
    detalles = cursor.fetchall()
    conn.close()
    return detalles


def select_detalleid(iddetalle: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM abastecimiento WHERE idabastecimiento = %s", (iddetalle,))
        detalle = cursor.fetchone()
        
        if detalle is None:
            raise HTTPException(status_code=404, detail="Detalle no encontrado.")
            
        return detalle
    
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(err)}")
    
    finally:
        cursor.close()
        conn.close()

def update_detalle(iddetalle: int, DetalleActualizado: AbastecimientoCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        Detalle = select_detalleid(iddetalle)
        if not Detalle:
            raise HTTPException(status_code=404, detail="Detalle no encontrado.")
        
        productAntiguo = producto.get_producto(Detalle['idproducto'])
        if not productAntiguo:
            raise HTTPException(status_code=404, detail="Producto original no encontrado.")

        # Caso 1: Mismo producto, solo actualizar cantidad
        if Detalle['idproducto'] == DetalleActualizado.idproducto:
            stock_actualizado = productAntiguo['stock_producto'] - Detalle['cantidad_abastecimiento'] + DetalleActualizado.cantidad_abastecimiento
            cursor.execute("UPDATE Producto SET stock_producto = %s WHERE idproducto = %s", (stock_actualizado, DetalleActualizado.idproducto))
        # Caso 2: Producto diferente, actualizar ambos productos
        else: 
            # Actualiza el stock del producto antiguo
            stock_antiguo_actualizado = productAntiguo['stock_producto'] - Detalle['cantidad_abastecimiento']
            cursor.execute("UPDATE Producto SET stock_producto = %s WHERE idproducto = %s", (stock_antiguo_actualizado, Detalle['idproducto']))

            # Actualiza el stock del nuevo producto
            productoNuevo = producto.get_producto(DetalleActualizado.idproducto)
            if not productoNuevo:
                raise HTTPException(status_code=404, detail="Nuevo producto no encontrado.")
            
            stock_nuevo_actualizado = productoNuevo['stock_producto'] + DetalleActualizado.cantidad_abastecimiento
            cursor.execute(
                "UPDATE Producto SET stock_producto = %s WHERE idproducto = %s", 
                (stock_nuevo_actualizado, DetalleActualizado.idproducto)
            )
        fecha_abastecimiento = datetime.now()
        # Actualiza el detalle
        cursor.execute(
            '''UPDATE abastecimiento SET idproveedor = %s, idalmacen = %s, idproducto = %s, cantidad_abastecimiento = %s, fecha_abastecimiento = %s
               WHERE idabastecimiento = %s''',
            (DetalleActualizado.idproveedor, DetalleActualizado.idalmacen, DetalleActualizado.idproducto, DetalleActualizado.cantidad_abastecimiento,fecha_abastecimiento, iddetalle)
        )
        conn.commit()  
    except mysql.connector.Error as err:
        conn.rollback()  # Revertir cambios en caso de error
        raise HTTPException(status_code=400, detail=f"Error en la base de datos: {str(err)}") 
    finally:
        cursor.close()  
        conn.close()  

    return {"message": "Detalle actualizado con éxito"}

def delete_detalle(iddetalle: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()
    try:

        Detalle = select_detalleid(iddetalle)
        if not Detalle:
            raise HTTPException(status_code=404, detail="Detalle no encontrado.")
        
        productoDet = producto.get_producto(Detalle['idproducto'])
        if not productoDet:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")

        stock_actualizado = productoDet['stock_producto'] - Detalle['cantidad_abastecimiento']
        cursor.execute("UPDATE Producto SET stock_producto = %s WHERE idproducto = %s", (stock_actualizado, Detalle['idproducto']))

        # Actualiza el estado de 1 a 0 (desactivado/eliminado)
        cursor.execute("UPDATE abastecimiento SET estado = 0 WHERE idabastecimiento = %s", (iddetalle,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error en la base de datos: {str(err)}")
    finally:
        cursor.close()
        conn.close()
    return {"message": "El detalle se eliminó con éxito"}

