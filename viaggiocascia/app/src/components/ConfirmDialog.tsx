interface Props {
  open: boolean
  title: string
  message: string
  confirmLabel: string
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({ open, title, message, confirmLabel, onConfirm, onCancel }: Props) {
  if (!open) return null
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-pietra-950/50 p-6 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label={title}
      onClick={onCancel}
    >
      <div
        className="w-full max-w-sm rounded-2xl bg-pietra-50 p-5 shadow-xl dark:bg-pietra-900"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="font-display text-lg font-semibold">{title}</h2>
        <p className="mt-2 text-sm text-pietra-700 dark:text-pietra-300">{message}</p>
        <div className="mt-5 flex justify-end gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="min-h-11 rounded-full px-4 text-sm font-semibold text-pietra-700 active:bg-pietra-200 dark:text-pietra-200 dark:active:bg-pietra-800"
          >
            Annulla
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="min-h-11 rounded-full bg-terracotta-600 px-5 text-sm font-semibold text-white active:bg-terracotta-700"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
