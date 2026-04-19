import { useState, useEffect } from 'react'
import { useApp } from './context/AppContext'
import { api } from './api/client'
import { useToast } from './hooks/useToast'
import { ToastList } from './components/Toast'
import { ConnectionForm } from './components/ConnectionForm'
import { SchemaSelector } from './components/SchemaSelector'
import { TableSelector } from './components/TableSelector'
import { AnalysisDashboard } from './components/AnalysisDashboard'
import { GeneratePanel } from './components/GeneratePanel'

const STEP_LABELS = ['Conexão', 'Tabelas', 'Análise']

function stepToScreen(step: string): number {
  if (step === 'connect') return 0
  if (['schemas', 'tables', 'select'].includes(step)) return 1
  return 2
}

export default function App() {
  const { state, dispatch } = useApp()
  const { toasts, addToast, removeToast } = useToast()
  const [screen, setScreen] = useState(0)
  const [analysisLoading, setAnalysisLoading] = useState(false)

  useEffect(() => {
    const s = stepToScreen(state.step)
    if (s > screen) setScreen(s)
  }, [state.step])

  async function handleAnalyse() {
    if (!state.connection || !state.selectedSchema) return
    setAnalysisLoading(true)
    try {
      const result = await api.analyse(state.selectedSchema, state.selected)
      dispatch({ type: 'SET_ANALYSIS', payload: result })
      setScreen(2)
    } catch (e) {
      addToast((e as Error).message, 'error')
    } finally {
      setAnalysisLoading(false)
    }
  }

  async function handleGenerate() {
    if (!state.selectedSchema) return
    try {
      const { job_id } = await api.generate(state.selectedSchema, state.selected)
      dispatch({ type: 'SET_JOB', payload: { job_id, status: 'pending' } })
    } catch (e) {
      addToast((e as Error).message, 'error')
    }
  }

  const screens = [
    // ── Screen 0: Conexão ────────────────────────────────────────────────
    <div className="flex items-center justify-center w-full min-h-full py-10 px-6">
      <ConnectionForm
        onSuccess={m => addToast(m, 'success')}
        onError={m => addToast(m, 'error')}
      />
    </div>,

    // ── Screen 1: Schema + Tabelas ────────────────────────────────────────
    <div className="flex gap-5 w-full max-w-5xl mx-auto px-6 py-10 items-start">
      <div className="w-56 shrink-0">
        <SchemaSelector
          onSuccess={m => addToast(m, 'success')}
          onError={m => addToast(m, 'error')}
        />
      </div>
      <div className="flex-1 min-w-0">
        {state.selectedSchema ? (
          <TableSelector onConfirm={handleAnalyse} loading={analysisLoading} />
        ) : (
          <div className="flex items-center justify-center h-48 rounded-xl border border-dashed border-[#2e3148] text-slate-600 text-sm">
            Selecione um schema para ver as tabelas
          </div>
        )}
      </div>
    </div>,

    // ── Screen 2: Análise + Geração ───────────────────────────────────────
    <div className="flex flex-col gap-5 w-full max-w-5xl mx-auto px-6 py-10">
      <AnalysisDashboard loading={analysisLoading} onGenerate={handleGenerate} />
      {state.job && (
        <GeneratePanel
          onError={m => addToast(m, 'error')}
          onSuccess={m => addToast(m, 'success')}
        />
      )}
    </div>,
  ]

  return (
    <div className="h-screen bg-[#0f1117] flex flex-col overflow-hidden">
      {/* Header */}
      <header className="shrink-0 border-b border-[#2e3148] bg-[#1a1d27]/80 backdrop-blur z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center gap-3">
          {screen > 0 && (
            <button
              onClick={() => setScreen(s => s - 1)}
              aria-label="Voltar"
              className="flex items-center justify-center h-7 w-7 rounded-md text-slate-400 hover:text-slate-100 hover:bg-[#2e3148] transition-colors text-lg"
            >
              ←
            </button>
          )}

          <h1 className="text-base font-semibold text-slate-100 tracking-tight">Relationals Doc</h1>

          <nav className="flex items-center gap-1 ml-auto" aria-label="Progresso">
            {STEP_LABELS.map((label, i) => (
              <div key={label} className="flex items-center gap-1">
                {i > 0 && (
                  <div className={`w-6 h-px transition-colors duration-300 ${i <= screen ? 'bg-indigo-500' : 'bg-[#2e3148]'}`} />
                )}
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium transition-colors duration-300 ${
                  i === screen ? 'bg-indigo-600 text-white' : i < screen ? 'text-indigo-400' : 'text-slate-600'
                }`}>
                  {label}
                </span>
              </div>
            ))}
          </nav>
        </div>
      </header>

      {/* Sliding panels */}
      <main className="flex-1 relative overflow-hidden">
        {screens.map((content, i) => (
          <div
            key={i}
            aria-hidden={i !== screen}
            className={`absolute inset-0 overflow-y-auto transition-transform duration-300 ease-in-out ${i !== screen ? 'pointer-events-none' : ''}`}
            style={{ transform: `translateX(${(i - screen) * 100}%)` }}
          >
            {content}
          </div>
        ))}
      </main>

      <ToastList toasts={toasts} onRemove={removeToast} />
    </div>
  )
}
