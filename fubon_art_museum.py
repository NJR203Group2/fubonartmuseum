# fubon_art_museum.py
import urllib.request as req
import bs4 as bs
import json
import os
from fubon_utils import parse_exhibition_section
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

    # ------------------------------------------------------
    # 解析展覽區塊
    # ------------------------------------------------------
    on_now_section = html_doc.find("section", class_="section-now")
    upcoming_section = html_doc.find("section", class_="section-upcoming")

    on_now_result = parse_exhibition_section(on_now_section, "現正展出 On Now", base_url, downloads_dir)
    upcoming_result = parse_exhibition_section(upcoming_section, "即將發生 Upcoming", base_url, downloads_dir)

    # ------------------------------------------------------
    # 解析 Footer (場館資訊)
    # ------------------------------------------------------
    footer = html_doc.find("footer", class_="fb-layout-footer")
    venue_info = {}

    if footer:
        # ===================== 聯絡資訊區塊 =====================
        contact_block = footer.find("div", class_="footer_contact")
        if contact_block:
            # 館名與地址
            address_block = contact_block.find("div", class_="contact_address")
            if address_block:
                address_text = address_block.get_text(separator=" ", strip=True)
                venue_info["name"] = address_text.split(" ")[0] if address_text else "(未提供館名)"
                venue_info["address"] = address_text if address_text else "(未提供地址)"
            else:
                venue_info["name"] = "(未提供館名)"
                venue_info["address"] = "(未提供地址)"

            # 聯絡資訊 (電話、傳真、郵件)
            others_block = contact_block.find("div", class_="contact_others")
            venue_info["phone"] = "(未提供電話)"
            venue_info["fax"] = "(未提供傳真)"
            venue_info["email"] = "(未提供郵件)"

            if others_block:
                for item in others_block.find_all("div", class_="others_item"):
                    label_tag = item.find("p", class_="item_label")
                    label_text = label_tag.get_text(strip=True) if label_tag else ""
                    value_p = item.find_all("p", class_="font-sm")
                    value_a = item.find("a", class_="footer_button")

                    if "電話" in label_text and value_p:
                        venue_info["phone"] = value_p[-1].get_text(strip=True)
                    elif "傳真" in label_text and value_p:
                        venue_info["fax"] = value_p[-1].get_text(strip=True)
                    elif "郵件" in label_text and value_a:
                        venue_info["email"] = value_a.get_text(strip=True)

            # 開放時間
            schedule_block = contact_block.find("div", class_="contact_schedule")
            if schedule_block:
                venue_info["open_hours"] = schedule_block.get_text(separator=" ", strip=True)
            else:
                venue_info["open_hours"] = "(未提供開放時間)"

        # ===================== 社群連結 =====================
        social_links = footer.select("div.app_social a.footer_button")
        venue_info["social_links"] = {}
        for link in social_links:
            name = link.get_text(strip=True)
            href = link.get("href", "").strip()
            if href.startswith("/"):
                href = f"{base_url}{href.lstrip()}"
            venue_info["social_links"][name] = href

        # ===================== 政策連結 =====================
        policy_links = footer.select("div.app_policy a.footer_button")
        venue_info["policies"] = {}
        for link in policy_links:
            name = link.get_text(strip=True)
            href = link.get("href", "").strip()
            if href.startswith("/"):
                href = f"{base_url}{href.lstrip()}"
            venue_info["policies"][name] = href

        # ===================== Google Map =====================
        gmap_link = footer.select_one("a.button-gmap")
        venue_info["google_map"] = gmap_link.get("href") if gmap_link else "(未提供 Google Map 連結)"

    else:
        venue_info = {"error": "未找到 footer 區塊"}

    # ------------------------------------------------------
    # 輸出 JSON
    # ------------------------------------------------------
    output_json_path = os.path.join(downloads_dir, "fubon_exhibitions.json")
    final_output = {
        "on_now": on_now_result,
        "upcoming": upcoming_result,
        "venue_info": venue_info
    }

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

    print(f"\n已輸出 JSON 檔案至: {output_json_path}")

    # ------------------------------------------------------
    # 輸出展覽 CSV
    # ------------------------------------------------------
    output_csv_path = os.path.join(downloads_dir, "fubon_exhibitions.csv")

    combined_data = []
    for record in on_now_result:
        record["section"] = "On Now"
        combined_data.append(record)
    for record in upcoming_result:
        record["section"] = "Upcoming"
        combined_data.append(record)

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

    # ------------------------------------------------------
    # 輸出場館資訊 CSV
    # ------------------------------------------------------
    venue_csv_path = os.path.join(downloads_dir, "fubon_venue_info.csv")
    with open(venue_csv_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["欄位", "內容"])

        for key, value in venue_info.items():
            if isinstance(value, dict):
                for sub_key, sub_val in value.items():
                    writer.writerow([f"{key} - {sub_key}", sub_val])
            else:
                writer.writerow([key, value])

    print(f"已輸出場館資訊 CSV 檔案至: {venue_csv_path}")


if __name__ == "__main__":
    main()