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
    # 1. 검색 페이지 요청
    search_url = f"https://www.yes24.com/Product/Search?domain=BOOK&query={isbn}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    # 2. 책 링크 추출
    prd_info = soup.find('a', class_='gd_name')
    if not prd_info:
        print("❌ 도서 링크를 찾을 수 없습니다.")
        return None

    url_detail = "https://www.yes24.com" + prd_info['href']

    # 3. 이미지 URL 추출 (검색 결과 페이지에서)
    img_tag = soup.select_one("ul#yesSchList img[src^='https://image.yes24.com']")
    image_url = img_tag['src'] if img_tag else None

    # 4. 상세 페이지 요청
    r = requests.get(url_detail, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    title_tag = soup.find("h2", class_="gd_name")
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    author_tag = soup.select_one("span.gd_auth a")
    author = author_tag.get_text(strip=True) if author_tag else "저자 없음"

    date_tag = soup.select_one("span.gd_date")
    pub_date_text = date_tag.get_text(strip=True) if date_tag else None
    parsed_date = parse_korean_date(pub_date_text) if pub_date_text else None

    # 디버깅 출력
    print("📘 상세 링크:", url_detail)
    print("🖼️ 이미지:", image_url)
    print("📗 제목:", title)
    print("👤 저자:", author)
    print("📅 출판일:", parsed_date)

    time.sleep(1)

    return {
        "identifier_code": isbn,
        "name": title,
        "publisher": author,
        "publish_date": parsed_date,
        "image_url": image_url  # ✅ 여기서 이미지 URL 반환
    }
