# RelationalsDoc

Documentação automática e visual de bancos relacionais para Obsidian

---

## Visão Geral

O RelationalsDoc é uma ferramenta que conecta em bancos relacionais (inicialmente Oracle) e gera documentação completa das tabelas, relacionamentos, constraints e triggers em formato Markdown, pronta para ser usada no Obsidian. O objetivo é facilitar a análise de bancos grandes, trazendo a estrutura para um ambiente visual, com knowledge graph e navegação tipo mapa mental.

## Funcionalidades

- Conexão com bancos Oracle (com suporte a túnel SSH)
- Seleção de schema e tabelas para análise
- Análise automática dos metadados (colunas, constraints, relacionamentos, triggers)
- Geração de documentação Markdown compatível com Obsidian (wikilinks, navegação, knowledge graph)
- Interface web moderna e responsiva
- Pronto para escalar para outros bancos (SQL Server, PostgreSQL, etc.)

## Tecnologias Utilizadas

- **Frontend:** React + TypeScript + Vite
- **Backend:** Python 3.11+, FastAPI, oracledb
- **Containerização:** Docker (devcontainer)
- **Gerenciamento de dependências:** uv (Python), npm (Node)

## Roadmap Futuro

- Suporte a SQL Server, PostgreSQL e outros SGBDs
- Exportação direta para vaults do Obsidian
- Templates customizáveis de documentação
- Geração de diagramas ER automáticos
- Autenticação e multiusuário

## Como Rodar do Zero

### Pré-requisitos
- Docker (recomendado para ambiente dev)
- VS Code com extensão Remote - Containers (ou Dev Containers)
- Node.js 18+ (caso rode o frontend fora do container)

### Passos

1. **Clone o repositório:**
  ```bash
  git clone https://github.com/stolpe22/relationaldocs.git
  cd relationaldocs
  ```

2. **Abra no VS Code e use o Dev Container:**
  - Abra a pasta no VS Code e selecione "Reabrir no Container" (ou "Reopen in Container").
  - O ambiente já vem pronto com todas as dependências do backend.

3. **Configuração do ambiente:**
  - Copie os arquivos `.env.example` para `.env` tanto em `backend/` quanto em `frontend/` e ajuste as variáveis se necessário.

4. **Instale as dependências do frontend:**
  ```bash
  cd frontend
  npm install
  ```

5. **Rodando em modo desenvolvimento:**
  - **Backend:**
    ```bash
    make dev
    ```
  - **Frontend:**
    ```bash
    npm run dev
    ```

6. **Acesse a aplicação:**
  - Frontend: [http://localhost:5173](http://localhost:5173)
  - API: [http://localhost:8000/docs](http://localhost:8000/docs)

7. **Conecte ao banco Oracle, selecione as tabelas e gere a documentação!**

## Estrutura do Projeto

```
relationalsdoc/
  backend/
    src/
    tests/
    pyproject.toml
    ...
  frontend/
    src/
    public/
    package.json
    ...
  .devcontainer/
  CLAUDE.md
  ...
```

## Contribuição

Pull requests são bem-vindos! Sinta-se à vontade para abrir issues com sugestões ou bugs.



## Observação sobre uso de túnel SSH

Se você estiver usando túnel SSH para conectar ao banco Oracle, utilize como porta do banco de dados a porta local que o frontend mostrar ao abrir o túnel (exemplo: 33989). Não use a porta padrão 1521, a menos que o túnel tenha sido explicitamente aberto nela.

---

> Projeto criado para facilitar a análise e documentação de bancos relacionais, trazendo a estrutura para o universo visual do Obsidian. Em breve, mais SGBDs e recursos!