# Shot Tracker：籃球投籃軌跡分析（Phase 0 原型）

從**側面拍攝**的投籃影片中追蹤籃球、擬合拋物線，算出每一球的：

| 指標 | 說明 |
|---|---|
| 進／不進 | 失手會再分成 `short`（打前框）、`long`（打後框）、`rim_out` |
| 出手角度、出手速度、出手高度 | 在球離手那一刻計算 |
| 最高點高度 | 弧度有多高 |
| **入框角度** | 球落到籃框高度時的角度，理想約 43–47° |
| **深度** | 球通過籃框高度時，在籃框中心前（−）或後（+）多少 cm，理想約 +5～+8 |

最後會根據整段練習的平均值和一致性，給出中文的建議。

規劃與後續階段請見 [docs/plan.md](docs/plan.md)。

## 在 Windows 上安裝

```powershell
cd shot-tracker
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 使用方式

**1. 先用合成影片試跑**（不需要自己的影片）

```powershell
python -m shot_tracker synth --out demo
python -m shot_tracker analyze demo\synthetic.mp4 --rim demo\rim.json --out results
```

**2. 分析自己的影片**

```powershell
# 在畫面上依序點擊籃框的左緣、右緣，按 Enter 存檔
python -m shot_tracker pick-rim videos\my_shots.mp4 --out videos\rim.json

python -m shot_tracker analyze videos\my_shots.mp4 --rim videos\rim.json --out results
```

輸出（在 `results\`）：

- `annotated.mp4`：疊上軌跡、數據和命中數的影片
- `overlay.png`：所有出手的軌跡畫在同一張圖（綠色＝進，紅色＝不進）
- `shots.csv`、`report.json`：每一球的數據和整體統計

## 拍攝規格

- 手機固定在三腳架上，放在**投籃者與籃框連線的側面**，鏡頭盡量和這條線垂直
- **出手點和籃框都要在畫面內**（出手點在畫面外，就量不到出手角度）
- 橫拍、1080p、**60fps 以上**（慢動作 120/240fps 更好）
- 背景裡最好不要有其他會動的橘色物體

## 運作原理

1. **偵測**：橘色 + 移動偵測（背景相減），用籃框寬度推算球應該有多大，藉此過濾雜訊
2. **追蹤**：用「等速 + 重力」預測下一格的位置，把偵測結果串成軌跡
3. **擬合**：從最高點到籃框這段（一定是自由飛行）先擬合，再往回延伸，直到點不再落在拋物線上，那一點就是出手點
4. **換算**：籃框直徑 45.72 cm，用來把像素換算成公分
5. **品質檢查**：`gravity_ratio` 是擬合出來的重力 ÷ 9.81。接近 1.0 代表拍攝角度和比例尺正確；明顯偏離的話，表示鏡頭沒有和投籃方向垂直

## 已知限制

- 側面拍攝**看不到左右偏差**。偏左或偏右的失手，可能被誤判成進球，之後可以用球網晃動或第二支手機改善
- 顏色偵測對光線很敏感，可以改用 `--detector yolo`（要另外 `pip install ultralytics`，屬於 AGPL 授權）
- 一次只追蹤一顆球

## 測試

```powershell
python -m pytest
```
