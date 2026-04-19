---
paths:
  - "frontend/**/*"
---
# Regras do Frontend

## Stack
- **React + Vite** — SPA estático, sem SSR. Sem Next.js.
- TypeScript obrigatório (`strict: true`).
- Estilização exclusivamente com **Tailwind CSS v4** — sem CSS Modules, sem CSS-in-JS, sem arquivos `.module.css`.
- Tema escuro hard-coded via classes Tailwind e cores custom em `@theme` no `index.css`. Sem variáveis CSS globais para cores de componentes.
- Paleta padrão: surface `#0f1117`, card `#1a1d27`, border `#2e3148`, input `#141720`, accent `indigo-600`, muted `slate-500`.
- Comunicação com API via `fetch()` com wrapper centralizado em `src/api/client.ts`.
- Gerenciamento de estado com `useState` + `useContext` — sem Redux ou Zustand (estado não justifica lib externa).
- Layout responsivo para 1024px+ (sem foco em mobile).
- Componentes visuais esperados:
  1. **Formulário de conexão** — campos: host, port, service_name/SID, user, password, tipo de banco (select).
  2. **Formulário de túnel SSH** — campos: ssh_host, ssh_port, ssh_user, ssh_password, remote_host, remote_port. Sem campo de chave privada — autenticação exclusivamente por username + password (modelo DBeaver).
  3. **Seletor de tabelas** — busca com autocomplete, chips/tags para selecionadas.
  4. **Dashboard de análise** — cards com métricas: total tabelas, total colunas, total FKs, total triggers, total constraints.
  5. **Botão "Analisar Estrutura"** e **"Gerar Documentação"** — estados: idle, loading, success, error.
- Feedback visual obrigatório: spinners durante requests, toasts para sucesso/erro.
- Acessibilidade: labels em todos os inputs, aria-labels em botões com ícone, contraste mínimo AA.

## Máquina de estados
- O fluxo multi-etapa obrigatório: **conectar → listar schemas → listar tabelas → selecionar → analisar → gerar**.
- Implementar com `useContext` + `useReducer` num `AppContext` global. Estado mínimo:
  ```ts
  type Step = 'connect' | 'schemas' | 'tables' | 'select' | 'analyze' | 'generate'
  interface AppState {
    step: Step
    tunnel: TunnelStatus | null
    schemas: string[]
    tables: string[]
    selected: string[]
    job: Job | null
  }
  ```
- Cada etapa só é acessível se a anterior foi concluída.
- Etapas regridem se a conexão cair (ex: túnel fechado → volta para `connect`).
- Toda transição de estado passa pelo reducer — sem setState espalhado em handlers.

## Polling de jobs
- Após `POST /generate` retornar `job_id`, iniciar polling em `GET /jobs/{job_id}` a cada 2s com `useInterval` (hook customizado).
- Cancelar polling quando status for `done` ou `error` (cleanup no `useEffect`).
- Exibir barra de progresso indeterminada enquanto `status === 'running'`.
- Quando `done`: exibir botão de download apontando para `/api/v1/jobs/{job_id}/download`.