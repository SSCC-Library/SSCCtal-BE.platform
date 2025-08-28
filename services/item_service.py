import requests
from bs4 import BeautifulSoup
from datetime import date
import re
import time

def parse_korean_date(date_str: str) -> date:
    match = re.search(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", date_str)
    if match:
        year, month, day = map(int, match.groups())
        return date(year, month, day)
    return None

def fetch_book_info(isbn: str):
    url = f"https://www.yes24.com/Product/Search?domain=BOOK&query={isbn}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, 'html.parser')

    prd_info = soup.find('a', class_='gd_name')
    if not prd_info:
        print("❌ 도서 링크를 찾을 수 없습니다.")
        return None

    url_detail = "https://www.yes24.com" + prd_info['href']
    r = requests.get(url_detail, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, 'html.parser')

    # 제목
    title_tag = soup.find("h2", class_="gd_name")
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    # 저자
    author_tag = soup.select_one("span.gd_auth a")
    author = author_tag.get_text(strip=True) if author_tag else "저자 없음"

    # 출판일
    date_tag = soup.select_one("span.gd_date")
    pub_date_text = date_tag.get_text(strip=True) if date_tag else None
    parsed_date = parse_korean_date(pub_date_text) if pub_date_text else None

    # 이미지 (data-original 속성에서 가져오기)
    img_tag = soup.select_one("span.img_item img")
    image_url = img_tag.get("data-original") if img_tag else None

    print("📘 상세 링크:", url_detail)
    print("📗 제목:", title)
    print("👤 저자:", author)
    print("📅 출판일:", parsed_date)
    print("🖼️ 이미지:", image_url)

    time.sleep(1)
    return {
        "identifier_code": isbn,
        "name": title,
        "publisher": author,
        "publish_date": parsed_date,
        "image_url": image_url
    }
