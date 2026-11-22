# 人類待辦（每天約 1 小時）

格式：`- [ ] [project] 事項（預估時間）— 說明連結`

- [ ] [主控] 每晚 10 點看推播與 `reports/` 當日回報（10 分鐘）

## Project A：走啊敢不敢（旅遊試算工具站）

程式碼在分支 `claude/gifted-ride-nnfsux`，路徑 `ai-hustle/projects/japan-travel-site/site/`。2026-11-22 品牌改為「走啊敢不敢」，日本內容都在 `/japan/` 之下。

> **部署平台：請直接用 Cloudflare Pages（A-0）。** Vercel Hobby（免費）方案只限個人、非商業用途，網站之後要放聯盟連結就屬商業用途。**開始放聯盟連結（A-6）之前一定要完成 A-0。** 如果還沒做 A-1，就跳過 A-1 直接做 A-0；已經部署到 Vercel 的話，照 A-0 第 7 步搬家。

- [ ] [japan-travel-site] A-0 部署到 Cloudflare Pages（15 分鐘；**要註冊 Cloudflare 帳號，需你決定**）— 開始放聯盟連結前要完成
  1. 到 https://dash.cloudflare.com/sign-up 註冊或登入（免費方案即可）。
  2. 左側 **Workers & Pages** → **Create** → 選 **Pages** 分頁 → **Connect to Git** → 授權 GitHub → 選 `timfrom2007/git-test`。
  3. 設定（照填）：
     - Production branch：`claude/gifted-ride-nnfsux`（主控合併到 main 後改成 `main`）
     - Framework preset：**Astro**
     - Build command：`npm run build`
     - Build output directory：`dist`
     - Root directory（Advanced 裡）：`ai-hustle/projects/japan-travel-site/site`
     - Environment variables：`NODE_VERSION` = `22`；`SITE_URL` = `https://<專案名>.pages.dev`（有正式網域後改成網域，見 A-3）
  4. 按 **Save and Deploy**，約 1–2 分鐘。打開 `https://<專案名>.pages.dev`，確認：
     - 首頁顯示「走啊敢不敢」和「選目的地」；
     - `/japan/tools/jr-pass-calculator/` 點「東京⇄大阪⇄廣島」應顯示關西＋廣島周遊券最划算；
     - 打開舊網址 `/tools/jr-pass-calculator/` 會自動跳到 `/japan/tools/jr-pass-calculator/`（301 轉址由 `site/public/_redirects` 設定）。
  5. 把 `pages.dev` 網址貼回 `projects/japan-travel-site/STATUS.md`「需要人類做什麼」下方。
  6. （有網域後）Pages 專案 → **Custom domains** → **Set up a custom domain** → 輸入網域。網域在 Cloudflare 管 DNS 時會自動設定；在別家註冊商就照畫面加 CNAME。改完 `SITE_URL` 後 → **Deployments** → 最新一筆 → **Retry deployment**。
  7. （只有已經用過 Vercel 才需要）Cloudflare 版確認正常後：把網域 DNS 改指到 Cloudflare Pages（步驟 6）→ 等新網站生效 → 到 Vercel 專案 Settings → Domains 移除網域 → Settings → Advanced → **Delete Project**。Search Console 用同一個網域就不用重新驗證；如果原本只有 `vercel.app` 網址，到 Search Console 新增 `pages.dev` 或正式網域資源（A-4）。
  - Cloudflare 免費方案條款是否允許商業用途，請在註冊時看一下 Cloudflare 條款（agent 沒有替你做法律判斷）。

- [ ] [japan-travel-site] A-1（已被 A-0 取代，可跳過）用 Vercel 部署預覽版
  - 只在想先看預覽、還沒決定 Cloudflare 時使用。Vercel Hobby 不允許商業用途，放聯盟連結前要搬到 Cloudflare（A-0 第 7 步）。設定與 A-0 相同：Root Directory `ai-hustle/projects/japan-travel-site/site`、Framework Astro；舊路徑轉址由 `site/vercel.json` 處理。

- [ ] [japan-travel-site] A-2 決定並購買網域（15 分鐘，**會付費，需你決定**）
  1. 品牌「走啊敢不敢」之後不只日本，網域不要綁日本。候選（**agent 沒有查是否可註冊**，請自行到 Cloudflare Registrar 查價格與可用性）：`zouagan.com`、`daretogo.tw`、`goornot.tw`。
  2. 建議直接在 **Cloudflare Registrar** 買（以成本價續約，DNS 也在 Cloudflare，A-0 第 6 步最省事）。`.com` 一年通常約 US$10–12，以註冊商頁面為準。
  3. 不想付費也可以先用 `pages.dev` 網址上線，之後再換（換網域會損失部分搜尋累積，建議儘早決定）。

- [ ] [japan-travel-site] A-3 把網域接到網站（10 分鐘）
  1. 用 Cloudflare Pages：照 A-0 第 6 步。
  2. 把 `SITE_URL` 環境變數改成 `https://你的網域`，重新部署。這一步讓 sitemap、canonical、OG 圖網址改成正式網域。

