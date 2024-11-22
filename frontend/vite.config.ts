import {defineConfig, loadEnv} from "vite"
import EntryShakingPlugin from "vite-plugin-entry-shaking";
import react from "@vitejs/plugin-react-swc";
import obfuscatorPlugin from "vite-plugin-javascript-obfuscator";

// https://vitejs.dev/config/
export default ({mode}) => {
  const env = {...process.env, ...loadEnv(mode, process.cwd(), "")};

  return defineConfig({
    base: "/",
    plugins: [
      react()
    ],
    build: {
    },
    define: {
      "process.env": env
    },
    server: {
      host: env.HOST || "localhost",
      port: env.PORT ? parseInt(env.PORT, 10) : 3000
    },
    resolve: {
      alias: [
        {
          find: /^~(.*)$/,
          replacement: "$1",
        },
      ],
    }
  })
}
