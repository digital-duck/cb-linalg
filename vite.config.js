import { defineConfig } from 'vite'

export default defineConfig({
  base: '/cb-linalg/',
  server: {
    proxy: {
      '/api': 'http://localhost:8200',
    },
  },
})
