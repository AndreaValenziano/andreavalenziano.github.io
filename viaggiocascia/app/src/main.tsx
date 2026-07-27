import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { registerSW } from 'virtual:pwa-register'
import App from './App'
import './index.css'

// autoUpdate + controllo orario: le modifiche ai contenuti pubblicate prima
// della partenza arrivano da sole sui telefoni con l'app installata.
registerSW({
  immediate: true,
  onRegisteredSW(_url, registration) {
    if (registration) {
      setInterval(() => void registration.update(), 60 * 60 * 1000)
    }
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
