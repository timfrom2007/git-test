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

- [ ] [japan-travel-site] A-6 申請聯盟行銷帳號（每個約 15 分鐘，分天做；**是註冊帳號，需你決定**）
  網站已在工具和文章裡預留聯盟連結位置，正式版目前不顯示。拿到連結後填進 `site/src/data/affiliates.json` 的 `url` 欄，就會自動顯示並加上「聯盟連結」揭露文字。
  建議順序（一天做一個）：
  1. **KKday 聯盟**：搜尋「KKday Affiliate」或「KKday 聯盟行銷」進官方申請頁 → 填網站網址（用 A-1 的 vercel.app 網址或 A-3 的正式網域）與網站介紹「日本鐵道 JR Pass／周遊券試算與櫻花季懶人包，繁中、台灣旅客」→ 送出等審核。
  2. **Klook 聯盟**：搜尋「Klook Affiliate Partner」→ 同上。
  3. **訂房**：Agoda Partners 或 Booking.com Affiliate Partner 擇一先申請。
  4. **eSIM／網卡**：審核通過的平台內通常有 eSIM 商品，可先用 KKday／Klook 的商品頁連結，不用另外申請。
  審核通過後，在平台後台產生以下商品的連結，貼到 STATUS.md 或直接改 `affiliates.json`：JR Pass 全國版、關西地區周遊券、賞櫻行程、日本 eSIM、訂房搜尋頁。
  注意：各平台條款（是否接受新網站、分潤比例、付款門檻）以申請頁為準，這裡沒有替你查證；有的平台要求網站先上線且有內容，建議 A-1 完成後再申請。

## Project B 短影音（B1／B2 交付，2026-11-22）
建議順序：B-1 → B-2 → B-3 當天做完；B-4 之後每 2–3 天一支。**10 支影片都已產好 `out/video.mp4`，可以直接上傳。**檔案都在 `ai-hustle/projects/short-video/`。

- [ ] [B] B-1 聽範例影片，決定旁白用 AI 還是自己錄（5 分鐘）
  1. 在 GitHub 打開 `ai-hustle/projects/short-video/videos/01-tax-free-refund/out/video.mp4`（分支 `claude/gifted-ride-nnfsux`）→ 按「Download raw file」。
  2. 用手機看完 44 秒。重點聽：口音（AI 是大陸普通話口音）、數字有沒有念錯。
  3. 在 `projects/short-video/STATUS.md` 最下面「人類決定」寫一行：`旁白：AI` 或 `旁白：自己錄`。
     - 選「自己錄」：每支照該資料夾的 `narration.txt` 念（約 1 分鐘），**每段 [1][2]… 之間停 1 秒**，用 iPhone「語音備忘錄」錄一次就好，念錯就從那段重念。
       傳到 repo：GitHub 網頁打開該影片資料夾 →「Add file」→「Upload files」→ 檔名改成 `voice.m4a` → Commit。AI 會自動切段、對齊字卡字幕、縮短停頓，重新產出影片。

- [ ] [B] B-2 確認帳號名稱並註冊 YouTube 頻道＋IG 帳號（15 分鐘）
  1. 推薦名稱：**日本行前60秒**（其他候選見 `positioning.md`）。若要跟網站同名，先跟主控確認網站名稱。
  2. YouTube：手機 YouTube App → 頭像 →「你的頻道」→ 建立頻道 → 名稱填「日本行前60秒」→ 帳號代碼依序試 `@japan60s`、`@japan.before60`、`@xingqian60`。
  3. 頻道說明貼上：`出發去日本前，60 秒搞懂新規則、日期和怎麼省錢。每支影片都附資料來源。`
  4. IG：新帳號用同一名稱與 handle → 設定 → 帳號類型改「創作者」（不要選「商家」，商家帳號不能用熱門音樂）。
  5. 把最後用的 handle 寫在 `STATUS.md`「人類決定」。

- [ ] [B] B-3 看 5 個參考帳號現況（10 分鐘）
  1. 在 YouTube／IG 搜尋：三原JAPAN、阿倫頻道 Alan Channel、樂吃購！日本、LIVE JAPAN、MATCHA。
  2. 每個帳號點「Shorts／Reels」→ 依熱門排序 → 記下前 3 支的：題材、長度、第一句話。
  3. 隨手寫在 `research.md` 第 5 節表格旁（格式不拘，條列即可）。

- [ ] [B] B-4 上傳第 1 支 Shorts（YouTube 10 分鐘＋IG／Threads 5 分鐘）— 需先完成 B-2
  1. 下載 `videos/01-tax-free-refund/out/video.mp4`（旁白若選自己錄，等 AI 重新合成後再下載）。
  2. YouTube App →「＋」→「上傳影片」→ 選影片（直式、60 秒內會自動判定為 Shorts）。
  3. 標題：從 `videos/01-tax-free-refund/README.md` 的「標題」複製第 1 個。說明：複製「說明欄」整段＋「Hashtag」的 YouTube 那行。
  4. 觀眾設定：「否，這不是為兒童打造的內容」。「變造或合成內容」：字卡＋AI 旁白並非擬真的真人或事件，一般選「否」；不確定時選「是」比較保險。
  5. 發布。
  6. IG：「＋」→ Reels → 選同一支影片 → 封面選 `out/cover.jpg` → 說明貼「說明欄」＋IG 那行 hashtag → 分享。勾「同時分享到 Threads」若有此選項；沒有就到 Threads 另發一則：貼說明欄 3 個重點＋附影片。
  7. 在 `STATUS.md` 記下發布日期與連結。
  - 說明欄裡的 `🔗 {SITE_URL}…` 那行：網站還沒上線前**整行刪掉**；上線後 AI 會換成正式網址。
  - 之後照建議順序 01 → 02 → 06 → 03 → 04 → 07 → 05 → 08 → 09 → 10，每 2–3 天一支（理由見 `projects/short-video/STATUS.md`）。05 白川鄉發布前，先打開 https://shirakawa-go.gr.jp/ 確認 2027 日期（2 分鐘）。

- [ ] [B] B-5 每日回覆留言（每天 ≤ 10 分鐘，影片上線後開始）
  - 有人問的問題若影片沒講到，複製到 `projects/short-video/STATUS.md`「觀眾問題」，AI 會拿來做下一支。

- [ ] [B] B-6（可選）同一支影片再發一則 IG 輪播貼文（5 分鐘）— 建議在 Reels 發布 2～3 天後
  1. 下載該影片資料夾 `carousel/` 裡的全部圖片（01.jpg、02.jpg…）。
  2. IG「＋」→「貼文」→ 右上「選取多張」→ 照檔名順序選 → 說明貼 README 的「說明欄」（IG 版連結）＋IG hashtag → 分享。
  - 輪播圖每張都有完整文字，沒聲音也看得懂；適合被收藏、分享。
