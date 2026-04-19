export type Step = 'connect' | 'schemas' | 'tables' | 'select' | 'analyze' | 'generate'

export interface ConnectionConfig {
  db_type: string
  host: string
  port: number
  service_name: string
  connection_type: 'service_name' | 'sid'
  user: string
  password: string
}

export interface TunnelConfig {
  ssh_host: string
  ssh_port: number
  ssh_user: string
  ssh_password: string
  remote_host: string
  remote_port: number
}
}

export interface TunnelStatus {
  active: boolean
  local_port: number | null
  remote_port: number | null
}

export interface TablesResponse {
  tables: string[]
  total: number
  limit: number
  offset: number
}

export interface TableSummary {
  name: string
  columns: number
  pks: number
  fks: number
  uks: number
  checks: number
  triggers: number
  referenced_tables: string[]
}

export interface ImplicitRelation {
  column: string
  table_1: string
  table_2: string
}

export interface AnalysisResult {
  total_tables: number
  total_columns: number
  total_pks: number
  total_fks: number
  total_uks: number
  total_checks: number
  total_triggers: number
  total_constraints: number
  external_references: string[]
  implicit_relations: ImplicitRelation[]
  tables: TableSummary[]
}

export type JobStatus = 'pending' | 'running' | 'done' | 'error'

export interface Job {
  job_id: string
  status: JobStatus
  error?: string | null
}

export interface AppState {
  step: Step
  connection: ConnectionConfig | null
  tunnel: TunnelStatus | null
  schemas: string[]
  selectedSchema: string | null
  tables: string[]
  selected: string[]
  analysis: AnalysisResult | null
  job: Job | null
}
