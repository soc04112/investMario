import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs';
import path from 'path'; 

// const certDir = '../cert';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://open-api.bingx.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // /api를 제거하고 전달
        secure: false,
      }
    },
    port: 3500,
    // https: {
    //     key: fs.readFileSync(path.join(certDir, 'key.pem')),
    //     cert: fs.readFileSync(path.join(certDir, 'cert.pem')),
    // },
    // host: true, 
    // allowedHosts: ["vt.ngrok.pro"],
    watch: {
      usePolling: true, 
      interval: 100,   
    },
  }
})
