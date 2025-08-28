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
        time.sleep(2)  # 페이지가 완전히 로드될 때까지 3초 대기

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
img_url =[]
# 사용 예시
isbn = ["9788963414485","9788968481475","9791165217303","9780137050512","9780470531082","9788971630662","9788996094050","9791169211475","9791185475028","9791161753096","9791165922238","9788960773424",
        "9788960773417","9788960779471","9791161750316","9788960778580","9791197008467"]
img_urls = [
    "https://image.yes24.com/goods/125295944/L",
    "https://image.yes24.com/goods/15651484/L",
    "https://image.yes24.com/goods/104245816/L",
    "https://image.yes24.com/goods/5177108/L",
    "https://image.yes24.com/goods/3440583/L",
    "https://image.yes24.com/goods/129272/L",
    "https://image.yes24.com/goods/4333686/L",
    "https://image.yes24.com/goods/122338517/L",
    "https://image.yes24.com/goods/16854000/L",
    "https://image.yes24.com/goods/74099632/L",
    "https://image.yes24.com/goods/118929778/L",
    "https://image.yes24.com/goods/7516872/L",
    "https://image.yes24.com/goods/7516721/L",
    "https://image.yes24.com/goods/34764614/L",
    "https://image.yes24.com/goods/44150337/L",
    "https://image.yes24.com/goods/26079920/L",
    "https://image.yes24.com/goods/129124813/L"
]
qwer = []
for k in range(len(isbn)) :
    qwer.append([isbn[k],img_urls[k]])

with open ("isbn_same.txt","w",encoding="utf-8") as file :
    for url in qwer :
        file.write(url[0]+","+url[1]+"\n")
