import { useApp } from '../context/AppContext'
import { Spinner } from './Spinner'

interface Props {
  loading: boolean
  onGenerate: () => void
}

interface MetricCardProps {
  label: string
  value: number | string
  sub?: string
  accent?: boolean
}

function MetricCard({ label, value, sub, accent }: MetricCardProps) {
  return (
    <div className={`flex flex-col rounded-lg border px-4 py-3 gap-0.5 ${accent ? 'border-indigo-500/40 bg-indigo-600/10' : 'border-[#2e3148] bg-[#141720]'}`}>
      <span className={`text-2xl font-bold ${accent ? 'text-indigo-400' : 'text-slate-200'}`}>{value}</span>
      <span className="text-xs text-slate-500">{label}</span>
      {sub && <span className="text-xs text-slate-600 truncate">{sub}</span>}
    </div>
  )
}

export function AnalysisDashboard({ loading, onGenerate }: Props) {
  const { state } = useApp()
  const a = state.analysis

  return (
    <div className="w-full max-w-5xl rounded-xl bg-[#1a1d27] border border-[#2e3148] p-6 shadow-xl">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">Análise — {state.selectedSchema}</h2>
          <p className="text-xs text-slate-500 mt-0.5">{state.selected.length} tabela(s) selecionada(s)</p>
        </div>
      </div>

      {loading && (
        <div className="w-full h-2 rounded-full bg-[#2e3148] overflow-hidden mb-6">
          <div className="h-full bg-indigo-500 rounded-full animate-[progress_1.5s_ease-in-out_infinite]" style={{ width: '40%' }} />
        </div>
      )}

      {!a ? (
        <div className="flex items-center justify-center py-12 text-slate-500 text-sm">
          Clique em Analisar para carregar os dados.
        </div>
      ) : (
        <>
          {/* Totais globais */}
          <div className="grid grid-cols-4 gap-3 mb-6 sm:grid-cols-8">
            <MetricCard label="Tabelas" value={a.total_tables} accent />
            <MetricCard label="Colunas" value={a.total_columns} accent />
            <MetricCard label="FKs" value={a.total_fks} accent />
            <MetricCard label="Triggers" value={a.total_triggers} accent />
            <MetricCard label="PKs" value={a.total_pks} />
            <MetricCard label="UKs" value={a.total_uks} />
            <MetricCard label="CHECKs" value={a.total_checks} />
            <MetricCard label="Constraints" value={a.total_constraints} />
          </div>

          {/* Relacionamentos implícitos */}
          {a.implicit_relations.length > 0 && (
            <div className="mb-5 p-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5">
              <p className="text-xs font-medium text-emerald-400 mb-2">
                🤝 {a.implicit_relations.length} vínculo(s) implícito(s) detectado(s) por nomenclatura (COD%, NUM%)
              </p>
              <div className="flex flex-col gap-1 max-h-40 overflow-y-auto">
                {a.implicit_relations.map((r, i) => (
                  <span key={i} className="text-xs text-emerald-300 font-mono">
                    <span className="text-slate-400">{r.column}</span>
                    {' → '}
                    <span className="text-emerald-300">{r.table_1}</span>
                    <span className="text-slate-500"> ↔ </span>
                    <span className="text-emerald-300">{r.table_2}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Referências externas */}
          {a.external_references.length > 0 && (
            <div className="mb-5 p-3 rounded-lg border border-amber-500/20 bg-amber-500/5">
              <p className="text-xs font-medium text-amber-400 mb-1.5">
                {a.external_references.length} tabela(s) referenciada(s) fora da seleção
              </p>
              <div className="flex flex-wrap gap-1.5">
                {a.external_references.map(ref => (
                  <span key={ref} className="px-2 py-0.5 rounded text-xs bg-amber-500/10 border border-amber-500/20 text-amber-300">
                    {ref}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Breakdown por tabela */}
          <div className="rounded-lg border border-[#2e3148] overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#2e3148] bg-[#141720]">
                  <th className="text-left px-4 py-2.5 text-xs font-medium text-slate-400">Tabela</th>
                  <th className="text-center px-3 py-2.5 text-xs font-medium text-slate-400">Colunas</th>
                  <th className="text-center px-3 py-2.5 text-xs font-medium text-slate-400">PKs</th>
                  <th className="text-center px-3 py-2.5 text-xs font-medium text-slate-400">FKs</th>
                  <th className="text-center px-3 py-2.5 text-xs font-medium text-slate-400">UKs</th>
                  <th className="text-center px-3 py-2.5 text-xs font-medium text-slate-400">CHECKs</th>
                  <th className="text-center px-3 py-2.5 text-xs font-medium text-slate-400">Triggers</th>
                  <th className="text-left px-4 py-2.5 text-xs font-medium text-slate-400">Referencia</th>
                </tr>
              </thead>
              <tbody>
                {a.tables.map((t, i) => (
                  <tr key={t.name} className={`border-b border-[#2e3148] last:border-0 ${i % 2 === 0 ? '' : 'bg-[#141720]/40'}`}>
                    <td className="px-4 py-2 font-mono text-xs text-slate-200">{t.name}</td>
                    <td className="px-3 py-2 text-center text-slate-300">{t.columns}</td>
                    <td className="px-3 py-2 text-center text-slate-300">{t.pks || '—'}</td>
                    <td className="px-3 py-2 text-center">
                      <span className={t.fks > 0 ? 'text-indigo-400' : 'text-slate-600'}>{t.fks || '—'}</span>
                    </td>
                    <td className="px-3 py-2 text-center text-slate-300">{t.uks || '—'}</td>
                    <td className="px-3 py-2 text-center text-slate-300">{t.checks || '—'}</td>
                    <td className="px-3 py-2 text-center">
                      <span className={t.triggers > 0 ? 'text-amber-400' : 'text-slate-600'}>{t.triggers || '—'}</span>
                    </td>
                    <td className="px-4 py-2">
                      <div className="flex flex-wrap gap-1">
                        {t.referenced_tables.map(ref => (
                          <span key={ref} className="px-1.5 py-0.5 rounded text-xs bg-indigo-600/20 text-indigo-300 font-mono">
                            {ref}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Botão Gerar Documentação no final */}
          <div className="flex justify-end mt-8">
            <button
              className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={onGenerate}
              disabled={loading || !a}
            >
              {loading ? <Spinner /> : 'Gerar Documentação'}
            </button>
          </div>
        </>
      )}
    </div>
  )
}
