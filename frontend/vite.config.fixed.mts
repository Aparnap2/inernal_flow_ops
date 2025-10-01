import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import cloudflareWorkers from "@cloudflare/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [
    react(), 
    cloudflareWorkers(),
    tailwindcss()
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  optimizeDeps: {
    include: ['wrangler'],
  },
  build: {
    commonjsOptions: {
      include: [/wrangler/, /node_modules/],
    },
  },
  server: {
    port: 5173,
    host: true,
  },
});
