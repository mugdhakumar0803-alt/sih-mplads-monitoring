import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Without this, analyticsApi.js calls to "/api/analytics/..." hit
    // the frontend's own dev server (5173) instead of the backend (8000)
    // and silently fail — that's why charts showed nothing.
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
})
