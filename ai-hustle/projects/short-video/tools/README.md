# 自動產片工具評估與雛型

## 結論
**可行。** 在這個容器裡，用 `make_video.py` 從一份 `scenes.json` 自動產出 1080×1920、30fps、H.264＋AAC 的直式影片（字卡動畫＋AI 旁白＋燒入字幕＋進度條）、`.srt`、旁白稿、分鏡表、封面圖。一支 45 秒影片約 30 秒產完。

成品：`videos/01`～`10` 每支都有 `out/video.mp4`（33–48 秒，各約 2–4MB）。同一份 `scenes.json` 也能產 IG 輪播圖（`make_carousel.py`）。

## 用法
```bash
pip install sherpa-onnx soundfile numpy pillow     # ffmpeg、中文字型（文泉驛正黑）容器內已有
python3 tools/make_video.py videos/01-tax-free-refund            # 產出全部
python3 tools/make_video.py videos/01-tax-free-refund --no-video # 只更新 narration/srt/storyboard
python3 tools/make_video.py videos/01-tax-free-refund --bgm bgm.mp3
python3 tools/make_video.py videos/01-tax-free-refund --tts        # 資料夾有 voice.m4a 也強制用 TTS
python3 tools/make_carousel.py videos/01-tax-free-refund           # IG 輪播圖 → carousel/01.jpg…
```

## 人聲錄音模式
資料夾裡有 `voice.m4a`（或 `voice.mp3`／`voice.wav`，或用 `--voice 路徑`）時自動啟用：
1. ffmpeg 轉單聲道、濾低頻、音量標準化到 -16 LUFS。
2. 依音量偵測有聲段，取**最長的 N−1 個停頓**當場景分界（N＝場景數），所以人類只要在每段之間停約 1 秒。
3. 每段之間的停頓縮成 0.3 秒，字卡跟著換，字幕在段內依字數分配。
4. 自我檢查：任何一段的語速偏離中位數超過 2.2 倍會印出警告（通常是漏念、多念或段內停太久）；偵測到的段數比場景少會直接停止並說明。

驗證：用 TTS 合成一段「假錄音」（段間 0.8–1.4 秒隨機停頓、加底噪、轉 m4a），7 個場景的切點全部正確，每段長度誤差 < 0.2 秒。**還沒用真人手機錄音測過**，第一次請人類錄完後由 AI 檢查成品。

已知弱點：如果段內停頓比段間停頓還長（例如念到一半想很久），會切錯；遇到警告時請重錄那支或在段間停久一點。

## IG 輪播圖
`make_carousel.py` 產 1080×1350（4:5）：封面＋每個重點一張（附旁白全文當內文，沒聲音也看得懂）＋結尾（資料來源、查核日期）。超過 8 張會自動合併最後幾個重點。
第一次執行會從 GitHub 下載 TTS 模型（約 160MB）到 `~/.cache/short-video-tts/`（可用 `TTS_CACHE` 換位置）。

`scenes.json` 欄位：`say`（旁白／字幕）、`tts`（選填，給 TTS 念的版本，例如把數字改成國字）、`text`（大字卡）、`sub`（小字）、`badge`（標籤）、`visual`（給人類的 B-roll 建議）、`tone`（語氣提示）、`hold`（場景後多停幾秒）。頂層 `cover` 是封面。

## 試過的 TTS
| 方案 | 結果 | 備註 |
|---|---|---|
| Microsoft Edge TTS（`edge-tts`，zh-TW-HsiaoChen） | ❌ 容器網路擋住 `speech.platform.bing.com` | 台灣腔最自然；但這是非官方介面，**商用授權不明確**，不建議當正式產線 |
| espeak-ng | 可用但像機器人 | 不適合發布 |
| **MeloTTS zh_en（sherpa-onnx，離線）** | ✅ 採用 | 模型 **MIT 授權**（MyShell.ai），可商用；支援繁體字輸入、中英混讀 |

## 目前的限制（要誠實告訴人類）
1. **口音**：MeloTTS 中文是**大陸普通話口音**、只有一個女聲。台灣觀眾可能覺得「不像台灣人」，影響信任感。我在容器裡無法播放音檔，**沒有親耳驗證過音質**，請人類先聽 `01` 範例再決定。
2. **畫面**：目前只有漸層背景＋字卡，沒有實景 B-roll。資訊型內容可以接受，但加上實景畫面通常留存率更好。
3. **數字讀法**：日期、金額有時會念錯，所以 `scenes.json` 提供 `tts` 欄位改寫成國字。
4. 沒有背景音樂（可用 `--bgm` 加；音樂來源見 `videos/ASSETS.md`）。

## 建議的產線（依人類時間排序）
| 方案 | 人類時間／支 | 品質 |
|---|---|---|
| A. 直接上傳 `out/video.mp4` | 5 分鐘 | 能看；AI 口音 |
| **B. 人類用手機照 `narration.txt` 錄音（約 1 分鐘）→ 上傳成 `voice.m4a` → AI 重跑 `make_video.py`** | 10 分鐘 | 推薦：台灣口音、可信度高（已實作） |
| C. 人類用 CapCut 把 B-roll 疊在範例影片下半部 | 15 分鐘 | 最好，但吃時間 |


## 若要更好的台灣腔 TTS（需人類決定，可能有成本）
- Azure AI Speech（zh-TW 神經語音，官方商用授權，有免費額度）：需要人類申請 Azure 帳號並把 API key 設成環境的網路密鑰；需在環境網路允許清單加入對應主機。
- Google Cloud Text-to-Speech（cmn-TW）：同上。
這兩項屬於「註冊／可能付費」，依 RULES 第 2 條，沒有人類同意前不做。
