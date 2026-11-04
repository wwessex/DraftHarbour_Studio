import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';
import { handleBrokerRequest } from './src/server/integrationBroker';

const MAX_BROKER_BODY_BYTES = 16 * 1024 * 1024;
const MAX_BROKER_BODY_READS = 4;
const BROKER_BODY_TIMEOUT_MS = 15_000;

function integrationBrokerPlugin(): Plugin {
  return {
    name: 'integration-broker',
    configureServer(server) {
      let activeReads = 0;
      server.middlewares.use((req, res, next) => {
        const route = (req.url || '/').split('?')[0];
        if (req.method !== 'POST' || !/^\/api\/(?:ai\/generate|chat|integrations\/[^/]+\/(?:connect|push|pull))$/.test(route)) {
          next();
          return;
        }

        const reject = (status: number) => {
          res.writeHead(status, { Connection: 'close' });
          res.end();
        };
        if (Number(req.headers['content-length']) > MAX_BROKER_BODY_BYTES) {
          reject(413);
          return;
        }
        if (activeReads >= MAX_BROKER_BODY_READS) {
          reject(503);
          return;
        }

        activeReads++;
        let reading = true;
        let bytes = 0;
        const chunks: Buffer[] = [];
        const finishRead = () => {
          if (!reading) return false;
          reading = false;
          activeReads--;
          clearTimeout(deadline);
          return true;
        };
        const deadline = setTimeout(() => {
          if (finishRead()) {
            chunks.length = 0;
            reject(408);
          }
        }, BROKER_BODY_TIMEOUT_MS);
        req.on('close', finishRead);
        req.on('error', finishRead);
        req.on('data', (chunk: Buffer) => {
          if (!reading) return;
          bytes += chunk.length;
          if (bytes > MAX_BROKER_BODY_BYTES) {
            finishRead();
            chunks.length = 0;
            reject(413);
            return;
          }
          chunks.push(chunk);
        });
        req.on('end', async () => {
          if (!finishRead()) return;
          let body: unknown;
          try {
            body = bytes ? JSON.parse(Buffer.concat(chunks, bytes).toString('utf8')) : {};
          } catch {
            reject(400);
            return;
          } finally {
            chunks.length = 0;
          }

          const result = await handleBrokerRequest({
            method: 'POST',
            path: route,
            body,
            authorization: req.headers.authorization,
          });
          if (!result) {
            next();
            return;
          }
          res.statusCode = result.status;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify(result.body));
        });
      });
    },
  };
}

export default defineConfig({
  base: './',
  plugins: [
    tailwindcss(),
    react(),
    integrationBrokerPlugin(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['assets/favicon.ico', 'assets/apple-touch-icon.png', 'assets/*.png', 'assets/*.svg', 'brand/*.svg'],
      manifest: {
        name: 'DraftHarbour Studio',
        short_name: 'DraftHarbour',
        description: 'Offline-first Progressive Web Application for writing novels',
        theme_color: '#0b1020',
        background_color: '#0b1020',
        display: 'standalone',
        start_url: './',
        icons: [
          {
            src: 'assets/icon-blue-32.png',
            sizes: '32x32',
            type: 'image/png'
          },
          {
            src: 'assets/icon-blue-48.png',
            sizes: '48x48',
            type: 'image/png'
          },
          {
            src: 'assets/icon-blue-192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'assets/icon-blue-512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'assets/pwa-192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'maskable'
          },
          {
            src: 'assets/pwa-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          },
          {
            urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'gstatic-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      }
    })
  ],

  test: {
    include: ['src/**/*.test.{ts,tsx}'],
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      enabled: false,
      provider: 'v8',
      reporter: ['text', 'json-summary'],
      reportsDirectory: './coverage',
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/**/*.d.ts',
        'src/**/*.test.{ts,tsx}',
        'src/test/**',
        'src/vite-env.d.ts',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  // Native build output also contains HTML; only scan the web entry point.
  optimizeDeps: {
    entries: ['index.html'],
  },
  build: {
    target: ['es2020', 'safari14'],
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (
            id.includes('/src/lib/export/')
            || id.includes('/src/components/Modals/ExportModal')
            || id.includes('/src/components/Modals/ExportHistoryModal')
          ) {
            return 'export';
          }

          if (
            id.includes('/src/lib/ai/')
            || id.includes('/src/components/Modals/AIWritingModal')
            || id.includes('/src/components/Modals/TranslationModal')
          ) {
            return 'ai';
          }

          if (
            id.includes('/src/lib/integrations/')
            || id.includes('/src/components/Modals/IntegrationsModal')
          ) {
            return 'integrations';
          }

          if (id.includes('@codemirror') || id.includes('@lezer')) {
            return 'codemirror';
          }

          return undefined;
        }
      }
    }
  }
});
