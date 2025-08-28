from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_yes24_image_url_selenium(isbn):
    """
    Selenium을 사용하여 YES24에서 ISBN을 기반으로 상품 이미지 URL을 가져옵니다.
    """
    # Chrome 옵션 설정 (브라우저 창을 띄우지 않는 headless 모드)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0...")
    
    # 웹 드라이버 설정 (webdriver-manager를 사용하여 자동으로 설치)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    search_url = f"https://www.yes24.com/Product/Search?query={isbn}"
    
    try:
        driver.get(search_url)
        time.sleep(3)  # 페이지가 완전히 로드될 때까지 3초 대기

        # CSS 선택자를 사용해 이미지 요소 찾기
        # 'src' 속성을 가진 <img> 태그를 찾습니다.
        image_element = driver.find_element(By.CSS_SELECTOR, '.sGLi .item_img .img_item img')

        if image_element:
            image_url = image_element.get_attribute('src')
            return image_url
        else:
            return "이미지 URL을 찾을 수 없습니다."

    except Exception as e:
        return f"오류 발생: {e}"

    finally:
        driver.quit() # 드라이버 종료

# 사용 예시

with open("C:/Users/nhlk1/Downloads/isbn_unique.txt", "r", encoding="utf-8") as ifile, \
    open("isbn_img_url.txt", "w", encoding="utf-8") as ofile:

    for line in ifile:
        isbn = line.strip()
        if isbn:
            image_url = get_yes24_image_url_selenium(isbn)
            ofile.write(f"{isbn},{image_url}\n")
            print(f"{isbn} → {image_url}")
    
        print(f"ISBN {isbn}에 대한 YES24 이미지 URL: {image_url}")