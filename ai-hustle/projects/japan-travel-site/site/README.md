# 日本鐵道省錢工具箱（Astro）

```bash
npm install
npm run check-data   # 檢查票價資料都有來源
npm run build        # 輸出到 dist/
npm run preview      # 本地預覽 http://localhost:4321
```

- 正式網址用環境變數 `SITE_URL` 設定（影響 sitemap、canonical、OG）。沒設時預設 `https://japan-travel-tools.vercel.app`。
- 票價資料只放在 `src/data/fares.json`。更新時一併改 `checked` 日期與 `confidence`（official／secondary／unknown）。文章中的數字目前是手寫的，改資料時要同步修改 `src/pages/articles/*.md`。
- OG 圖：`scripts/og.html` 用 Playwright 截圖產生 `public/og-default.png`。
