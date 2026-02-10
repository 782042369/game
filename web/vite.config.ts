import vue from '@vitejs/plugin-vue'
import { splitChunks } from '@xiaowaibuzheng/rolldown-vite-split-chunks'
import Unocss from 'unocss/vite'
import { defineConfig } from 'vite'
import { createHtmlPlugin } from 'vite-plugin-html'

export default defineConfig({
  plugins: [
    splitChunks(),
    createHtmlPlugin({ minify: true }),
    Unocss(),
    vue(),
  ],
  build: {
    rollupOptions: {
      output: {
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]',
      },
    },
    emptyOutDir: true,
    chunkSizeWarningLimit: 1000,
  },
  server: {
    open: true,
    host: '0.0.0.0',
  },
})
