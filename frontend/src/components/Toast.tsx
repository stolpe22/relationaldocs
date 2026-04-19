import type { Toast, ToastType } from '../hooks/useToast'

const colors: Record<ToastType, string> = {
  success: 'bg-green-600',
  error: 'bg-red-600',
  info: 'bg-indigo-600',
}

export function ToastList({ toasts, onRemove }: { toasts: Toast[]; onRemove: (id: number) => void }) {
  return (
    <div className="fixed bottom-6 right-6 flex flex-col gap-2 z-50">
      {toasts.map(t => (
        <div key={t.id} className={`flex items-center gap-3 px-4 py-3 rounded-lg text-white text-sm shadow-xl min-w-64 ${colors[t.type]}`}>
          <span className="flex-1">{t.message}</span>
          <button onClick={() => onRemove(t.id)} aria-label="Fechar" className="text-white/80 hover:text-white text-lg leading-none">×</button>
        </div>
      ))}
    </div>
  )
}
