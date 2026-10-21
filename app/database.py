"""
Este arquivo cuida de UMA responsabilidade só: abrir a porta para o banco de dados.

É aqui que a "ponte" entre o Python e o PostgreSQL do Render é construída.
Nenhuma regra de negócio mora aqui — só a conexão.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carrega as variáveis do arquivo .env para dentro do ambiente do Python.
# Isso é o que permite que a senha do banco NUNCA apareça escrita no código.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não foi encontrada. Crie um arquivo .env "
        "baseado no .env.example antes de rodar a aplicação."
    )

# O Render exige conexão criptografada (SSL) para acesso externo ao banco.
# Se a URL já não pedir isso explicitamente, garantimos aqui.
if "sslmode" not in DATABASE_URL:
    separador = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{separador}sslmode=require"

# O "engine" é o motor que sabe falar o dialeto do PostgreSQL.
# pool_pre_ping=True evita erros estranhos quando a conexão cai por inatividade
# (comum em planos free do Render, que "dormem" o banco às vezes).
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal é uma "fábrica" de sessões. Cada requisição à API vai pedir
# uma sessão nova, usar, e devolver — nunca compartilhamos sessão entre requisições.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base é a classe da qual todos os nossos modelos (tabelas) vão herdar.
Base = declarative_base()


def get_db():
    """
    Esta função é usada pelo FastAPI como 'dependency'.
    Ela abre uma sessão, entrega para a rota usar, e GARANTE que fecha
    no final — mesmo se der erro no meio do caminho (por isso o try/finally).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
