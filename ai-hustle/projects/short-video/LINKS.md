# 影片 → 網站連結對照（Project A 維護）

更新：2026-11-22（Asia/Taipei）｜品牌「走啊敢不敢」改版後，日本內容都在 `/japan/` 之下。網站尚未部署，正式網域決定後，**把下表路徑接在網域後面**，例如 `https://網域/japan/tools/japan-tax-refund/`（README 裡的 `{SITE_URL}` 就是網域）。

| 影片 | 主題 | 網站路徑（主要導流） | 補充連結 |
|---|---|---|---|
| 01 | 免稅改退稅制 | `/japan/tools/japan-tax-refund/` | `/japan/articles/japan-new-rules-2026-2027/` |
| 02 | 2027 新費用（出國稅、京都住宿稅、JESTA） | `/japan/articles/japan-new-rules-2026-2027/` | `/japan/tools/japan-trip-budget/` |
| 03 | 2027 櫻花規劃 | `/japan/sakura/2027/` | `/japan/articles/sakura-avoid-crowds-2027/`、`/japan/articles/sakura-spots-access-2027/` |
| 04 | 札幌雪祭 2027 | `/japan/articles/hokkaido-winter-2027/` | `/japan/tools/japan-trip-budget/` |
| 05 | 白川鄉點燈 2027 | `/japan/articles/hokuriku-winter-2027/` | `/japan/tools/jr-pass-calculator/` |
| 06 | JR Pass 漲價：官網 vs 代理商 | `/japan/articles/jr-pass-price-2026/` | `/japan/tools/jr-pass-calculator/` |
| 07 | 東京⇄大阪 JR Pass 實算 | `/japan/articles/tokyo-osaka-shinkansen-jr-pass/` | `/japan/tools/jr-pass-calculator/` |
| 08 | 賞櫻避人潮 | `/japan/articles/sakura-avoid-crowds-2027/` | `/japan/sakura/2027/` |
| 09 | 追櫻 3 路線 | `/japan/sakura/2027/` | `/japan/articles/sakura-avoid-crowds-2027/` |
| 10 | 最容易漏算的 4 筆錢 | `/japan/tools/japan-trip-budget/` | `/japan/tools/japan-tax-refund/` |

- 頻道「主頁連結」只能放一個網址時：放日本入口 `/japan/`（列出所有日本工具與文章）。之後有其他目的地，再改成首頁 `/`。
- **舊路徑**（`/tools/…`、`/articles/…`、`/sakura/…`、`/sources/…`）已設定 301 轉到 `/japan/…`（`site/public/_redirects` 給 Cloudflare Pages，`site/vercel.json` 給 Vercel），就算有舊連結流出也不會壞。新的說明欄請一律用 `/japan/` 路徑。

## 成效追蹤（UTM）
```
?utm_source=youtube&utm_medium=shorts&utm_campaign=v01
```
IG 用 `utm_source=instagram`、Threads 用 `utm_source=threads`；`v01` 換成影片編號。之後接 Cloudflare Web Analytics 或 GA 就能分出影片帶來的流量。

## 注意
- 頁面與影片的事實要一致。A4 查證後，影片 05 的旁白和官方資料不符（參加方式是 5 種、展望台券不單賣），詳見 `projects/japan-travel-site/STATUS.md`「影片影響清單」。