- [ ] [japan-travel-site] A-4 設定 Google Search Console（10 分鐘）
  1. 到 https://search.google.com/search-console → **新增資源** → 選「網域」→ 輸入網域（不含 https）。
  2. 複製 Google 給的 TXT 記錄，到 DNS（Cloudflare → 網域 → DNS → Add record → TXT）新增 → 回 Search Console 按「驗證」（DNS 生效可能要幾分鐘，失敗就隔 10 分鐘再按）。
  3. 左側 **Sitemap** → 輸入 `sitemap-index.xml` → 提交。
  4. 上方「網址審查」依序貼上並按 **要求建立索引**：`/japan/`、`/japan/tools/jr-pass-calculator/`、`/japan/sakura/2027/`、`/japan/tools/japan-tax-refund/`（一天有配額，做不完隔天再做）。
  5. 完成日期寫進 `projects/japan-travel-site/STATUS.md`，驗收指標（30 天曝光 > 1,000、點擊 > 50）從這天起算。

- [x] ~~[japan-travel-site] A-5 核對官方票價（15 分鐘，可選但建議）~~ **已改由 agent 處理（A4，2026-11-22）**：網路權限開放後，agent 已逐項對照官方網站，結果見 `projects/japan-travel-site/STATUS.md`「A4 查證結果」。仍需人工確認的只剩少數幾項（JR 東日本、臺銀拒絕自動存取），列在同一節。

- [ ] [japan-travel-site] A-6 申請聯盟行銷帳號（每個約 15 分鐘，分天做；**是註冊帳號，需你決定**）
  **前提：A-0（Cloudflare Pages）已完成。**網站已在工具和文章裡預留聯盟連結位置，正式版目前不顯示。拿到連結後填進 `site/src/data/affiliates.json` 的 `url` 欄，就會自動顯示並加上「聯盟連結」揭露文字。
  建議順序（一天做一個）：
  1. **KKday 聯盟**：搜尋「KKday Affiliate」或「KKday 聯盟行銷」進官方申請頁 → 填網站網址（A-3 的正式網域，或 A-0 的 pages.dev 網址）與網站介紹「走啊敢不敢：旅行試算工具與懶人包（目前為日本：JR Pass／周遊券、退稅、預算、櫻花），繁中、台灣旅客」→ 送出等審核。
  2. **Klook 聯盟**：搜尋「Klook Affiliate Partner」→ 同上。
  3. **訂房**：Agoda Partners 或 Booking.com Affiliate Partner 擇一先申請。
  4. **eSIM／網卡**：審核通過的平台內通常有 eSIM 商品，可先用 KKday／Klook 的商品頁連結，不用另外申請。
  審核通過後，在平台後台產生以下商品的連結，貼到 STATUS.md 或直接改 `affiliates.json`：JR Pass 全國版、關西地區周遊券、賞櫻行程、日本 eSIM、訂房搜尋頁。
  注意：各平台條款（是否接受新網站、分潤比例、付款門檻）以申請頁為準，這裡沒有替你查證；有的平台要求網站先上線且有內容，建議 A-0 完成後再申請。

## Project B 短影音（B1／B2 交付，2026-11-22）
建議順序：B-1 → B-2 → B-3 當天做完；B-4 之後每 2–3 天一支。**10 支影片都已產好 `out/video.mp4`，可以直接上傳。**檔案都在 `ai-hustle/projects/short-video/`。

- [ ] [B] B-1 錄聲音樣本，讓 AI 用你的聲音產旁白（10 分鐘）
  - 先聽一支現有影片（例如 `videos/01-tax-free-refund/out/video.mp4`）知道目前 AI 聲音的程度。
  - 照 `projects/short-video/voice/RECORDING_GUIDE.md` 做：
    1. **建立私有 repo `ai-hustle-voice`**（本 repo 是公開 fork，不能放聲音樣本）。
    2. 安靜小房間、手機本體麥克風、距離 20 公分，照 `voice/script.txt` 念約 2 分鐘（第一段是同意聲明）。
    3. 檔名改 `sample.m4a`，上傳到 `ai-hustle-voice`。
    4. 在 `projects/short-video/STATUS.md`「人類決定」寫：`聲音樣本已上傳到 ai-hustle-voice，日期`。
  - 不想複製自己的聲音：寫 `旁白：Azure 台灣腔`（要另外註冊 Azure，見 `voice/README.md`），或 `旁白：每支自己錄`（舊流程：每支照 `narration.txt` 錄、上傳成該資料夾的 `voice.m4a`，同樣放私有 repo）。

- [ ] [B] B-1b 允許 AI 在雲端容器執行聲音複製模型（2 分鐘，Claude Code 設定）
  - 原因：AI 嘗試用開源模型 Fun-CosyVoice3（Apache-2.0，可商用）做 CPU 測試時，被 Claude Code 的自動權限檢查擋下兩次，AI 沒有繞過。
  - 做法（二選一）：
    1. 在這個 Project B 的 Claude 對話裡直接回覆：「允許執行 CosyVoice 聲音複製測試（只用我本人同意的聲音）」，AI 會再試一次，系統會跳出確認時按允許。
    2. 或在 Claude Code 設定中為 Bash 加入允許規則（見 Claude Code 文件「permissions」）。
  - 不允許也可以：改用 ElevenLabs（約 US$6／月，你自己操作網頁）或 Azure 台灣腔。

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
