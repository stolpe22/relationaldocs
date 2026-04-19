import type {
  AnalysisResult,
  ConnectionConfig,
  Job,
  TablesResponse,
  TunnelConfig,
  TunnelStatus,
} from '../types'

const BASE = '/api/v1'
const API_KEY = import.meta.env.VITE_API_KEY ?? ''

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
      ...init.headers,
    },
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body?.detail ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  testConnection: (body: ConnectionConfig) =>
    request<{ success: boolean; message: string }>(`${BASE}/connections/test`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  openTunnel: (body: TunnelConfig) =>
    request<TunnelStatus>(`${BASE}/tunnels/open`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  closeTunnel: () =>
    request<TunnelStatus>(`${BASE}/tunnels/close`, { method: 'POST' }),

  tunnelStatus: () =>
    request<TunnelStatus>(`${BASE}/tunnels/status`),

  listSchemas: (conn: ConnectionConfig) => {
    const p = new URLSearchParams({
      db_type: conn.db_type,
      host: conn.host,
      port: String(conn.port),
      service: conn.service_name,
      user: conn.user,
      password: conn.password,
    })
    return request<{ schemas: string[] }>(`${BASE}/schemas?${p}`)
  },

  listTables: (conn: ConnectionConfig, schema: string, limit = 10000, offset = 0) => {
    const p = new URLSearchParams({
      schema,
      db_type: conn.db_type,
      host: conn.host,
      port: String(conn.port),
      service: conn.service_name,
      user: conn.user,
      password: conn.password,
      limit: String(limit),
      offset: String(offset),
    })
    return request<TablesResponse>(`${BASE}/tables?${p}`)
  },

  analyse: (schema: string, tables: string[]) =>
    request<AnalysisResult>(`${BASE}/analysis`, {
      method: 'POST',
      body: JSON.stringify({ schema_name: schema, tables }),
    }),

  generate: (schema: string, tables: string[]) =>
    request<{ job_id: string }>(`${BASE}/generate`, {
      method: 'POST',
      body: JSON.stringify({ schema_name: schema, tables }),
    }),

  jobStatus: (jobId: string) =>
    request<Job>(`${BASE}/jobs/${jobId}`),

  downloadZip: async (jobId: string): Promise<void> => {
    const res = await fetch(`${BASE}/jobs/${jobId}/download`, {
      headers: { 'X-Api-Key': API_KEY },
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body?.detail ?? `HTTP ${res.status}`)
    }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `docs_${jobId.slice(0, 8)}.zip`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  },
}
