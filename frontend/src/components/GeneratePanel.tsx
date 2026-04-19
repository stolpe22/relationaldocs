import { useApp } from '../context/AppContext'
import { api } from '../api/client'
import { useInterval } from '../hooks/useInterval'

interface Props {
  onError: (msg: string) => void
  onSuccess: (msg: string) => void
}

const statusLabel: Record<string, string> = {
  pending: 'Aguardando...',
  running: 'Gerando...',
  done: 'Concluído!',
  error: 'Erro',
}

const statusColor: Record<string, string> = {
  pending: 'text-slate-400',
  running: 'text-indigo-400',
  done: 'text-green-400',
  error: 'text-red-400',
}

export function GeneratePanel({ onError, onSuccess }: Props) {
  const { state, dispatch } = useApp()
  const job = state.job

  async function handleDownload() {
    if (!job) return
    try {
      await api.downloadZip(job.job_id)
      onSuccess('Download iniciado.')
    } catch (e) {
      onError((e as Error).message)
    }
  }

  const polling = job !== null && (job.status === 'pending' || job.status === 'running')

  useInterval(async () => {
    if (!job) return
    try {
      const updated = await api.jobStatus(job.job_id)
      dispatch({ type: 'SET_JOB', payload: updated })
    } catch (e) {
      onError((e as Error).message)
    }
  }, polling ? 2000 : null)

  if (!job) return null

  // Ajusta largura para igualar à análise (max-w-5xl)
  return (
    <div className="w-full max-w-5xl rounded-xl bg-[#1a1d27] border border-[#2e3148] p-6 shadow-xl">
      <h2 className="text-lg font-semibold text-slate-100 mb-4">Geração de Documentação</h2>

      <div className="flex items-center gap-2 mb-4">
        <span className={`text-sm font-medium ${statusColor[job.status] ?? 'text-slate-400'}`}>
          {statusLabel[job.status] ?? job.status}
        </span>
      </div>

      {(job.status === 'pending' || job.status === 'running') && (
        <div className="w-full h-1.5 rounded-full bg-[#2e3148] overflow-hidden mb-4">
          <div className="h-full bg-indigo-500 rounded-full animate-[progress_1.5s_ease-in-out_infinite]" style={{ width: '40%' }} />
        </div>
      )}

      {job.status === 'error' && (
        <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-md px-3 py-2 mb-4">{job.error}</p>
      )}

      {job.status === 'done' && (
        <button
          onClick={handleDownload}
          className="flex items-center justify-center gap-2 w-full py-2.5 rounded-md bg-green-600 hover:bg-green-500 text-white text-sm font-medium transition-colors"
        >
          ⬇ Baixar ZIP
        </button>
      )}
    </div>
  )
}
