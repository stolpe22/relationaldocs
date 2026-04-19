export function Spinner({ size = 'sm' }: { size?: 'sm' | 'md' }) {
  const cls = size === 'md' ? 'h-5 w-5' : 'h-4 w-4'
  return (
    <span
      className={`inline-block ${cls} animate-spin rounded-full border-2 border-white/20 border-t-white`}
      aria-label="Carregando"
    />
  )
}
