import urllib.request as req
import bs4 as bs
import json
import os
import html
from urllib.parse import quote  # 用於處理空白與中文網址

# ======================================================
#  1) 目標網址與基本下載
# ======================================================
url = "https://www.fubonartmuseum.org/Exhibitions"

response = req.urlopen(url)

# 判斷 HTTP 狀態是否為 200（成功）
if hasattr(response, "status"):
    if response.status != 200:
        print(f"下載失敗，HTTP 狀態碼: {response.status}")
        print("程式結束。")
        exit()
else:
    print("無法確認 HTTP 狀態，可能 urllib 版本不同。")

content = response.read()
if not content:
    print("下載失敗：網站回傳空內容。")
    print("程式結束。")
    exit()

# ======================================================
#  2) 用 BeautifulSoup 解析 HTML
# ======================================================
html_doc = bs.BeautifulSoup(content, "html.parser")

# ======================================================
#  3) 精準定位「現正展出」區塊 (On Now)
# ======================================================
on_now_header = html_doc.find("h3", string="On Now")
if on_now_header is None:
    print("找不到 'On Now' 標題，可能網站結構有變動。")
    print("程式結束。")
    exit()

on_now_section = on_now_header.find_parent("section")
if on_now_section is None:
    print("找不到 'On Now' 的 <section> 區塊，可能網站結構有變動。")
    print("程式結束。")
    exit()

# ======================================================
#  4) 抓取展覽卡片
# ======================================================
exhibitions = on_now_section.find_all("a", class_="fb-exhibitions-card")
if len(exhibitions) == 0:
    print("在 'On Now' 區塊內找不到展覽卡片。")
    print("程式結束。")
    exit()

# ======================================================
#  5) 建立 Downloads 資料夾
# ======================================================
current_dir = os.getcwd()
downloads_dir = os.path.join(current_dir, "Downloads")

if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)
    print(f"已建立資料夾: {downloads_dir}")
else:
    print(f"資料夾已存在: {downloads_dir}")

# ======================================================
#  6) 解析展覽資訊 + 下載圖片
# ======================================================
base_url = "https://www.fubonartmuseum.org"
result = []

for expo in exhibitions:
    # -----------------------------
    # (a) 展覽連結
    # -----------------------------
    href_value = expo.get("href")
    if href_value:
        link = base_url + href_value
    else:
        link = "(無連結)"

    # -----------------------------
    # (b) 中文標題
    # -----------------------------
    title_tag = expo.find("h2", class_="font-h2 font-bold")
    title = title_tag.get_text(strip=True) if title_tag else "(無標題)"

    # -----------------------------
    # (c) 英文標題
    # -----------------------------
    eng_title_tag = expo.find("h3", class_="font-h3")
    eng_title = eng_title_tag.get_text(strip=True) if eng_title_tag else "(無英文標題)"

    # -----------------------------
    # (d) 展期與地點
    # -----------------------------
    info_tags = expo.find_all("p", class_="font-body-en")
    date = info_tags[0].get_text(strip=True) if len(info_tags) >= 1 else "(未提供展期)"
    location = info_tags[1].get_text(strip=True) if len(info_tags) >= 2 else "(未提供地點)"

    # -----------------------------
    # (e) 圖片下載
    # -----------------------------
    img_tag = expo.find("img")
    if img_tag is not None:
        img_url = img_tag.get("src")
        img_url = html.unescape(img_url)  # 轉換 HTML 實體
        encoded_url = quote(img_url, safe=':/')  # URL 編碼（處理空白與中文）

        filename_part = os.path.basename(img_url)
        filename_no_ext = os.path.splitext(filename_part)[0]
        image_filename = filename_no_ext + ".jpg"
        image_path = os.path.join(downloads_dir, image_filename)

        # 用 os.system("curl") 方式嘗試下載（比 urlretrieve 更容錯）
        cmd = f'curl -L -o "{image_path}" "{encoded_url}"'
        result_code = os.system(cmd)

        if result_code == 0 and os.path.exists(image_path):
            print(f"已下載圖片: {image_filename}")
        else:
            print(f"圖片下載失敗: {encoded_url}")
            image_filename = "(下載失敗)"
    else:
        encoded_url = "(無圖片)"
        image_filename = "(無圖片)"
        print("未找到圖片，略過。")

    # -----------------------------
    # (f) 顯示結果
    # -----------------------------
    print("展覽名稱:", title)
    print("英文名稱:", eng_title)
    print("展覽日期:", date)
    print("展覽地點:", location)
    print("展覽連結:", link)
    print("圖片連結:", encoded_url)
    print("-" * 60)

    # -----------------------------
    # (g) 加入 JSON 結構
    # -----------------------------
    record = {
        "title": title,
        "eng_title": eng_title,
        "date": date,
        "location": location,
        "link": link,
        "image_url": encoded_url,
        "image_file": image_filename
    }
    result.append(record)

# ======================================================
#  7) 擷取美術館場館資訊
# ======================================================
venue_info = {}
footer = html_doc.find("footer")

if footer is not None:
    footer_texts = footer.find_all("p")
    footer_data = []
    for p in footer_texts:
        text = p.get_text(separator="\n", strip=True)
        if text != "":
            footer_data.append(text)
    venue_info["texts"] = footer_data
else:
    venue_info["texts"] = ["未找到 footer 區塊，可能網站結構變動"]
    print("警告：未找到 footer 區塊。")

print("\n===== 場館資訊 =====")
for line in venue_info["texts"]:
    print(line)
print("=====================\n")

# ======================================================
#  8) 輸出 JSON 檔案
# ======================================================
output_path = os.path.join(downloads_dir, "fubon_on_now.json")

if len(result) == 0:
    print("未找到任何展覽資料，JSON 不會輸出。")
    print("程式結束。")
    exit()

final_output = {
    "exhibitions": result,
    "venue_info": venue_info
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)

print(f"已輸出 JSON 檔案至: {output_path}")