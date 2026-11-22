# 人類待辦（每天約 1 小時）

格式：`- [ ] [project] 事項（預估時間）— 說明連結`

- [ ] [主控] 每晚 10 點看推播與 `reports/` 當日回報（10 分鐘）

## Project A：日本旅遊工具站（A1 完成後）

前提：A1 的程式碼在分支 `claude/gifted-ride-nnfsux`，路徑 `ai-hustle/projects/japan-travel-site/site/`。先等主控決定要不要合併到 main；以下步驟 A-1 可以直接用分支部署成預覽網址。

- [ ] [japan-travel-site] A-1 用 Vercel 建立專案並部署預覽版（10 分鐘）
  1. 登入 https://vercel.com → **Add New… → Project** → Import Git Repository，選 `timfrom2007/git-test`（沒看到就按 *Adjust GitHub App Permissions* 授權這個 repo）。
  2. **Root Directory** 按 Edit，選 `ai-hustle/projects/japan-travel-site/site`。
  3. Framework Preset 會自動偵測為 **Astro**；Build Command `npm run build`、Output Directory `dist` 都用預設，不用改。
  4. 按 **Deploy**，約 1 分鐘完成。打開拿到的 `*.vercel.app` 網址，確認首頁、`/tools/jr-pass-calculator/` 能用（點「東京⇄大阪⇄廣島」應顯示關西＋廣島周遊券省 ¥3,840）。
  5. 若專案預設分支不是 A1 分支：Project → Settings → Git → **Production Branch** 改成 `claude/gifted-ride-nnfsux`，或等主控合併到 main。
  6. 把拿到的網址貼回 `projects/japan-travel-site/STATUS.md` 的「需要人類做什麼」下方。

- [ ] [japan-travel-site] A-2 決定並購買網域（15 分鐘，**會付費，需你決定**）
  1. 候選（自行到 Cloudflare Registrar／Namecheap／Gandi 查是否可註冊與價格）：`jrpass-calc.com`、`japanrail.tw`、`jp-railtools.com`。`.com` 一年通常約 US$10–12，`.tw` 較貴，價格以註冊商頁面為準。
  2. 不想付費也可以先用 `*.vercel.app` 網址上線，之後再換（換網域會損失部分搜尋累積，建議儘早決定）。

- [ ] [japan-travel-site] A-3 把網域接到 Vercel（10 分鐘）
  1. Vercel 專案 → Settings → **Domains** → 輸入網域（建議加 `www.` 版本並把裸網域轉址到 www，Vercel 會自動提示）。
  2. 照 Vercel 顯示的 DNS 記錄到註冊商後台新增（通常裸網域 A 記錄、www 的 CNAME 記錄，以 Vercel 畫面顯示的值為準）。
  3. 回 Vercel 等狀態變成 **Valid Configuration**（幾分鐘到數小時）。
  4. Settings → **Environment Variables** 新增 `SITE_URL` = `https://www.你的網域`（Production），然後 Deployments → 最新一筆 → **Redeploy**。這一步讓 sitemap、canonical、OG 圖網址改成正式網域。

- [ ] [japan-travel-site] A-4 設定 Google Search Console（10 分鐘）
  1. 到 https://search.google.com/search-console → **新增資源** → 選「網域」→ 輸入網域（不含 https）。
  2. 複製 Google 給的 TXT 記錄，到註冊商 DNS 新增 TXT 記錄 → 回 Search Console 按「驗證」（DNS 生效可能要幾分鐘，失敗就隔 10 分鐘再按）。
  3. 左側 **Sitemap** → 輸入 `sitemap-index.xml` → 提交。
  4. 上方「網址審查」貼上 `https://www.你的網域/tools/jr-pass-calculator/` → **要求建立索引**。三篇文章也各做一次（一天有配額，做不完隔天再做）。
  5. 完成日期寫進 `projects/japan-travel-site/STATUS.md`，驗收指標（30 天曝光 > 1,000、點擊 > 50）從這天起算。

- [ ] [japan-travel-site] A-5 核對官方票價（15 分鐘，可選但建議）
  這次 agent 的環境無法直接開 JR 官網，網站上多數票價標「二手來源・待官方確認」。請打開以下 3 頁，核對 `site/src/data/fares.json` 的數字，有不同就在 STATUS.md 記下（agent 下次會更新）：
  1. https://japanrailpass.net/ （JR Pass 7／14／21 日，官網價與代理商價）
  2. https://www.westjr.co.jp/travel-information/en/tickets-passes/jrwest-rail-pass/kansai_hiroshima/ （關西＋廣島 ¥17,000？）
  3. https://tabidachi.travel/hokuriku-arch-pass 或 JR 西日本北陸拱型券頁面（¥35,000？）
