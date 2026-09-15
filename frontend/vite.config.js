import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/backend-api": {
        target: "http://127.0.0.1:8000",
        rewrite: (path) => path.replace(/^\/backend-api/, ""),
      },
    },
  },
})
