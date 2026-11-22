# 影片 → 網站連結對照（Project A 維護）

更新：2026-11-22（Asia/Taipei）｜網站尚未部署。正式網域由人類完成 `control/human-todo.md` A-1／A-3 後決定，**請把下表路徑接在網域後面**，例如 `https://www.網域/tools/japan-tax-refund/`。

| 影片 | 主題 | 網站路徑（主要導流） | 補充連結 |
|---|---|---|---|
| 01 | 免稅改退稅制 | `/tools/japan-tax-refund/` | `/articles/japan-new-rules-2026-2027/` |
| 02 | 2027 新費用（出國稅、京都住宿稅、JESTA） | `/articles/japan-new-rules-2026-2027/` | `/tools/japan-trip-budget/` |
| 03 | 2027 櫻花規劃 | `/sakura/2027/` | `/articles/sakura-avoid-crowds-2027/`、`/articles/sakura-spots-access-2027/` |
| 04 | 札幌雪祭 2027 | `/articles/hokkaido-winter-2027/` | `/tools/japan-trip-budget/` |
| 05 | 白川鄉點燈 2027 | `/articles/hokuriku-winter-2027/` | `/tools/jr-pass-calculator/` |

## 成效追蹤建議（UTM）
在說明欄連結後加參數，Search Console 看不到，但之後接 GA 或 Vercel Analytics 就能分出影片帶來的流量：

```
?utm_source=youtube&utm_medium=shorts&utm_campaign=v01
```
IG 用 `utm_source=instagram`、Threads 用 `utm_source=threads`；`v01` 換成影片編號。

## 注意
- 頁面裡的「待確認」項目（例如白川鄉點燈官方日期、雪祭官方公告）和影片的待確認項目一致，官方公布後兩邊要一起改。
- 「主頁連結」若只能放一個網址，建議放首頁 `/`，首頁已列出所有工具。
