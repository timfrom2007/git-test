import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// 正式網域確定後，在 Vercel 設定環境變數 SITE_URL（例：https://www.example.tw）
const site = process.env.SITE_URL || 'https://japan-travel-tools.vercel.app';

export default defineConfig({
  site,
  trailingSlash: 'always',
  integrations: [sitemap()],
  build: { format: 'directory' },
});
