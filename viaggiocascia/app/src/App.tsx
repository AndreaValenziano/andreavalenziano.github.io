import { useEffect, useState } from 'react'
import { BottomNav } from './components/BottomNav'
import type { TabId } from './components/BottomNav'
import { useStoredState } from './lib/storage'
import { GiorniTab } from './tabs/GiorniTab'
import { InfoTab } from './tabs/InfoTab'
import { ChecklistTab } from './tabs/ChecklistTab'
import { DiarioTab } from './tabs/DiarioTab'
import { AltroTab } from './tabs/AltroTab'
import type { Theme } from './tabs/AltroTab'

export default function App() {
  const [tab, setTab] = useState<TabId>('giorni')
  const [theme, setTheme] = useStoredState<Theme>('theme', 'auto')

  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)')
    const apply = () =>
      document.documentElement.classList.toggle('dark', theme === 'dark' || (theme === 'auto' && media.matches))
    apply()
    media.addEventListener('change', apply)
    return () => media.removeEventListener('change', apply)
  }, [theme])

  return (
    <div className="mx-auto min-h-dvh max-w-lg">
      <main className="pb-24">
        {tab === 'giorni' && <GiorniTab />}
        {tab === 'info' && <InfoTab />}
        {tab === 'checklist' && <ChecklistTab />}
        {tab === 'diario' && <DiarioTab />}
        {tab === 'altro' && <AltroTab theme={theme} onThemeChange={setTheme} />}
      </main>
      <BottomNav tab={tab} onChange={setTab} />
    </div>
  )
}
