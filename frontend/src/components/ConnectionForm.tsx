import { useState } from 'react'
import { api } from '../api/client'
import { useApp } from '../context/AppContext'
import type { ConnectionConfig } from '../types'
import { Spinner } from './Spinner'
import { Modal } from './Modal'

interface Props {
  onSuccess: (msg: string) => void
  onError: (msg: string) => void
}

const defaultConn: ConnectionConfig = {
  db_type: 'oracle',
  host: '',
  port: 1521,
  service_name: '',
  connection_type: 'service_name',
  user: '',
  password: '',
}

interface SshConfig {
  ssh_host: string
  ssh_port: number
  ssh_user: string
  ssh_password: string
}

const defaultSsh: SshConfig = { ssh_host: '', ssh_port: 22, ssh_user: '', ssh_password: '' }

const inputCls = 'w-full rounded-md bg-[#141720] border border-[#2e3148] px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors'
const labelCls = 'block text-xs font-medium text-slate-400 mb-1'

export function ConnectionForm({ onSuccess, onError }: Props) {
  const { state, dispatch } = useApp()
  const [conn, setConn] = useState<ConnectionConfig>(defaultConn)
  const [ssh, setSsh] = useState<SshConfig>(defaultSsh)
  const [sshOpen, setSshOpen] = useState(false)
  const [loading, setLoading] = useState<'tunnel' | 'connect' | null>(null)

  const tunnelActive = state.tunnel?.active ?? false

  async function handleTunnel() {
    setLoading('tunnel')
    try {
      if (tunnelActive) {
        const status = await api.closeTunnel()
        dispatch({ type: 'SET_TUNNEL', payload: status })
        onSuccess('Túnel SSH fechado.')
        setSshOpen(false)
      } else {
        const status = await api.openTunnel({
          ...ssh,
          remote_host: conn.host,
          remote_port: conn.port,
        })
        dispatch({ type: 'SET_TUNNEL', payload: status })
        onSuccess(`Túnel aberto na porta local ${status.local_port}.`)
        setSshOpen(false)
      }
    } catch (e) {
      onError((e as Error).message)
    } finally {
      setLoading(null)
    }
  }

  async function handleConnect() {
    setLoading('connect')
    try {
      const res = await api.testConnection(conn)
      if (!res.success) throw new Error(res.message)
      dispatch({ type: 'SET_CONNECTION', payload: conn })
      const { schemas } = await api.listSchemas(conn)
      dispatch({ type: 'SET_SCHEMAS', payload: schemas })
      onSuccess('Conexão bem-sucedida!')
    } catch (e) {
      onError((e as Error).message)
    } finally {
      setLoading(null)
    }
  }

  return (
    <>
      <div className="w-full max-w-md rounded-xl bg-[#1a1d27] border border-[#2e3148] p-6 shadow-xl">
        <h2 className="text-lg font-semibold text-slate-100 mb-5">Conexão com o Banco</h2>

        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-[1fr_100px] gap-3">
            <div>
              <label htmlFor="db_host" className={labelCls}>Host</label>
              <input id="db_host" className={inputCls} value={conn.host} onChange={e => setConn({ ...conn, host: e.target.value })} placeholder="localhost" />
            </div>
            <div>
              <label htmlFor="db_port" className={labelCls}>Porta</label>
              <input id="db_port" type="number" className={inputCls} value={conn.port} onChange={e => setConn({ ...conn, port: Number(e.target.value) })} />
            </div>
          </div>

          <div>
            <span className={labelCls}>Tipo de conexão</span>
            <div className="flex gap-4 mt-1">
              {(['service_name', 'sid'] as const).map(type => (
                <label key={type} className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                  <input
                    type="radio"
                    name="connection_type"
                    value={type}
                    checked={conn.connection_type === type}
                    onChange={() => setConn({ ...conn, connection_type: type })}
                    className="accent-indigo-500"
                  />
                  {type === 'service_name' ? 'Service Name' : 'SID'}
                </label>
              ))}
            </div>
          </div>

          <div>
            <label htmlFor="db_service" className={labelCls}>{conn.connection_type === 'sid' ? 'SID' : 'Service Name'}</label>
            <input id="db_service" className={inputCls} value={conn.service_name} onChange={e => setConn({ ...conn, service_name: e.target.value })} placeholder={conn.connection_type === 'sid' ? 'ORCL' : 'XEPDB1'} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="db_user" className={labelCls}>Usuário</label>
              <input id="db_user" className={inputCls} value={conn.user} onChange={e => setConn({ ...conn, user: e.target.value })} />
            </div>
            <div>
              <label htmlFor="db_password" className={labelCls}>Senha</label>
              <input id="db_password" type="password" className={inputCls} value={conn.password} onChange={e => setConn({ ...conn, password: e.target.value })} />
            </div>
          </div>

          {/* Tunnel status / button */}
          <div className="flex items-center justify-between rounded-md border border-[#2e3148] bg-[#141720] px-3 py-2">
            {tunnelActive ? (
              <span className="text-xs text-green-400 flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse" />
                Túnel ativo — porta {state.tunnel?.local_port}
              </span>
            ) : (
              <span className="text-xs text-slate-500">Sem túnel SSH</span>
            )}
            <button
              onClick={() => setSshOpen(true)}
              className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-medium"
            >
              {tunnelActive ? 'Gerenciar' : 'Configurar túnel SSH'}
            </button>
          </div>

          <button
            onClick={handleConnect}
            disabled={loading === 'connect'}
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading === 'connect' ? <Spinner /> : 'Conectar'}
          </button>
        </div>
      </div>

      {/* SSH Modal */}
      <Modal open={sshOpen} onClose={() => setSshOpen(false)} title="Túnel SSH">
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-[1fr_100px] gap-3">
            <div>
              <label htmlFor="ssh_host" className={labelCls}>SSH Host</label>
              <input id="ssh_host" className={inputCls} value={ssh.ssh_host} onChange={e => setSsh({ ...ssh, ssh_host: e.target.value })} placeholder="servidor.empresa.com" />
            </div>
            <div>
              <label htmlFor="ssh_port" className={labelCls}>Porta</label>
              <input id="ssh_port" type="number" className={inputCls} value={ssh.ssh_port} onChange={e => setSsh({ ...ssh, ssh_port: Number(e.target.value) })} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="ssh_user" className={labelCls}>Usuário</label>
              <input id="ssh_user" className={inputCls} value={ssh.ssh_user} onChange={e => setSsh({ ...ssh, ssh_user: e.target.value })} />
            </div>
            <div>
              <label htmlFor="ssh_password" className={labelCls}>Senha</label>
              <input id="ssh_password" type="password" className={inputCls} value={ssh.ssh_password} onChange={e => setSsh({ ...ssh, ssh_password: e.target.value })} />
            </div>
          </div>

          {tunnelActive && (
            <p className="text-xs text-green-400 flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
              Túnel ativo na porta {state.tunnel?.local_port}
            </p>
          )}

          <button
            onClick={handleTunnel}
            disabled={loading === 'tunnel'}
            className={`flex items-center justify-center gap-2 w-full py-2.5 rounded-md text-sm font-medium transition-colors disabled:opacity-50 ${
              tunnelActive ? 'bg-red-600 hover:bg-red-500 text-white' : 'bg-indigo-600 hover:bg-indigo-500 text-white'
            }`}
          >
            {loading === 'tunnel' ? <Spinner /> : tunnelActive ? 'Fechar Túnel' : 'Abrir Túnel'}
          </button>
        </div>
      </Modal>
    </>
  )
}
