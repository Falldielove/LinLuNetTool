# LinLu工具箱使用說明

## 快速開始

1. 執行 `Installing Python Prerequisites.bat` 安裝必要的 Python 庫。
2. 運行 `start_all.bat` 啟動所有工具。

## 功能概覽

- Ma2cd 轉譜器
- XML 生成器
- 圖片和 PV 背景轉換工具

## 使用注意事項

### 轉譜器

1. 將譜面文件放入 `input` 文件夾。
2. 轉換後的文件將輸出到 `output` 文件夾。
3. 請勿刪除 `input` 中的 `music_template.xml`。

### 譜面文件格式

- 僅保留 `&inote_X=(124){1},,,{4},,` 格式的內容。
- 每個文件只能包含一個 `&inote_X`。
- X 為譜面編號，可自定義。

### 圖片轉換

- 將原始圖片放入 `img input` 文件夾。
- 自動生成 200x200 和 400x400 尺寸的封面。

### PV 背景轉換

- 將影片或圖片放入 `dat_input` 文件夾。
- 自動轉換為 .dat 格式。

## 注意事項

- 如遇防毒軟件報錯，可暫時關閉。
- 確保譜面文件格式正確，避免出現異常符號。
- 轉譜不支持使用 # 調整滑星（Slide）語法。

## 版本信息

當前版本：Ver.1.5

## 未來計劃

- CMD 窗口直接設置偏移
- 批量轉換功能
- 完善 .awb、.acb 音源生成
- 擴展 .dat PV 轉換功能

## 反饋與支持

如遇問題或有建議，請聯繫開發團隊。感謝您的使用和支持！
