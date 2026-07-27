import type { ComponentType, SVGProps } from 'react'
import { CalendarIcon, CheckSquareIcon, GearIcon, InfoIcon, NotebookIcon } from './icons'

export type TabId = 'giorni' | 'info' | 'checklist' | 'diario' | 'altro'

const TABS: { id: TabId; label: string; Icon: ComponentType<SVGProps<SVGSVGElement>> }[] = [
  { id: 'giorni', label: 'Giorni', Icon: CalendarIcon },
  { id: 'info', label: 'Info', Icon: InfoIcon },
  { id: 'checklist', label: 'Checklist', Icon: CheckSquareIcon },
  { id: 'diario', label: 'Diario', Icon: NotebookIcon },
  { id: 'altro', label: 'Altro', Icon: GearIcon },
]

export function BottomNav({ tab, onChange }: { tab: TabId; onChange: (tab: TabId) => void }) {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 border-t border-pietra-200 bg-pietra-50/95 backdrop-blur dark:border-pietra-800 dark:bg-pietra-950/95">
      <div className="mx-auto flex max-w-lg items-stretch justify-around pb-[env(safe-area-inset-bottom)]">
        {TABS.map(({ id, label, Icon }) => {
          const active = tab === id
          return (
            <button
              key={id}
              type="button"
              onClick={() => onChange(id)}
              aria-current={active ? 'page' : undefined}
              className={`flex min-h-14 flex-1 flex-col items-center justify-center gap-0.5 pt-1.5 pb-1 text-[11px] font-semibold transition-colors ${
                active
                  ? 'text-terracotta-600 dark:text-terracotta-300'
                  : 'text-pietra-500 active:text-pietra-700 dark:text-pietra-400'
              }`}
            >
              <Icon className="size-6" />
              {label}
            </button>
          )
        })}
      </div>
    </nav>
  )
}
