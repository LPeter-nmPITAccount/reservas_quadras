# Sistema de Reservas — Quadras de Vôlei

## 1. Como rodar localmente

```bash
# cria e ativa um ambiente virtual (isola as dependências deste projeto)
python3 -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate

# instala as dependências
pip install -r requirements.txt

# copia o arquivo de exemplo e preenche com os dados reais
cp .env.example .env
```

## 2. Pegando a URL de conexão no Render

1. Entre no [dashboard do Render](https://dashboard.render.com).
2. Abra o banco PostgreSQL que você criou.
3. Procure por **"External Database URL"** (não a "Internal" — essa só
   funciona se sua API também estiver hospedada no Render, na mesma região).
4. Copie essa URL inteira e cole no `.env`, na variável `DATABASE_URL`.

Formato típico:
```
postgresql://usuario:senha@dpg-xxxxx.oregon-postgres.render.com/nome_do_banco
```

⚠️ **Nunca** coloque essa URL direto no código ou faça commit do `.env`.
O `.gitignore` já está configurado pra evitar isso.

## 3. Criando as tabelas

Você não precisa rodar nenhum script separado: quando a aplicação sobe
pela primeira vez, a linha `models.Base.metadata.create_all(bind=engine)`
em `main.py` cria automaticamente as tabelas `quadras` e `reservas`
caso elas não existam.

## 4. Subindo a API

```bash
uvicorn app.main:app --reload
```

Depois, abra `http://127.0.0.1:8000/docs` — o FastAPI gera essa página
de testes interativa sozinho, sem você escrever nada a mais.

## 5. Cadastrando as 2 quadras (uma vez só)

Pelo `/docs`, ou via curl:

```bash
curl -X POST http://127.0.0.1:8000/quadras -H "Content-Type: application/json" -d '{"nome": "Quadra 1"}'
curl -X POST http://127.0.0.1:8000/quadras -H "Content-Type: application/json" -d '{"nome": "Quadra 2"}'
```

## 6. Testando uma reserva

```bash
curl -X POST http://127.0.0.1:8000/reservas -H "Content-Type: application/json" -d '{
  "quadra_id": 1,
  "nome_cliente": "Maria",
  "telefone": "86999999999",
  "data": "2026-10-25",
  "hora_inicio": "19:00:00",
  "hora_fim": "20:00:00"
}'
```

Tente criar outra reserva na mesma quadra, data e horário — a API deve
responder `409 Conflict`.

## 7. Próximos passos (quando quiser evoluir)

- **Alembic**: para controlar mudanças futuras no formato das tabelas
  sem perder dados.
- **Autenticação**: se este sistema sair do seu uso pessoal e virar
  algo público, adicione um esquema de login (ex.: `fastapi-users` ou
  JWT simples) antes de expor `POST`/`DELETE` para qualquer pessoa.
- **Deploy no Render como Web Service**: aponte o "Start Command" para
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
