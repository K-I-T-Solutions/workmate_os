import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [
    tailwindcss(),
    vue(),
    {
      name: "host-filter",
      configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const rawHost =
          req.headers["x-forwarded-host"] ?? req.headers.host;

        const host = Array.isArray(rawHost) ? rawHost[0] : rawHost ?? "";
        const hostname = host.split(":")[0];

        if (
          hostname === "localhost" ||
          hostname === "127.0.0.1" ||
          hostname === "workmate_ui" ||
          hostname.endsWith(".intern.phudevelopement.xyz") ||
          hostname.endsWith(".phudevelopement.xyz")
        ) {
          return next();
        }

        res.statusCode = 403;
        res.end("Host not allowed");
      });
    }
    },
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      // @root-assets entfernt - nicht mehr nötig
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    allowedHosts: [
      "workmate_ui",
      "workmate_backend",
      "workmate.intern.phudevelopement.xyz",
      "workmate.phudevelopement.xyz",
      "workmate-api.phudevelopement.xyz",
      "api.workmate.intern.phudevelopement.xyz",
      "login.intern.phudevelopement.xyz",
      "localhost",
      "127.0.0.1",
    ],
    proxy: {
      "/api": {
        target: "http://workmate_backend:8000",
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on("proxyReq", (proxyReq, req, res) => {
            console.log("🔄 [Vite Proxy] Forwarding:", req.method, req.url, "→", options.target);
          });
        },
      },
    },
  },
});
