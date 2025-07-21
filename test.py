# import cv2
# from pyzbar.pyzbar import decode

# cap = cv2.VideoCapture(0)  # 기본 카메라 사용

# print("QR/바코드 인식 대기 중... (창에서 'q'를 누르면 종료)")

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("카메라 읽기 실패")
#         break

#     barcodes = decode(frame)
#     for barcode in barcodes:
#         data = barcode.data.decode('utf-8')
#         barcode_type = barcode.type  # QR Code, CODE128, EAN13 등

#         print(f"[{barcode_type} 인식됨] ▶ {data}")

#         # 사각형 그리기
#         x, y, w, h = barcode.rect
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

#         # 인식된 텍스트 보여주기
#         cv2.putText(frame, f"{barcode_type}: {data}", (x, y - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 255, 50), 2)

#     cv2.imshow("QR/Barcode Scanner", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()


import time
import re
start = time.time()
import requests
from bs4 import BeautifulSoup
import datetime
ISBN13 = ["9788931551167"]#, "9791169210911", "9791169213608", "9791169212151", "9791169212144", "9791169212137", "9791169211901"]




# ISBN13 = ""

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("카메라 읽기 실패")
#         break

#     barcodes = decode(frame)
#     for barcode in barcodes:
#         data = barcode.data.decode('utf-8')
#         barcode_type = barcode.type  # QR Code, CODE128, EAN13 등

#         print(f"[{barcode_type} 인식됨] ▶ {data}")
#         ISBN13 = data

#         # 사각형 그리기
#         x, y, w, h = barcode.rect
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

#         # 인식된 텍스트 보여주기
#         cv2.putText(frame, f"{barcode_type}: {data}", (x, y - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 255, 50), 2)

#     cv2.imshow("QR/Barcode Scanner", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q') or ISBN13 != "":
#         break

# cap.release()
# cv2.destroyAllWindows()








'''
# start = time.time()
for isbn in ISBN13:
    print(f"/n📕 ISBN 검색: {isbn}")

    try:
        # 1. 검색 페이지 접근
        url = f"https://www.yes24.com/Product/Search?domain=BOOK&query={isbn}"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, 'html.parser')

        # 2. 검색 결과에서 도서 상세 링크 추출
        prd_info = soup.find('a', class_='gd_name')
        if not prd_info:
            print("❌ 도서 링크를 찾을 수 없습니다.")
            continue

        url_detail = "https://www.yes24.com" + prd_info['href']
        print("📘 상세 링크:", url_detail)

        # 3. 상세 페이지 요청
        r = requests.get(url_detail, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, 'html.parser')

        # 4. 제목
        title_tag = soup.find("h2", class_="gd_name")
        title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

        # 작가(저자) 이름 추출
        author_tag = soup.select_one("span.gd_auth a")
        author = author_tag.get_text(strip=True) if author_tag else "저자 없음"

        date_tag = soup.select_one("span.gd_date")
        pub_date = date_tag.get_text(strip=True) if date_tag else "출간일 없음"

        def parse_korean_date(date_str: str) -> datetime.date:
            match = re.search(r"(/d{4})년/s*(/d{1,2})월/s*(/d{1,2})일", date_str)
            if match:
                year, month, day = map(int, match.groups())
                return datetime.date(year, month, day)
            else:
                return None
        
        print("📘 상세 링크:", url_detail)
        print("📗 제목:", title)
        print("👤 저자:", author)
        print("출판일 ",parse_korean_date(pub_date))

        time.sleep(1)  # 서버 과부하 방지를 위한 쉬는 시간

    except Exception as e:
        print("❌ 오류 발생:", str(e))

'''

    # # 이미지 태그 선택
    # img_tag = soup.find("img", class_="gImg")

    # # 이미지 다운로드
    # if img_tag:
    #     img_url = img_tag.get("src")
    #     print("이미지 URL:", img_url)

    #     # 이미지 요청 및 저장
    #     response = requests.get(img_url)
    #     if response.status_code == 200:
    #         with open("{0}.jpg".format(i), "wb") as f:
    #             f.write(response.content)
    #         print("이미지 다운로드 완료!")
    #     else:
    #         print("이미지 요청 실패:", response.status_code)
    # else:
    #     print("이미지를 찾을 수 없습니다.")

end = time.time()
print(f"{end - start:.5f} sec")
# for i in ('infoset_introduce', 'infoset_toc'):
#     print(i + "/n")
#     prd_detail = soup.find('div', attrs={'id':{i}})
#     prd_tr_list = prd_detail.find_all('textarea')
#     print(prd_tr_list,"/n/n")

# prd_detail = soup.find('div', attrs={'id':'infoset_specific'})

# prd_tr_list = prd_detail.find_all('tr')

# for tr in prd_tr_list:
#     if tr.find('th').get_text() == "쪽수, 무게, 크기":
#         print(tr.find('td').get_text().split()[0])


isbn_seen = set()
isbn_unique = []
isbn_duplicates = set()

with open("C:/Users/nhlk1/OneDrive/바탕 화면/isbn_list.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) != 2:
            continue  # 예외 처리

        isbn = parts[1].strip()

        if isbn in isbn_seen:
            isbn_duplicates.add(isbn)
        else:
            isbn_seen.add(isbn)
            isbn_unique.append(isbn)

# ✅ 결과 출력
print("📚 총 ISBN 개수:", len(isbn_unique) + len(isbn_duplicates))
print("✅ 고유한 ISBN 수:", len(isbn_unique))
print("❗ 중복 ISBN 수:", len(isbn_duplicates))

if isbn_duplicates:
    print("/n📛 중복된 ISBN 목록:")
    for d in isbn_duplicates:
        print("-", d)


