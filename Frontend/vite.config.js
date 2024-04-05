import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Use "/api" as the prefix for routes you want to proxy to your backend
      '/api': {
        target: 'http://localhost:8000', // Your backend server
        changeOrigin: true, // Needed for virtual hosted sites
        rewrite: (path) => path.replace(/^\/api/, '') // Rewrite the path to remove "/api"
      },
    },
  },
});
