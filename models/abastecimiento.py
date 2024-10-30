from pydantic import BaseModel
from datetime import datetime

class AbastecimientoCreate(BaseModel):
    idproveedor: int
    idalmacen: int
    idproducto: int
    cantidad_abastecimiento: int
    fecha_abastecimiento: datetime
    estado: int
