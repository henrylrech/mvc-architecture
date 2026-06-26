# Matrículas Região Sul — Aplicação Web MVC

Aplicação web para análise de dados de matrículas de graduação na Região Sul do Brasil.
Desenvolvida com Litestar (Python/ASGI), seguindo o padrão arquitetural MVC.

---

## Pré-requisitos

- Python 3.11+
- pip

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Configuração do banco de dados

O caminho do arquivo SQLite é configurável via variável de ambiente `DATABASE_URL`.

| Variável       | Exemplo                        | Padrão         |
|----------------|-------------------------------|----------------|
| `DATABASE_URL` | `sqlite:///data/app.db`       | `data/app.db`  |

Se a variável não estiver definida, o banco será criado em `data/app.db` (relativo à raiz do projeto).

Para definir manualmente (opcional):

```bash
# Windows (cmd)
set DATABASE_URL=sqlite:///data/app.db

# Windows (PowerShell)
$env:DATABASE_URL = "sqlite:///data/app.db"

# Linux/macOS
export DATABASE_URL=sqlite:///data/app.db
```

---

## Importação dos dados (executar uma vez)

Este script lê o CSV e popula o banco SQLite. Deve ser executado antes de iniciar a aplicação.

```bash
python scripts/import_csv.py
```

O script irá:
- Criar o arquivo `data/app.db` (se não existir)
- Aplicar o schema (`scripts/schema.sql`)
- Importar todos os registros do CSV
- Exibir um resumo de sanidade (total de linhas, range de anos, cursos e IES distintos)

---

## Executando a aplicação

```bash
uvicorn app.main:app --reload
```

Ou via CLI do Litestar:

```bash
litestar run --reload
```

A aplicação estará disponível em: **http://127.0.0.1:8000**

---

## Estrutura do projeto

```
app/
  main.py                        # instância Litestar + rotas
  models/entities.py             # dataclass Enrollment (Model)
  repositories/
    db.py                        # helper de conexão SQLite
    enrollment_repository.py     # Repository (único lugar com SQL)
  controllers/
    enrollment_controller.py     # Controller (todas as rotas)
  templates/                     # Views (MiniJinja)
    base.html / navbar.html
    aggregated/
    evolution/
    partials/                    # fragmentos HTMX
scripts/
  schema.sql                     # DDL do banco
  import_csv.py                  # importação única do CSV
data/
  Matriculados Região Sul.csv
  app.db                         # gerado pelo import_csv.py
docs/
  ARCHITECTURE.md
```

---

## Funcionalidades

| Rota | Descrição |
|------|-----------|
| `/` | Página inicial com resumo |
| `/aggregated/enrollment-by-year` | Total de matrículas por ano (filtro: modalidade) |
| `/aggregated/top-courses/Presencial` | Top 10 cursos presenciais em 2023 |
| `/aggregated/top-courses/EaD` | Top 10 cursos EaD em 2023 |
| `/aggregated/top-institutions/Presencial` | Top IES presencial em 2023 (filtro: pública/privada) |
| `/aggregated/top-institutions/EaD` | Top IES EaD em 2023 (filtro: pública/privada) |
| `/evolution/course-timeline` | Evolução de matrículas por curso ao longo dos anos |
| `/evolution/pandemic-impact` | Impacto da pandemia 2019–2022 |
