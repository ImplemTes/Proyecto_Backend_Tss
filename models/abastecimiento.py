from pydantic import BaseModel

class AbastecimientoCreate(BaseModel):
    idproveedor: int
    idalmacen: int
    idproducto: int
    cantidad_abastecimiento: int
    estado: int
