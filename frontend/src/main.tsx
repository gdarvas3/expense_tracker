import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import { App } from './App'
import { CurrentUserProvider } from './context/CurrentUserProvider'
import './index.css'

const rootElement = document.getElementById('root')
if (rootElement === null) {
  throw new Error('index.html must contain an element with id="root".')
}

createRoot(rootElement).render(
  <StrictMode>
    <CurrentUserProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </CurrentUserProvider>
  </StrictMode>,
)
