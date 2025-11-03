# fubon_utils.py
import urllib.request as req
import bs4 as bs
import os
import html
import base64
from urllib.parse import quote


# ======================================================
#  函式：解析展覽詳細頁 (第二層爬蟲)
# ======================================================
def get_exhibition_detail(detail_url, downloads_dir, title):
    """進入展覽內頁，抓取展期、地點、介紹文字、QR Code"""
    print(f"\n進入詳細頁: {detail_url}")
    response = req.urlopen(detail_url)
    html_detail = bs.BeautifulSoup(response.read(), "html.parser")

    # --- (1) 展期（date） ---
    date_tags = html_detail.select("div#exhibition-info-basic h2.font-h2")
    if date_tags:
        # 最後一個 <h2> 通常為日期，例如 "2025.10.23 - 2026.4.20"
        date = date_tags[-1].get_text(strip=True)
    else:
        # 備援：舊結構可能使用 detail_intro
        date_tag = html_detail.select_one("div.detail_intro h2.font-h2")
        date = date_tag.get_text(strip=True) if date_tag else "(未提供展期)"

    # --- (2) 地點（div.content_location） ---
    location_div = html_detail.select_one("div.content_location")
    if location_div:
        p_tags = location_div.select("p.font-body")
        location_texts = [p.get_text(strip=True) for p in p_tags if p.get_text(strip=True)]
        location = " ".join(location_texts)
    else:
        location = "(未提供地點)"

    # --- 展覽介紹文字與 QR Code ---
    desc_div = html_detail.select_one("div.font-body")
    description = ""
    qr_filename = "(無 QR Code)"

    if desc_div:
        paragraphs = desc_div.find_all("p")
        text_blocks = []
        for p in paragraphs:
            img = p.find("img")
            if img and img.get("src", "").startswith("data:image/png;base64,"):
                # 解析 base64 圖片
                base64_data = img["src"].split(",")[1]
                pkno = detail_url.split("=")[-1]
                safe_title = "".join([c for c in title if c.isalnum() or c in " _-"]).strip()
                qr_filename = f"{safe_title}_qr_{pkno}.png"
                qr_path = os.path.join(downloads_dir, qr_filename)
                with open(qr_path, "wb") as f:
                    f.write(base64.b64decode(base64_data))
                print(f"已擷取 QR Code 圖片: {qr_filename}")
            else:
                text = p.get_text(strip=True)
                if text:
                    text_blocks.append(text)
        description = "\n".join(text_blocks) if text_blocks else "(無展覽介紹)"
    else:
        description = "(無展覽介紹)"

    return {
        "description": description,
        "date": date,
        "location": location,
        "qr_image_file": qr_filename
    }


# ======================================================
#  函式：解析展覽區塊
# ======================================================
def parse_exhibition_section(section, section_name, base_url, downloads_dir):
    """解析單一區塊（On Now / Upcoming）"""
    print(f"\n=== 解析區塊: {section_name} ===")

    from fubon_utils import get_exhibition_detail  # 避免循環匯入

    exhibitions = section.find_all("a", class_="fb-exhibitions-card")
    results = []

    for expo in exhibitions:
        href_value = expo.get("href")
        link = base_url + href_value if href_value else "(無連結)"

        title_tag = expo.find("h2", class_="font-h2 font-bold")
        eng_title_tag = expo.find("h3", class_="font-h3")
        title = title_tag.get_text(strip=True) if title_tag else "(無標題)"
        eng_title = eng_title_tag.get_text(strip=True) if eng_title_tag else "(無英文標題)"

        info_tags = expo.find_all("p", class_="font-body-en")
        date = info_tags[0].get_text(strip=True) if len(info_tags) >= 1 else "(未提供展期)"
        location = info_tags[1].get_text(strip=True) if len(info_tags) >= 2 else "(未提供地點)"

        # 封面圖處理
        img_tag = expo.find("img")
        if img_tag is not None:
            img_url = html.unescape(img_tag.get("src"))
            encoded_url = quote(img_url, safe=':/')

            # 安全標題前綴
            safe_title = "".join([c for c in title if c.isalnum() or c in " _-"]).strip()

            raw_filename = os.path.basename(img_url).replace(" ", "_")
            filename = f"{safe_title}_{raw_filename}"

            image_path = os.path.join(downloads_dir, filename)
            cmd = f'curl -L -o "{image_path}" "{encoded_url}"'
            os.system(cmd)
            if os.path.exists(image_path):
                print(f"已下載圖片: {filename}")
            else:
                print(f"圖片下載失敗: {encoded_url}")
                filename = "(下載失敗)"
        else:
            encoded_url = "(無圖片)"
            filename = "(無圖片)"

        # 內頁詳細資料
        if link.startswith("https://www.fubonartmuseum.org/ExhibitionDetail"):
            detail_data = get_exhibition_detail(link, downloads_dir, title)
        else:
            detail_data = {
                "description": "(無展覽介紹)",
                "date": date,
                "location": location,
                "qr_image_file": "(無 QR Code)"
            }

        print("展覽名稱:", title)
        print("英文名稱:", eng_title)
        print("展覽日期:", detail_data["date"])
        print("展覽地點:", detail_data["location"])
        print("展覽連結:", link)
        print("展覽介紹:", detail_data["description"][:40] + "...")
        print("QR Code 圖片:", detail_data["qr_image_file"])
        print("-" * 60)

        results.append({
            "title": title,
            "eng_title": eng_title,
            "date": detail_data["date"],
            "location": detail_data["location"],
            "link": link,
            "cover_image_file": filename,
            "cover_image_url": encoded_url,
            "description": detail_data["description"],
            "detail_qr_image_file": detail_data["qr_image_file"]
        })

    return results