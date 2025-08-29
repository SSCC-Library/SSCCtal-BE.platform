import requests

url = "https://sscctal.soongsilcomputingclub.kr/api/v1/admin/items/add1"  # 실제 서버 주소/포트로 수정하세요

with open("C:/Users/nhlk1/OneDrive/바탕 화면/SSCCtal-BE.platform/isbn_img_url.txt", "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()  # ✅ 줄바꿈 제거
        if not line:
            continue  # 빈 줄 건너뜀

        try:
            isbn, img_url = line.split(",", 1)
            isbn = isbn.strip()
            img_url = img_url.strip()

            payload = {
                "isbn": isbn,
                "img_url": img_url
            }

            response = requests.post(url, json=payload)
            print(f"{isbn} → 응답 코드: {response.status_code}, 응답 내용: {response.json()}")

        except ValueError:
            print(f"잘못된 형식의 라인: {line}")