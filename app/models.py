"""
Aqui moram as TABELAS do banco, descritas como classes Python.
Isso se chama ORM (Object-Relational Mapping): você escreve classes,
o SQLAlchemy traduz para SQL por baixo dos panos.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Time,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from .database import Base


class Quadra(Base):
    __tablename__ = "quadras"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True)
    # Ex.: "Quadra 1", "Quadra 2". Como você disse que são só 2 quadras fixas,
    # essa tabela existe mais para ORGANIZAR do que para crescer sem limite.

    reservas = relationship("Reserva", back_populates="quadra")


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    quadra_id = Column(Integer, ForeignKey("quadras.id"), nullable=False)
    nome_cliente = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    data = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    quadra = relationship("Quadra", back_populates="reservas")

    __table_args__ = (
        # Isso impede, no próprio banco, que a MESMA quadra seja cadastrada
        # duas vezes com EXATAMENTE a mesma data e hora de início.
        # É uma segunda linha de defesa — a primeira é a verificação que
        # faremos em Python antes de salvar (vem em crud.py).
        UniqueConstraint("quadra_id", "data", "hora_inicio", name="uq_quadra_horario"),
    )
