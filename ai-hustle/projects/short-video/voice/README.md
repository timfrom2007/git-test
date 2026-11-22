# 旁白真實度：聲音複製方案評估（B3）

查核日期：2026-11-22（Asia/Taipei）｜目標：台灣腔、像真人、可商用、成本低

## 我們的用量
每支影片旁白約 150–250 字，一週 3 支 → **每月約 3,000 字**。所有雲端方案的免費額度都遠大於這個量，所以「成本」主要看月費，不看字數。

## 比較表
| 方案 | 類型 | 自然度 | 台灣腔 | 權重／服務授權 | 成本 | CPU 速度（4 核，本容器） | 結論 |
|---|---|---|---|---|---|---|---|
| **Fun-CosyVoice3-0.5B**（阿里 FunAudioLLM） | 開源、零樣本複製（10–30 秒參考音） | 高（官方評測 CER 1.21%，見 [repo](https://github.com/FunAudioLLM/CosyVoice)） | 會跟著參考音的口音走 → **用人類自己的聲音就是台灣腔**（未實測） | **Apache-2.0**（[HF](https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512)）✅ 可商用 | 免費 | **未實測**（見下方「實測狀態」）；0.5B 參數的 LLM＋flow，預估每秒語音要數秒運算，一支 45 秒影片可能 3–10 分鐘 | **首選開源方案** |
| CosyVoice2-0.5B | 同上，前一版 | 高 | 同上 | **Apache-2.0** ✅ | 免費 | 未實測 | v3 的備案 |
| GPT-SoVITS | 開源、零樣本或 1 分鐘微調 | 高（微調後最像本人） | 跟參考音走 | **MIT**（code＋[預訓練權重](https://huggingface.co/lj1995/GPT-SoVITS)）✅；預訓練資料來源未完整說明 | 免費 | 推論可在 CPU；**微調在 CPU 不實際**（需 GPU） | 次選；想要「最像本人」時用 GPU 微調 |
| IndexTTS-2（bilibili） | 開源、零樣本 | 高 | 跟參考音走 | **bilibili 自訂授權**：月活 > 1 億或年營收 > 10 億人民幣才需另外授權；不得用來改進其他模型 | 免費 | 未實測 | 可商用但條款自訂，列備案 |
| OpenVoice V2 | 開源、音色轉換（底層就是我們現在的 MeloTTS） | 中 | ❌ 只換音色，**口音還是大陸腔** | **MIT** ✅ | 免費 | 快（接近現在） | 解決不了口音問題，不推薦 |
| F5-TTS | 開源 | 高 | 跟參考音走 | ❌ 權重 **CC-BY-NC-4.0** 不可商用 | — | — | **排除** |
| MaskGCT（Amphion） | 開源 | 高 | — | ❌ 權重 **CC-BY-NC-4.0** | — | — | **排除** |
| Spark-TTS-0.5B | 開源 | 中高 | — | ❌ 權重 **CC-BY-NC-SA-4.0** | — | — | **排除** |
| XTTS-v2（Coqui） | 開源 | 中 | — | ❌ **Coqui Public Model License**（非商用） | — | — | **排除** |
| Fish Speech／OpenAudio S1-mini | 開源 | 高 | — | ❌ 依官方說明為 **CC-BY-NC-SA**（本次 HF API 讀不到，待確認） | — | — | **排除** |
| **Azure AI Speech** zh-TW（HsiaoChen 女／YunJhe 男／HsiaoYu 女） | 雲端預建神經語音 | 高 | ✅ **道地台灣腔** | 官方商用 ✅ | **免費額度每月 50 萬字**（neural），我們用不完；超過才付費（美金單價請以[官方定價](https://azure.microsoft.com/pricing/details/cognitive-services/speech-services/)為準） | 雲端，秒出 | **最快能上線的台灣腔**，但不是人類本人的聲音 |
| Azure Personal Voice／Custom Neural Voice | 雲端聲音複製 | 很高 | ✅ | 需申請 **Limited Access** 審核，且不在一般定價內 | 另計 | 雲端 | 個人帳號很難申請到，不建議 |
| Google Cloud TTS（cmn-TW） | 雲端預建語音 | 中（Standard／WaveNet） | ✅ 台灣腔 | 官方商用 ✅ | WaveNet 免費額度每月約 400 萬字；Chirp 3 HD 約 US$30／百萬字、免費 100 萬字（[定價頁](https://cloud.google.com/text-to-speech/pricing)）；cmn-TW 是否有 Chirp 3 HD **待確認** | 雲端 | Azure 的備案；音質較舊 |
| **ElevenLabs** Instant Voice Cloning | 雲端聲音複製 | 很高 | 會跟著參考音（中文口音穩定度**未實測**） | 付費方案皆含商用授權 ✅（免費方案沒有） | **Starter 約 US$5–6／月**（3 萬 credits、含 IVC）；Creator 約 US$22／月（含 Professional Voice Cloning）。價格來自[第三方整理](https://dev.to/techsifted/elevenlabs-pricing-2026-plans-credits-and-api-costs-explained-1549)，以[官網](https://elevenlabs.io/pricing)為準 | 雲端，秒出 | 最省事的付費複製方案 |

## 建議
1. **主線：Fun-CosyVoice3＋人類自己的聲音**。免費、Apache-2.0 可商用、口音會像本人。人類只要錄一次 `voice/sample.m4a`（1–3 分鐘），之後每支影片都能自動產出「人類聲音」的旁白，不用每支都錄。
2. **如果 CPU 太慢或品質不夠**：
   - 想要本人聲音 → ElevenLabs Starter（約 US$6／月），或租 GPU 跑 GPT-SoVITS 微調。
   - 不在乎是不是本人、只要台灣腔 → Azure zh-TW（免費額度內 0 元，人類要註冊 Azure）。
3. 不採用：所有 NC（非商用）權重的模型，以及只換音色、不換口音的 OpenVoice。

## 實測狀態（重要）
- ✅ 已在容器內裝好 CosyVoice（CPU 版 PyTorch 2.3.1、Python 3.10 虛擬環境），並下載 Fun-CosyVoice3-0.5B 權重（約 9GB）。
- ✅ 已用現有 MeloTTS 合成一段 6.4 秒的**假參考音檔**（不是任何真人的聲音）。
- ❌ **執行聲音複製推論的指令被 Claude Code 的自動權限檢查（auto mode classifier）擋下兩次**（分類為 "Undermining Oversight"）。我沒有繞過它。所以 **CPU 速度與輸出品質目前都是未實測**。
- 要繼續，需要人類在 Claude Code 允許這一步（見 `control/human-todo.md` 的 B-1b）。允許後的測試指令：
  ```bash
  cd <scratchpad>/CosyVoice && .venv/bin/python <scratchpad>/clone/run.py <scratchpad>/clone
  ```
  `run.py` 只做一件事：用假參考音檔＋一句影片 01 的台詞做零樣本合成，印出載入時間與合成時間。
- 注意：容器是暫時的，重開 session 後虛擬環境與 9GB 權重要重新下載（約 5 分鐘）。

## 倫理與安全
- 只複製**人類本人、明確同意**的聲音。錄音稿第一段就是同意聲明（見 `script.txt`），檔案留在 repo 當紀錄。
- 不複製任何名人、其他創作者或第三方的聲音。
- 影片若使用複製聲音，上傳 YouTube 時「變造或合成內容」依實際情況勾選（複製本人聲音念本人寫的稿，一般屬於可揭露也可不揭露的範圍；不確定時勾「是」）。
- 聲音樣本可以被拿來複製人類的聲音。`timfrom2007/git-test` 是**公開的 fork**（2026-11-22 查核），不能改成私有，所以樣本**放在另一個私有 repo `ai-hustle-voice`**，不放在這裡；AI 產出的旁白只把最終影片放回公開 repo。`.gitignore` 也擋掉了 `voice/sample.*`，避免誤傳。
