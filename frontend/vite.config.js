import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Forward /api calls to Flask so the browser sees one origin (no CORS setup needed).
    proxy: { '/api': 'http://127.0.0.1:5000' },
  },
});