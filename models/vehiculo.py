from pydantic import BaseModel

class VehiculoCreate(BaseModel):
    placa: str
    marca: str
    modelo: str
    color: str
