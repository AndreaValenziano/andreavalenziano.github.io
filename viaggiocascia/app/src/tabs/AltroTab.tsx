import { useRef, useState } from 'react'
import { exportUserData, importUserData, resetUserData } from '../lib/storage'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { DownloadIcon, TrashIcon, UploadIcon } from '../components/icons'

export type Theme = 'auto' | 'light' | 'dark'

const THEME_OPTIONS: { id: Theme; label: string }[] = [
  { id: 'auto', label: 'Auto' },
  { id: 'light', label: 'Chiaro' },
  { id: 'dark', label: 'Scuro' },
]

export function AltroTab({ theme, onThemeChange }: { theme: Theme; onThemeChange: (theme: Theme) => void }) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [confirmReset, setConfirmReset] = useState(false)
  const [message, setMessage] = useState<{ kind: 'ok' | 'error'; text: string } | null>(null)

  const handleExport = () => {
    const { filename, json } = exportUserData()
    const url = URL.createObjectURL(new Blob([json], { type: 'application/json' }))
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
    setMessage({ kind: 'ok', text: 'Backup esportato: conservatelo (es. inviandovelo in chat).' })
  }

  const handleImport = async (file: File) => {
    try {
      importUserData(await file.text())
      location.reload()
    } catch (error) {
      setMessage({ kind: 'error', text: error instanceof Error ? error.message : 'Import non riuscito.' })
    }
  }

  return (
    <div className="space-y-4 px-4 pt-4 pb-6">
      <h1 className="font-display text-2xl font-semibold">Impostazioni</h1>

      <section className="rounded-2xl bg-pietra-50 p-4 shadow-sm dark:bg-pietra-900">
        <h2 className="font-display text-lg font-semibold">Tema</h2>
        <div className="mt-3 flex rounded-full bg-pietra-200/70 p-1 dark:bg-pietra-800">
          {THEME_OPTIONS.map((option) => (
            <button
              key={option.id}
              type="button"
              onClick={() => onThemeChange(option.id)}
              className={`min-h-10 flex-1 rounded-full text-sm font-semibold transition-colors ${
                theme === option.id
                  ? 'bg-pietra-50 shadow-sm dark:bg-pietra-950'
                  : 'text-pietra-600 dark:text-pietra-300'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
        <p className="mt-2 text-xs text-pietra-500 dark:text-pietra-400">
          La modalità scura è comoda la sera; «Auto» segue il telefono.
        </p>
      </section>

      <section className="rounded-2xl bg-pietra-50 p-4 shadow-sm dark:bg-pietra-900">
        <h2 className="font-display text-lg font-semibold">I tuoi dati</h2>
        <p className="mt-1 text-sm text-pietra-600 dark:text-pietra-400">
          Checklist, note e spese vivono solo su questo telefono. Ognuno ha la propria copia: usate
          esporta/importa per passarsi i dati o come backup.
        </p>
        <div className="mt-3 flex flex-col gap-2">
          <button
            type="button"
            onClick={handleExport}
            className="inline-flex min-h-12 items-center justify-center gap-2 rounded-xl bg-salvia-600 px-4 text-sm font-semibold text-white active:bg-salvia-700"
          >
            <DownloadIcon className="size-5" />
            Esporta dati (JSON)
          </button>
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex min-h-12 items-center justify-center gap-2 rounded-xl border border-salvia-400 px-4 text-sm font-semibold text-salvia-700 active:bg-salvia-50 dark:border-salvia-600 dark:text-salvia-200"
          >
            <UploadIcon className="size-5" />
            Importa da file
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/json,.json"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) void handleImport(file)
              e.target.value = ''
            }}
          />
          <button
            type="button"
            onClick={() => setConfirmReset(true)}
            className="inline-flex min-h-12 items-center justify-center gap-2 rounded-xl border border-terracotta-300 px-4 text-sm font-semibold text-terracotta-700 active:bg-terracotta-50 dark:border-terracotta-700 dark:text-terracotta-300"
          >
            <TrashIcon className="size-5" />
            Azzera i dati personali
          </button>
        </div>
        {message && (
          <p
            className={`mt-3 text-sm font-medium ${
              message.kind === 'ok' ? 'text-salvia-700 dark:text-salvia-300' : 'text-terracotta-700 dark:text-terracotta-300'
            }`}
          >
            {message.text}
          </p>
        )}
      </section>

      <section className="rounded-2xl bg-pietra-50 p-4 shadow-sm dark:bg-pietra-900">
        <h2 className="font-display text-lg font-semibold">Installare l’app sul telefono</h2>
        <div className="mt-2 space-y-3 text-sm leading-relaxed">
          <div>
            <h3 className="font-semibold">📱 iPhone (Safari)</h3>
            <ol className="mt-1 list-decimal space-y-0.5 pl-5 text-pietra-700 dark:text-pietra-300">
              <li>Apri questa pagina in Safari</li>
              <li>Tocca il pulsante Condividi (quadrato con freccia)</li>
              <li>Scegli «Aggiungi alla schermata Home»</li>
            </ol>
          </div>
          <div>
            <h3 className="font-semibold">🤖 Android (Chrome)</h3>
            <ol className="mt-1 list-decimal space-y-0.5 pl-5 text-pietra-700 dark:text-pietra-300">
              <li>Apri questa pagina in Chrome</li>
              <li>Menu ⋮ in alto a destra</li>
              <li>Scegli «Installa app» (o «Aggiungi a schermata Home»)</li>
            </ol>
          </div>
          <p className="rounded-xl bg-salvia-50 p-3 text-salvia-800 ring-1 ring-salvia-200 dark:bg-salvia-900/30 dark:text-salvia-100 dark:ring-salvia-800">
            ✈️ Dopo la prima apertura l’app funziona anche senza rete (in Valnerina il segnale spesso
            manca). Solo «Portami lì» apre le mappe e richiede la connessione.
          </p>
        </div>
      </section>

      <p className="pt-1 text-center text-xs text-pietra-400 dark:text-pietra-500">
        Umbria 2026 · funziona offline · fatta con ♥ per il vostro anniversario
      </p>

      <ConfirmDialog
        open={confirmReset}
        title="Azzerare i dati personali?"
        message="Checklist, note e spese di questo telefono verranno eliminate. I contenuti del viaggio (itinerario, ristoranti…) restano. L’operazione non si può annullare: valuta prima un export."
        confirmLabel="Azzera"
        onConfirm={() => {
          resetUserData()
          location.reload()
        }}
        onCancel={() => setConfirmReset(false)}
      />
    </div>
  )
}
