import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { vitePrerenderPlugin } from 'vite-prerender-plugin'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  plugins: [
    react(),
    tailwindcss(),
    // Prerender marketing pages for SEO
    command === 'build' && vitePrerenderPlugin({
      renderTarget: '#root',
      prerenderScript: path.resolve(__dirname, 'src/prerender.tsx'),
      additionalPrerenderRoutes: [
        '/',
        '/canvas',
        '/gallery',
        '/models',
        '/research',
        '/skills',
        '/pricing',
        '/demo',
        '/trust',
        '/solutions',
        '/customers',
        '/exhibitions',
      ],
    }),
  ].filter(Boolean),

  // Always use absolute base URL — required for BrowserRouter + Firebase Hosting
  base: '/',
  
  // Vite cache optimization for Windows compatibility
  cacheDir: '.vite',
  
  // Production optimizations
  build: {
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: false, // Disable in production for security
    chunkSizeWarningLimit: 1000,
    
    rollupOptions: {
      output: {
        entryFileNames: `assets/[name].[hash].js`,
        chunkFileNames: `assets/[name].[hash].js`,
        assetFileNames: `assets/[name].[hash].[ext]`,
        
        // Code splitting optimization
        // 注意: 避免循环依赖，只对独立的大型库进行手动分块
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['framer-motion', '@headlessui/react'],
          charts: ['recharts'],
          icons: ['lucide-react'],
          // Three.js 3D 渲染包独立分块
          'three-core': ['three'],
          'three-fiber': ['@react-three/fiber', '@react-three/drei'],
          // negative-space (740KB) now loaded via dynamic import — no manual chunk needed
        }
      }
    },
    
    // Optimize bundle size
    cssCodeSplit: true,
    assetsInlineLimit: 4096, // Inline assets smaller than 4kb
    
    // Already set minify: 'esbuild' above
  },
  
  // Development server configuration with cache fix
  server: {
    port: 5173,
    host: true,
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate'
    },
    // Windows file watching optimization - 优化CPU占用
    watch: {
      usePolling: false,  // 使用系统文件监听减少CPU轮询
      interval: 1000      // 降低轮询频率
    },
    // HMR configuration for better reliability
    hmr: {
      overlay: true,
      timeout: 30000      // 从60s降到30s
    }
  },
  
  // Preview server configuration
  preview: {
    port: 4173,
    host: true
  },
  
  // Define environment variables
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString())
  },
  
  // Optimize dependencies with better cache handling
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'framer-motion',
      '@headlessui/react',
      // Three.js 3D rendering packages - explicit include for CI build compatibility
      'three',
      '@react-three/fiber',
      '@react-three/drei'
    ],
    exclude: ['@vite/client', '@vite/env'],
    // 使用缓存提升启动速度 (移除force:true)
    force: false,
    // Entries to scan for dependencies
    entries: ['src/**/*.tsx', 'src/**/*.ts']
  },
  
  // Module resolution optimization - 关键配置解决 CI 构建问题
  resolve: {
    // Path alias — matches tsconfig.app.json paths
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    // Preserve symlinks for better module resolution
    preserveSymlinks: false,
    // Optimize extension resolution
    extensions: ['.tsx', '.ts', '.jsx', '.js'],
    // 去重配置 - 防止多个 Three.js 实例被导入（关键！）
    dedupe: ['react', 'react-dom', 'three', '@react-three/fiber', '@react-three/drei']
  }
}))
