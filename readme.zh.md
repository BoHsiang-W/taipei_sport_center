
[English Version](./readme.md)

## 北市運動中心預約狀態查詢系統

本專案是一個基於 Streamlit 的網頁應用程式，用於查詢並顯示台北市各運動中心的可預約時段。系統會即時從官方預約平台獲取資料，並以表格方式友善呈現。

### 功能特色

- 選擇運動類型（如羽球）
- 選擇單一天或日期區間
- 選擇特定運動中心
- 以表格方式顯示所有可預約時段
- 資料即時從官方預約 API 取得

### 環境需求

- Python 3.13+
- [Streamlit](https://streamlit.io/)
- [pandas](https://pandas.pydata.org/)
- [requests](https://docs.python-requests.org/)
- tqdm（可選，用於進度條）

安裝套件：

```bash
# 建議使用 uv 建立虛擬環境
uv venv -p 3.13
# 安裝所需套件
uv pip install -r requirements.txt
```

### 執行方式

1. 在專案目錄下開啟終端機。
2. 執行 Streamlit 應用程式：
   ```bash
   uv run streamlit run sport_center_info.py
   ```
3. 瀏覽器會自動開啟，請輸入運動類型、選擇日期/時間與場館，即可查詢可預約時段。

### 專案結構

- `sport_center_info.py` - 主程式與查詢邏輯
- `readme.md` - 專案說明文件（英文）

### 注意事項

- 本系統資料來源為台北市運動中心官方預約平台，時段與資訊正確性依賴外部 API。
- 建議使用穩定的網路環境以獲得最佳體驗。
