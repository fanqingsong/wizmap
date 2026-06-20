import { svelte } from '@sveltejs/vite-plugin-svelte';
import * as fs from 'fs';
import * as path from 'path';
import { defineConfig } from 'vite';

// // https://vitejs.dev/config/
// export default defineConfig({
//   plugins: [svelte()]
// });

const removeDataDir = () => {
  return {
    name: 'remove-data-dir',
    resolveId(source) {
      return source === 'virtual-module' ? source : null;
    },
    writeBundle(outputOptions, inputOptions) {
      const outDir = outputOptions.dir;
      const dataDir = path.resolve(outDir, 'data');
      fs.rm(dataDir, { recursive: true }, () =>
        console.log(`Deleted ${dataDir}`)
      );
    }
  };
};

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  if (command === 'serve') {
    // Development
    // Enable polling by default for Docker/WSL2 environments
    const usePolling = process.env.VITE_USE_POLLING === 'true' || process.env.CHOKIDAR_USEPOLLING === 'true';
    return {
      plugins: [svelte()],
      server: {
        // Bind to all interfaces so the dev server is reachable from the host
        // (and through Docker port mapping).
        host: true,
        port: 3000,
        strictPort: true,
        // HMR client connects back on the same port the browser loaded the
        // page from (the published container port).
        hmr: {
          clientPort: 3002,  // Use the external port (3002) instead of internal port (3000)
          // Use WebSocket for HMR
          protocol: 'ws',
          host: 'localhost',  // Use localhost instead of 0.0.0.0 for browser compatibility
          // Add timeout to prevent connection issues
          timeout: 60000
        },
        watch: {
          // Polling is needed when source is bind-mounted into Docker
          // (e.g. WSL2), where filesystem inotify events don't propagate.
          usePolling,
          // Reduce polling frequency to avoid excessive CPU usage
          interval: 1000,
          // Ignore node_modules and other unnecessary directories
          ignored: ['**/node_modules/**', '**/dist/**', '**/.vite/**', '**/git/**']
        }
      }
    };
  } else if (command === 'build') {
    switch (mode) {
      case 'production': {
        // Production: standard web page (default mode)
        return {
          build: {
            outDir: 'dist'
          },
          plugins: [svelte()]
        };
      }

      case 'vercel': {
        // Production: for vercel demo
        return {
          build: {
            outDir: 'dist'
          },
          plugins: [svelte()]
        };
      }

      case 'github': {
        // Production: github page
        return {
          base: '/wizmap/',
          build: {
            outDir: 'gh-page'
          },
          plugins: [svelte(), removeDataDir()]
        };
      }

      case 'notebook': {
        // Production: notebook widget
        return {
          build: {
            outDir: 'notebook-widget/_wizmap',
            sourcemap: false,
            lib: {
              entry: 'src/main.ts',
              formats: ['iife'],
              name: 'wizmap',
              fileName: format => 'wizmap.js'
            }
          },
          plugins: [
            svelte({
              emitCss: false
            }),
            {
              name: 'my-post-build-plugin',
              writeBundle: {
                sequential: true,
                order: 'post',
                handler(options) {
                  // Move target file to the notebook package
                  fs.copyFile(
                    path.resolve(options.dir, 'wizmap.js'),
                    path.resolve(__dirname, 'notebook-widget/wizmap/wizmap.js'),
                    error => {
                      if (error) throw error;
                    }
                  );

                  // Delete all other generated files
                  fs.rm(options.dir, { recursive: true }, error => {
                    if (error) throw error;
                  });
                }
              }
            }
          ]
        };
      }

      default: {
        console.error(`Unknown production mode ${mode}`);
        return null;
      }
    }
  }
});
