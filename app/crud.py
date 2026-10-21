"""
'CRUD' = Create, Read, Update, Delete.
A ideia desta camada é simples: o main.py (as rotas) NUNCA fala direto
com o banco. Ele chama essas funções. Isso separa "o que a API expõe"
de "como o banco é manipulado" — se um dia você trocar de banco,
só este arquivo muda.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from . import models, schemas


# ---------- Quadra ----------

def criar_quadra(db: Session, quadra: schemas.QuadraCreate) -> models.Quadra:
    nova_quadra = models.Quadra(nome=quadra.nome)
    db.add(nova_quadra)
    db.commit()
    db.refresh(nova_quadra)  # busca de volta o id gerado pelo banco
    return nova_quadra


def listar_quadras(db: Session):
    return db.query(models.Quadra).all()


# ---------- Reserva ----------

def existe_conflito_de_horario(db: Session, reserva: schemas.ReservaCreate) -> bool:
    """
    Verifica se já existe reserva para a MESMA quadra, MESMA data,
    e com sobreposição de horário.

    A lógica de sobreposição de intervalos é clássica:
    dois intervalos [A_inicio, A_fim) e [B_inicio, B_fim) se sobrepõem
    quando A_inicio < B_fim E B_inicio < A_fim.
    """
    conflito = (
        db.query(models.Reserva)
        .filter(
            models.Reserva.quadra_id == reserva.quadra_id,
            models.Reserva.data == reserva.data,
            and_(
                models.Reserva.hora_inicio < reserva.hora_fim,
                models.Reserva.hora_fim > reserva.hora_inicio,
            ),
        )
        .first()
    )
    return conflito is not None


def criar_reserva(db: Session, reserva: schemas.ReservaCreate) -> models.Reserva:
    nova_reserva = models.Reserva(**reserva.model_dump())
    db.add(nova_reserva)
    db.commit()
    db.refresh(nova_reserva)
    return nova_reserva


def listar_reservas(db: Session, data=None):
    query = db.query(models.Reserva)
    if data is not None:
        query = query.filter(models.Reserva.data == data)
    return query.order_by(models.Reserva.data, models.Reserva.hora_inicio).all()


def buscar_reserva(db: Session, reserva_id: int):
    return db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()


def deletar_reserva(db: Session, reserva_id: int) -> bool:
    reserva = buscar_reserva(db, reserva_id)
    if reserva is None:
        return False
    db.delete(reserva)
    db.commit()
    return True
