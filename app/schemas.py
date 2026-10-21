"""
Schemas são os "formulários" que a API aceita e devolve.
Repare: eles são DIFERENTES dos models.py. Os models descrevem o BANCO.
Os schemas descrevem a API. Essa separação é uma prática de mercado
importante — ela evita que você exponha colunas internas sem querer,
e permite validar os dados ANTES de eles chegarem perto do banco.
"""

from datetime import date, time, datetime
from pydantic import BaseModel, Field, field_validator


# ---------- Quadra ----------

class QuadraBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=50)


class QuadraCreate(QuadraBase):
    pass


class QuadraOut(QuadraBase):
    id: int

    class Config:
        from_attributes = True  # permite converter direto de um objeto SQLAlchemy


# ---------- Reserva ----------

class ReservaBase(BaseModel):
    quadra_id: int
    nome_cliente: str = Field(..., min_length=1, max_length=100)
    telefone: str = Field(..., min_length=8, max_length=20)
    data: date
    hora_inicio: time
    hora_fim: time

    @field_validator("hora_fim")
    @classmethod
    def hora_fim_depois_do_inicio(cls, hora_fim, info):
        hora_inicio = info.data.get("hora_inicio")
        if hora_inicio and hora_fim <= hora_inicio:
            raise ValueError("hora_fim precisa ser depois de hora_inicio")
        return hora_fim


class ReservaCreate(ReservaBase):
    pass


class ReservaOut(ReservaBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True
