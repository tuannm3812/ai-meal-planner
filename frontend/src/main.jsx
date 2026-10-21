import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Self-hosted fonts (SIL Open Font License 1.1), bundled by Vite, so the app
// makes no third-party font request.
import '@fontsource/inter/400.css'
import '@fontsource/inter/500.css'
import '@fontsource/inter/600.css'
import '@fontsource/bricolage-grotesque/700.css'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
