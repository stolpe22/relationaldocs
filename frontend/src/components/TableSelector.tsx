import { useState } from 'react'
import { useApp } from '../context/AppContext'
import { useDebounce } from '../hooks/useDebounce'

interface Props {
  onConfirm: () => void
  loading?: boolean
}

const inputCls = 'w-full rounded-md bg-[#141720] border border-[#2e3148] px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors'

export function TableSelector({ onConfirm, loading = false }: Props) {
  const { state, dispatch } = useApp()
  const [search, setSearch] = useState('')
  const [csvInput, setCsvInput] = useState('')
  const debouncedSearch = useDebounce(search, 300)

  const filtered = state.tables.filter(t =>
    t.toLowerCase().includes(debouncedSearch.toLowerCase())
  )
  const selected = new Set(state.selected)

  function toggle(table: string) {
    const next = selected.has(table)
      ? state.selected.filter(t => t !== table)
      : [...state.selected, table]
    dispatch({ type: 'SET_SELECTED', payload: next })
  }

  function selectAll() {
    dispatch({ type: 'SET_SELECTED', payload: filtered })
  }

  function clearAll() {
    dispatch({ type: 'SET_SELECTED', payload: [] })
  }

  function applyCSV() {
    const names = csvInput
      .split(',')
      .map(s => s.trim().toUpperCase())
      .filter(Boolean)

    const tableSet = new Set(state.tables)
    const found = names.filter(n => tableSet.has(n))
    const notFound = names.filter(n => !tableSet.has(n))

    if (found.length) {
      dispatch({ type: 'SET_SELECTED', payload: [...new Set([...state.selected, ...found])] })
    }
    if (notFound.length) {
      alert(`Tabelas não encontradas: ${notFound.join(', ')}`)
    }
    setCsvInput('')
  }

  return (
    <div className="w-full max-w-2xl rounded-xl bg-[#1a1d27] border border-[#2e3148] p-6 shadow-xl">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-slate-100">Tabelas — {state.selectedSchema}</h2>
        <p className="text-xs text-slate-500 mt-0.5">{state.tables.length} tabelas disponíveis</p>
      </div>

      <div className="flex flex-col gap-3">
        {/* CSV input */}
        <div className="flex gap-2">
          <input
            value={csvInput}
            onChange={e => setCsvInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && applyCSV()}
            placeholder="Cole nomes separados por vírgula: TABELA1, TABELA2, ..."
            aria-label="Tabelas por vírgula"
            className={inputCls}
          />
          <button
            onClick={applyCSV}
            className="shrink-0 px-3 py-2 rounded-md bg-[#2e3148] hover:bg-[#3a3f60] text-slate-200 text-sm font-medium transition-colors whitespace-nowrap"
          >
            Adicionar
          </button>
        </div>

        {/* Search + bulk actions */}
        <div className="flex gap-2">
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Buscar tabela..."
            aria-label="Buscar tabela"
            className={inputCls}
          />
          <button
            onClick={selectAll}
            className="shrink-0 px-3 py-2 rounded-md bg-[#2e3148] hover:bg-[#3a3f60] text-slate-200 text-sm font-medium transition-colors whitespace-nowrap"
          >
            Todas ({filtered.length})
          </button>
          <button
            onClick={clearAll}
            className="shrink-0 px-3 py-2 rounded-md bg-[#2e3148] hover:bg-[#3a3f60] text-slate-200 text-sm font-medium transition-colors"
          >
            Limpar
          </button>
        </div>

        {/* Selected chips */}
        {state.selected.length > 0 && (
          <div className="flex flex-wrap gap-1.5 p-3 rounded-md bg-[#141720] border border-[#2e3148] max-h-28 overflow-y-auto">
            {state.selected.map(t => (
              <span key={t} className="flex items-center gap-1 px-2 py-0.5 rounded bg-indigo-600/30 border border-indigo-500/40 text-indigo-300 text-xs font-medium">
                {t}
                <button onClick={() => toggle(t)} aria-label={`Remover ${t}`} className="text-indigo-400 hover:text-white leading-none">×</button>
              </span>
            ))}
          </div>
        )}

        {/* Table list */}
        <div className="flex flex-col gap-0.5 max-h-64 overflow-y-auto rounded-md border border-[#2e3148] bg-[#141720] p-1">
          {filtered.length === 0 ? (
            <p className="text-sm text-slate-500 px-3 py-2">Nenhuma tabela encontrada.</p>
          ) : (
            filtered.map(t => (
              <label
                key={t}
                className="flex items-center gap-2.5 px-3 py-1.5 rounded cursor-pointer hover:bg-[#2e3148] transition-colors text-sm text-slate-300"
              >
                <input
                  type="checkbox"
                  checked={selected.has(t)}
                  onChange={() => toggle(t)}
                  className="accent-indigo-500 h-3.5 w-3.5"
                />
                {t}
              </label>
            ))
          )}
        </div>

        <button
          className="w-full py-2.5 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-1 flex items-center justify-center gap-2 relative"
          disabled={state.selected.length === 0 || loading}
          onClick={onConfirm}
        >
          {loading ? (
            <>
              <span className="inline-block w-4 h-4 border-2 border-indigo-200 border-t-indigo-500 rounded-full animate-spin mr-2" />
              Analisando...
              <span className="absolute left-0 bottom-0 w-full h-1.5 bg-[#2e3148] overflow-hidden rounded-b-md">
                <span className="block h-full bg-indigo-500 rounded-b-md animate-[progress_1.5s_ease-in-out_infinite]" style={{ width: '40%' }} />
              </span>
            </>
          ) : `Analisar${state.selected.length > 0 ? ` (${state.selected.length})` : ''}`}
        </button>
      </div>
    </div>
  )
}
