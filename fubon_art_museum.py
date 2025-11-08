# fubon_art_museum.py
import urllib.request as req
import bs4 as bs
import json
import os
from fubon_utils import parse_exhibition_section  # 從自訂模組匯入函式
import csv

# ======================================================
#  主程式
# ======================================================
def main():
    url = "https://www.fubonartmuseum.org/Exhibitions"
    response = req.urlopen(url)
    content = response.read()
    html_doc = bs.BeautifulSoup(content, "html.parser")

    downloads_dir = os.path.join(os.getcwd(), "Downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    base_url = "https://www.fubonartmuseum.org"

    # 區塊
    on_now_section = html_doc.find("section", class_="section-now")
    upcoming_section = html_doc.find("section", class_="section-upcoming")

    on_now_result = parse_exhibition_section(on_now_section, "現正展出 On Now", base_url, downloads_dir)
    upcoming_result = parse_exhibition_section(upcoming_section, "即將發生 Upcoming", base_url, downloads_dir)

    # 場館資訊
    footer = html_doc.find("footer")
    venue_info = {}
    if footer:
        venue_info["texts"] = [p.get_text(strip=True) for p in footer.find_all("p") if p.get_text(strip=True)]
    else:
        venue_info["texts"] = ["未找到 footer 區塊"]

    # 輸出 JSON
    output_path = os.path.join(downloads_dir, "fubon_exhibitions.json")
    final_output = {"on_now": on_now_result, "upcoming": upcoming_result, "venue_info": venue_info}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

    print(f"\n已輸出 JSON 檔案至: {output_path}")

    # ======================================================
    #  輸出 JSON 檔案
    # ======================================================
    output_json_path = os.path.join(downloads_dir, "fubon_exhibitions.json")
    final_output = {
        "on_now": on_now_result,
        "upcoming": upcoming_result,
        "venue_info": venue_info
    }

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

    print(f"\n已輸出 JSON 檔案至: {output_json_path}")

    # ======================================================
    #  輸出 CSV 檔案
    # ======================================================
    output_csv_path = os.path.join(downloads_dir, "fubon_exhibitions.csv")

    # 合併 On Now + Upcoming 為同一張表
    combined_data = []
    for record in on_now_result:
        record["section"] = "On Now"
        combined_data.append(record)
    for record in upcoming_result:
        record["section"] = "Upcoming"
        combined_data.append(record)

    # 若有資料才寫入 CSV
    if combined_data:
        fieldnames = [
            "section",
            "title",
            "eng_title",
            "date",
            "location",
            "link",
            "cover_image_file",
            "cover_image_url",
            "description",
            "detail_qr_image_file"
        ]

        with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(combined_data)

        print(f"已輸出 CSV 檔案至: {output_csv_path}")
    else:
        print("未找到可寫入的展覽資料，未輸出 CSV。")

if __name__ == "__main__":
    main()