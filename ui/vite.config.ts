import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import type { ViteDevServer } from "vite";
import type { IncomingMessage, ServerResponse } from "http";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [
    tailwindcss(),
    vue(),
    {
      name: "host-filter",
      configureServer(server: ViteDevServer) {
        server.middlewares.use(
          (
            req: IncomingMessage,
            res: ServerResponse,
            next: (err?: unknown) => void
          ) => {
            const rawHost = req.headers.host;
            const host = Array.isArray(rawHost) ? rawHost[0] : rawHost ?? "";
            if (host.endsWith(".intern.phudevelopement.xyz")) return next();
            if (host.endsWith(".phudevelopement.xyz")) return next();
            if (host.startsWith("localhost")) return next();
            res.statusCode = 403;
            res.end("Host not allowed");
          }
        );
      },
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
      "workmate.intern.phudevelopement.xyz",
      "workmate.phudevelopement.xyz",
      "api.workmate.intern.phudevelopement.xyz",
      "login.intern.phudevelopement.xyz",
      "localhost",
      "127.0.0.1",
    ],
  },
});
