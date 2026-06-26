# Documentação de Arquitetura

- [Henry Lima Rech]

---

## Tecnologias Utilizadas

| Tecnologia | Versão | Motivo da escolha |
|---|---|---|
| Python | 3.11+ | Linguagem principal; suporte nativo a sqlite3 e tipagem moderna |
| Litestar | 2.x | Framework ASGI Python moderno, com suporte nativo a MiniJinja e roteamento por classes |
| MiniJinja | — | Engine de templates integrada ao Litestar; renderização server-side sem dependências extras |
| HTMX | 1.9 | Interatividade via atributos HTML; permite re-renderização parcial sem JavaScript customizado |
| Bootstrap 5 | 5.3 | Estilização via CDN; sem pipeline de build |
| SQLite | — | Banco relacional escolhido no lugar de PostgreSQL/MySQL pela simplicidade de setup zero: sem servidor, sem credenciais, apenas um arquivo `.db`. Atende ao requisito de SGBD relacional da disciplina |
| sqlite3 (stdlib) | — | Acesso ao banco via SQL puro, sem ORM (ex: SQLAlchemy). Escolha deliberada para tornar o papel do Repository completamente explícito: sem ORM, as classes Repository são inequivocamente o único lugar do código que contém SQL ou acessa a conexão com o banco |
| Chart.js | 4.x | Gráficos de linha e barra via CDN; sem etapa de build |

---

## Padrão Arquitetural: MVC

O projeto implementa o padrão **Model-View-Controller** de forma explícita na estrutura de pastas:

### Model — `app/models/entities.py`

Contém o único dataclass do projeto: `Enrollment`. Representa uma linha da tabela `enrollments` — um registro de matrícula por curso, ano, instituição e modalidade. A classe não contém SQL, não acessa banco de dados e não possui lógica de negócio. É a representação em memória de um ponto de dado, construída pelo Repository e passada ao Controller.

O schema relacional (instrução `CREATE TABLE`) vive em `scripts/schema.sql`, escrito como SQL puro.

### View — `app/templates/`

Templates MiniJinja organizados em:
- `base.html` + `navbar.html` — layout base reutilizado por todas as páginas
- `aggregated/` — páginas de dados agregados
- `evolution/` — páginas de análise de evolução
- `partials/` — fragmentos HTML retornados pelo servidor para re-renderização via HTMX

Os templates recebem dados via contexto e não contêm lógica de negócio nem acesso a banco.

### Controller — `app/controllers/enrollment_controller.py`

Classe `EnrollmentController` (Litestar `Controller`). Trata as requisições HTTP, chama os métodos do Repository, executa cálculos de negócio (ex: variação percentual de matrículas) e retorna respostas `Template`. Não contém SQL nem importa `sqlite3`.

A rota `/` (home) está definida diretamente em `app/main.py` como função handler, seguindo o mesmo padrão.

---

## Padrão de Persistência: Repository

`app/repositories/enrollment_repository.py` é o **único lugar no código** que contém strings SQL e manipula conexões `sqlite3`. Esta é uma escolha arquitetural deliberada:

- Controllers chamam métodos do Repository e recebem listas de dicionários ou objetos Python.
- Nenhuma camada além do Repository importa `sqlite3` ou escreve SQL.
- Sem ORM, este limite é completamente visível e verificável: basta inspecionar os imports do projeto.

O helper `app/repositories/db.py` centraliza a criação de conexões, lendo o caminho do banco via variável de ambiente `DATABASE_URL`.

---

## Papel do HTMX

Os filtros das páginas (modalidade, categoria administrativa, tipo de grau) usam HTMX para re-buscar apenas o fragmento relevante (gráfico + tabela) sem recarregar a página inteira. O servidor retorna um template parcial (`partials/`) com os dados já calculados. Toda a lógica permanece no Controller — nenhum JavaScript customizado é necessário.

---

## Ausência de Camada de Serviço

Não há camada de serviço/analytics separada. Os Controllers chamam o Repository diretamente e executam os cálculos de negócio (ex: `_pct_change` para variação percentual no impacto da pandemia) antes de passar os dados ao template. Isso mantém a arquitetura plana e fácil de seguir.

---

## Fluxo de Requisição

```
Requisição completa (navegação):

  Browser
    │  HTTP GET /enrollment/pandemic-impact
    ▼
  EnrollmentController.pandemic_impact()
    │  _repo.get_pandemic_totals(filter_type, filter_value)
    ▼
  EnrollmentRepository
    │  sqlite3 → SELECT ... FROM enrollments WHERE ...
    ▼
  SQLite (data/app.db)
    │  retorna linhas
    ▼
  EnrollmentRepository
    │  retorna list[dict]
    ▼
  EnrollmentController
    │  calcula _pct_change() → monta contexto
    ▼
  Template: enrollment/pandemic_impact.html
    │  renderiza HTML completo
    ▼
  Browser (página completa)


Re-renderização parcial via HTMX (mudança de filtro):

  Browser
    │  hx-get /enrollment/pandemic-impact/summary?filter_type=...
    ▼
  EnrollmentController.pandemic_impact_summary()
    │  (mesmo fluxo acima)
    ▼
  Template: partials/_pandemic_summary.html
    │  renderiza apenas o fragmento (gráfico + tabela)
    ▼
  HTMX substitui #pandemic-area no DOM
```
