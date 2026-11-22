# 狀態：A1 完成（2026-11-22，Asia/Taipei）

分支：`claude/gifted-ride-nnfsux`

## 做了什麼
- 用 Astro 5 建了靜態網站，繁體中文、面向台灣旅客，本地 `npm run build` 成功（8 頁）。
- 第一個工具：**JR Pass／周遊券划算試算器**。比較 JR Pass 全國版 7／14／21 日（官網價或代理商價）、關西廣域、關西＋廣島、北陸拱型周遊券和全部單買。有快速套用行程、可選 Nozomi 券，也能自行修改票價。已用瀏覽器測過，結果和手算一致，手機寬度不會橫向捲動。
- 3 篇支援文章，每篇都有表格和實際計算：
  1. `/articles/jr-pass-price-2026/`：2026 年 10 月 JR Pass 漲價，官網和代理商價差表、兒童價、Nozomi 券
  2. `/articles/tokyo-osaka-shinkansen-jr-pass/`：新幹線單程票價，加上 6 種行程的 JR Pass 回本實算
  3. `/articles/kansai-area-passes-2026/`：關西地區周遊券停售後的三張替代券比較與回本門檻
- `/sources/` 頁列出所有票價的來源、可信度、查核日期。
- SEO：sitemap（@astrojs/sitemap）、robots.txt、canonical、description、OG/Twitter 卡（1200×630 OG 圖）、JSON-LD（WebSite、WebApplication、FAQPage、Article、BreadcrumbList）。

## 成果在哪
- 程式碼：`projects/japan-travel-site/site/`（說明見 `site/README.md`）
- 票價資料：`site/src/data/fares.json`（用 `npm run check-data` 檢查：有數字的一定要有來源，沒數字的一定要標 unknown）

## 資料可信度（重要）
- 這個環境無法開 japanrailpass.net、westjr.co.jp、JR 東海等官方網站（DNS 被擋），票價只能從搜尋結果取得。
- 只有 Kansai WIDE ¥12,000 標為「官方」。其他都標「二手來源・待官方確認」，來源間有落差時取較低值。
- 查不到的標「待確認」，沒有填估計值：Haruka（關西機場–京都）、京都–大阪、新大阪–岡山、金澤–大阪、7 日綠色車廂官網價、多數兒童價、關西地區周遊券確切停售日。

## 下一步（建議）
1. 讓 agent 能讀官方網站後（需主控或人類把上述網域加進環境網路白名單），把二手數字逐一換成官方數字，補齊「待確認」。
2. 第二個工具：旅遊預算計算機或退稅試算。
3. 長尾文章：北陸（金澤）、四國、山陰的交通與周遊券。
4. 上線後設定聯盟連結（Klook／KKday 的 JR Pass、周遊券商品頁），需人類先申請聯盟帳號。

## 需要人類做什麼
見 `control/human-todo.md` 的「Project A」段落：A-1 Vercel 部署（10 分）、A-2 選購網域（15 分，付費）、A-3 接網域（10 分）、A-4 Search Console（10 分）、A-5 核對官方票價（15 分，可選）。

預覽網址：（人類完成 A-1 後填寫）
