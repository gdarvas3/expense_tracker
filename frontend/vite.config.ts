import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

const BACKEND_URL = 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  // The dev server forwards API calls, so the browser sees one origin and no CORS is needed.
  server: { proxy: { '/api': BACKEND_URL } },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
