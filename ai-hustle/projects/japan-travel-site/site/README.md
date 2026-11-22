# 走啊敢不敢（Astro）

旅行外掛：試算工具＋懶人包。目的地內容放在各自的路徑下（目前只有 `/japan/`），首頁是目的地入口（`src/site.ts` 的 `DESTINATIONS`）。

```bash
npm install
npm run check-data   # 檢查票價資料都有來源
npm run build        # 輸出到 dist/
npm run preview      # 本地預覽 http://localhost:4321
```

- 正式網址用環境變數 `SITE_URL` 設定（影響 sitemap、canonical、OG）。**部署時必填**，沒設時是 `http://localhost:4321`。
- 部署平台：Cloudflare Pages（`public/_redirects` 處理舊路徑 301）；`vercel.json` 只是備用。
- 新增目的地：在 `src/pages/<目的地>/` 建頁面，並把 `DESTINATIONS` 該項改成 `status: 'live'`。
- 票價資料只放在 `src/data/fares.json`。更新時一併改 `checked` 日期與 `confidence`（official／secondary／unknown）。文章中的數字目前是手寫的，改資料時要同步修改 `src/pages/articles/*.md`。
- OG 圖：`scripts/og.html` 用 Playwright 截圖產生 `public/og-default.png`。
