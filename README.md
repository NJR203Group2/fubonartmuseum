# 富邦美術館展覽資訊爬蟲（Fubon Art Museum Web Crawler）

本專案為一個以 Python 撰寫的網頁爬蟲程式，用於自動抓取富邦美術館（Fubon Art Museum）網站上之展覽資訊。  
主要功能包含「現正展出 (On Now)」與「即將發生 (Upcoming)」兩個展覽區塊，並能深入每個展覽內頁，擷取詳細資料、下載展覽圖片及 QR Code。

---

## 專案結構

```
fubon_art_museum/
│
├── fubon_art_museum.py      # 主程式：流程控制、輸出 JSON
├── fubon_utils.py           # 自訂模組：爬蟲核心邏輯（HTML 解析與資料擷取）
├── Downloads/               # 爬蟲輸出資料夾（圖片與 JSON）
└── README.md                # 專案說明文件
```

---

## 功能說明

### 1. 網頁來源
- 主要爬取網址：  
  [https://www.fubonartmuseum.org/Exhibitions](https://www.fubonartmuseum.org/Exhibitions)

- 同時擷取兩個展覽區塊：
  - 現正展出 (On Now)
  - 即將發生 (Upcoming)

---

### 2. 爬取項目
爬蟲會從展覽列表頁與內頁中擷取以下欄位：

| 欄位名稱 | 說明 |
|-----------|------|
| title | 展覽中文名稱 |
| eng_title | 展覽英文名稱 |
| date | 展期（自內頁擷取，格式如 2025.10.23 - 2026.4.20） |
| location | 展覽地點（自內頁擷取） |
| link | 展覽內頁連結 |
| cover_image_url | 展覽封面圖片網址 |
| cover_image_file | 展覽封面圖片儲存檔名（含展覽名稱前綴） |
| description | 展覽內頁介紹文字 |
| detail_qr_image_file | 內頁 QR Code 圖片檔名（含展覽名稱前綴） |

---

### 3. 圖片下載規則

- 所有圖片皆儲存在 `Downloads/` 資料夾。
- 圖片檔名會在原檔名前加上展覽名稱，例如：

  ```
  富邦典藏展_2_2592_x_1458.jpg
  安東尼麥考爾在光中遇見你_安東尼_官網_桌機.jpg
  ```

- QR Code 圖片亦會以展覽名稱與展覽代號命名，例如：

  ```
  富邦典藏展_qr_X0087XPM.png
  ```

---

### 4. JSON 輸出內容

最終會輸出一個 `fubon_exhibitions.json` 檔案，包含以下三個主要區塊：

```json
{
  "on_now": [...],
  "upcoming": [...],
  "venue_info": {
    "texts": [
      "富邦美術館",
      "110台北市信義區松高路79號",
      "聯繫電話 +886-2-6623-6771",
      "開放時間：11:00 - 18:00"
    ]
  }
}
```

---

## 執行環境

- Python 版本：3.10 以上（建議使用 3.12 或更新版）
- 必要套件：
  ```
  beautifulsoup4
  ```

如使用虛擬環境，可執行：
```bash
pip install beautifulsoup4
```

---

## 使用方式

1. 下載或複製此專案至本機：
   ```bash
   git clone https://github.com/yourname/fubon_art_museum.git
   cd fubon_art_museum
   ```

2. 確保 Python 環境可執行後，直接執行主程式：
   ```bash
   python fubon_art_museum.py
   ```

3. 程式執行後：
   - 所有封面圖與 QR Code 會自動下載至 `Downloads/` 資料夾。
   - 展覽資訊會輸出為 `Downloads/fubon_exhibitions.json`。

---

## 程式流程概要

1. 讀取主頁 HTML（`/Exhibitions`）
2. 解析「On Now」與「Upcoming」區塊
3. 擷取各展覽：
   - 展覽名稱
   - 日期與地點
   - 封面圖片
4. 進入展覽內頁（`/ExhibitionDetail?PKNO=...`）
   - 解析展期、地點、展覽介紹、QR Code
5. 合併資料並輸出 JSON 檔

---

## 注意事項

1. 若網站結構有變動（例如 CSS class 名稱不同），爬蟲可能需要更新選擇器。
2. 若展覽圖片包含中文或空白字元，系統會自動進行 URL 編碼。
3. 本程式僅用於學術與資料處理練習，請勿用於商業用途。

---

## 範例輸出（摘要）

```json
{
  "title": "《富邦典藏展》",
  "eng_title": "Fubon Collection",
  "date": "2025.10.23 - 2026.4.20",
  "location": "富邦美術館 3樓 星光展廳",
  "link": "https://www.fubonartmuseum.org/ExhibitionDetail?PKNO=X0087XPM",
  "cover_image_file": "富邦典藏展_2_2592_x_1458.jpg",
  "description": "富邦藝術基金會自1997年成立以來，長期關注二十世紀華人及世界各地重要藝術家的精彩作品。",
  "detail_qr_image_file": "富邦典藏展_qr_X0087XPM.png"
}
```

---

## 授權條款

本專案僅供個人學習與研究用途。  
若需使用此程式進行公開資料發佈或商業應用，請遵守富邦美術館網站之使用規範。
