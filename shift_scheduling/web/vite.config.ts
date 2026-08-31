import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'node:path'

export default defineConfig({
  base: '/shiftpro/',

  // Netlify publishes `dist` as the site root, so the emitted tree has to mirror
  // `base` for /shiftpro/favicon.svg to be a real file rather than something the
  // SPA fallback has to rewrite. Keep these two in step.
  build: { outDir: 'dist/shiftpro' },

  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(import.meta.dirname, './src') },
  },
  server: { port: 5173 },
})
