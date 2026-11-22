import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// 部署時一定要設定環境變數 SITE_URL（例：https://<專案>.pages.dev 或正式網域），
// 否則 sitemap、canonical、OG 網址會是 localhost。見 control/human-todo.md A-0。
const site = process.env.SITE_URL || 'http://localhost:4321';

export default defineConfig({
  site,
  trailingSlash: 'always',
  integrations: [sitemap()],
  build: { format: 'directory' },
});
