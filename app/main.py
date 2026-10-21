"""
Ponto de entrada da aplicação. É aqui que o FastAPI "liga as rotas".
"""

from datetime import date
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, get_db

# Cria as tabelas no banco SE elas ainda não existirem.
# Em projetos maiores de mercado isso seria feito com Alembic (migrations),
# mas para um projeto simples como o seu, isso resolve bem.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Reservas — Quadras de Vôlei",
    description="Sistema simples de reservas para 2 quadras de vôlei.",
    version="1.0.0",
)

# CORS: por padrão, um navegador bloqueia chamadas de um site para uma API
# em outro domínio. Aqui liberamos — mas em produção, troque "*" pela
# URL exata do seu front-end, nunca deixe "*" aberto de verdade.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["status"])
def raiz():
    return {"status": "online"}


# ---------- Quadras ----------

@app.post("/quadras", response_model=schemas.QuadraOut, status_code=status.HTTP_201_CREATED, tags=["quadras"])
def criar_quadra(quadra: schemas.QuadraCreate, db: Session = Depends(get_db)):
    return crud.criar_quadra(db, quadra)


@app.get("/quadras", response_model=list[schemas.QuadraOut], tags=["quadras"])
def listar_quadras(db: Session = Depends(get_db)):
    return crud.listar_quadras(db)


# ---------- Reservas ----------

@app.post("/reservas", response_model=schemas.ReservaOut, status_code=status.HTTP_201_CREATED, tags=["reservas"])
def criar_reserva(reserva: schemas.ReservaCreate, db: Session = Depends(get_db)):
    if crud.existe_conflito_de_horario(db, reserva):
        # 409 Conflict é o código HTTP correto para "isso já existe/colide".
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma reserva para esta quadra neste horário.",
        )
    try:
        return crud.criar_reserva(db, reserva)
    except IntegrityError:
        # Segunda linha de defesa: se por acaso duas requisições chegarem
        # ao mesmo tempo (condição de corrida), o banco barra pela
        # UniqueConstraint que criamos em models.py.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflito de horário detectado pelo banco de dados.",
        )


@app.get("/reservas", response_model=list[schemas.ReservaOut], tags=["reservas"])
def listar_reservas(data: date | None = None, db: Session = Depends(get_db)):
    return crud.listar_reservas(db, data)


@app.get("/reservas/{reserva_id}", response_model=schemas.ReservaOut, tags=["reservas"])
def buscar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = crud.buscar_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva não encontrada.")
    return reserva


@app.delete("/reservas/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["reservas"])
def deletar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    sucesso = crud.deletar_reserva(db, reserva_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva não encontrada.")
