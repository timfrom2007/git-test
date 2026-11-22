# 01｜日本免稅變了！11 月起先付稅、出境才退

**優先度：最高（新制剛上路，搜尋與討論正熱）**｜長度約 44 秒｜導流：網站「退稅試算」工具（Project A 尚未完成時改導流「日本退稅新制懶人包」）

## 檔案
| 檔案 | 用途 |
|---|---|
| `scenes.json` | 唯一來源：每個場景的旁白、字卡、畫面建議。改這裡再重跑 `tools/make_video.py` |
| `narration.txt` | 旁白稿（真人錄音用） |
| `subtitles.srt` | 字幕（對齊 TTS 版本；真人錄音後請在剪輯軟體自動對齊或用 CapCut 自動字幕） |
| `storyboard.md` | 分鏡表（時間碼、畫面、字卡、旁白） |
| `out/video.mp4` | **可直接上傳的成品**（字卡動畫＋AI 旁白＋燒入字幕） |
| `out/cover.jpg` | 封面 1080×1920 |
| `carousel/01.jpg`… | IG 輪播圖 1080×1350（同一則貼文依序上傳） |
| `voice.m4a`（人類放） | 人聲錄音；放進來後重跑 `make_video.py` 就會改用人聲 |

## 標題（擇一，A/B 測試建議用前兩個）
1. 日本免稅變了！11月起結帳不再直接扣稅
2. 2026/11/1起日本退稅新制：沒刷護照＝白付10%
3. 去日本買藥妝前必看｜免稅改成「出境才退」

## 封面文字
- 主：**日本免稅 不能直接扣了**
- 副：2026/11/1 起新制｜沒刷護照＝白付10%

## 說明欄（YouTube／IG 通用）
```
日本從 2026/11/1 起把免稅改成「退稅方式（リファンド方式）」：
✅ 免稅店先付含稅價
✅ 購買日起 90 天內，出境時在機場／港口的免稅手續機台刷護照
✅ 消耗品在日本吃掉、用掉就不能退
✅ 密封袋、消耗品 50 萬日圓上限取消
退款方式依店家不同，結帳時先問清楚。

📌 退稅試算 → 主頁連結
🔗 {SITE_URL}/?utm_source=shorts&utm_medium=social&utm_campaign=01-tax-free-refund
資料來源：日本觀光廳、日本海關（查核 2026-11-22）
```

## 導流連結
- 目前：`{SITE_URL}/?utm_source=shorts&utm_medium=social&utm_campaign=01-tax-free-refund`（退稅試算（Project A 製作中，LINKS.md 出現後改為正式路徑））
- `{SITE_URL}` 在網站部署（human-todo A-1）後由 AI 換成正式網域。YouTube Shorts 與 IG 說明欄的連結不能點，主要靠「主頁連結」；Threads 的連結可以點。

## Hashtag
YouTube（放標題或說明欄最後，3 個以內最有效）：`#日本旅遊 #日本退稅 #日本免稅`
IG／Threads（5–8 個）：`#日本旅遊 #日本退稅 #日本免稅 #日本藥妝 #日本自由行 #日本新制 #出國必看 #日本旅遊攻略`

## 事實與來源（查核日期 2026-11-22）
| 內容 | 來源 |
|---|---|
| 2026/11/1 販售分起改為リファンド方式；先付含稅價，出境時經海關確認後由免稅店退還 | [觀光廳 リファンド方式とは](https://www.mlit.go.jp/kankocho/tax-free/page01_000001_00021.html)、[日本海關](https://www.customs.go.jp/kaigairyoko/taxrefund/jpn.htm) |
| 購買日起 90 天內、出境時於空港／海港免稅手續端末出示護照 | 同上 |
| 消耗品在日本國內消費則無法退 | 同上 |
| 取消消耗品／一般物品區分、消耗品 50 萬日圓上限、特殊包裝（密封袋） | [nippon.com](https://www.nippon.com/ja/japan-data/h02925/)、觀光廳 |
| 退款方式（信用卡、現金等）與手續費 | **待確認**：依各店家／退稅代辦業者而異，影片已註明「結帳時先問」 |

## 素材建議（搜尋關鍵字，見 `../ASSETS.md`）
Pexels：`japan drugstore`, `cashier receipt`, `airport passport`, `shopping bag japan`。
