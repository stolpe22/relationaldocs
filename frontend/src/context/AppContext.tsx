import { createContext, useContext, useReducer, useEffect, type ReactNode } from 'react'
import { api } from '../api/client'
import type { AnalysisResult, AppState, Job, Step, TunnelStatus, ConnectionConfig } from '../types'

type Action =
  | { type: 'SET_STEP'; payload: Step }
  | { type: 'SET_CONNECTION'; payload: ConnectionConfig }
  | { type: 'SET_TUNNEL'; payload: TunnelStatus | null }
  | { type: 'SET_SCHEMAS'; payload: string[] }
  | { type: 'SET_SELECTED_SCHEMA'; payload: string }
  | { type: 'SET_TABLES'; payload: string[] }
  | { type: 'SET_SELECTED'; payload: string[] }
  | { type: 'SET_ANALYSIS'; payload: AnalysisResult }
  | { type: 'SET_JOB'; payload: Job | null }
  | { type: 'RESET' }

const initial: AppState = {
  step: 'connect',
  connection: null,
  tunnel: null,
  schemas: [],
  selectedSchema: null,
  tables: [],
  selected: [],
  analysis: null,
  job: null,
}

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_STEP':
      return { ...state, step: action.payload }
    case 'SET_CONNECTION':
      return { ...state, connection: action.payload }
    case 'SET_TUNNEL':
      if (!action.payload?.active) {
        return { ...initial, tunnel: action.payload }
      }
      return { ...state, tunnel: action.payload }
    case 'SET_SCHEMAS':
      return { ...state, schemas: action.payload, step: 'schemas' }
    case 'SET_SELECTED_SCHEMA':
      return { ...state, selectedSchema: action.payload, tables: [], selected: [], step: 'tables' }
    case 'SET_TABLES':
      return { ...state, tables: action.payload }
    case 'SET_SELECTED':
      return { ...state, selected: action.payload, step: action.payload.length ? 'select' : 'tables' }
    case 'SET_ANALYSIS':
      return { ...state, analysis: action.payload, step: 'analyze' }
    case 'SET_JOB':
      return { ...state, job: action.payload, step: action.payload ? 'generate' : state.step }
    case 'RESET':
      return initial
    default:
      return state
  }
}

interface AppContextValue {
  state: AppState
  dispatch: React.Dispatch<Action>
}

const AppContext = createContext<AppContextValue | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initial)

  useEffect(() => {
    api.tunnelStatus().then(status => {
      dispatch({ type: 'SET_TUNNEL', payload: status })
    }).catch(() => {})
  }, [])

  return <AppContext.Provider value={{ state, dispatch }}>{children}</AppContext.Provider>
}

export function useApp() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used inside AppProvider')
  return ctx
}
