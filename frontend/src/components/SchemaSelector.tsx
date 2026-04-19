import { useState } from 'react'
import { api } from '../api/client'
import { useApp } from '../context/AppContext'
import { Spinner } from './Spinner'

interface Props {
  onSuccess: (msg: string) => void
  onError: (msg: string) => void
}

export function SchemaSelector({ onSuccess, onError }: Props) {
  const { state, dispatch } = useApp()
  const [loading, setLoading] = useState(false)

  async function handleSelect(schema: string) {
    if (!state.connection) return
    setLoading(true)
    try {
      const res = await api.listTables(state.connection, schema)
      dispatch({ type: 'SET_SELECTED_SCHEMA', payload: schema })
      dispatch({ type: 'SET_TABLES', payload: res.tables })
      onSuccess(`${res.total} tabelas encontradas em ${schema}.`)
    } catch (e) {
      onError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-md rounded-xl bg-[#1a1d27] border border-[#2e3148] p-6 shadow-xl">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-lg font-semibold text-slate-100">Selecionar Schema</h2>
        {loading && <Spinner size="md" />}
      </div>

      <ul className="flex flex-col gap-1.5">
        {state.schemas.map(s => (
          <li key={s}>
            <button
              onClick={() => handleSelect(s)}
              disabled={loading}
              className={`w-full text-left px-4 py-2.5 rounded-md text-sm font-medium transition-colors disabled:opacity-50 ${
                s === state.selectedSchema
                  ? 'bg-indigo-600 text-white'
                  : 'bg-[#141720] hover:bg-[#2e3148] text-slate-300 border border-[#2e3148]'
              }`}
            >
              {s}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
