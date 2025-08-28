import requests
import time

# ISBN 목록이 들어 있는 파일 경로
file_path = "C:/Users/nhlk1/Downloads/message (1).txt"  # 실제 파일 경로로 수정

# 요청할 주소 (패스 파라미터 방식)
base_url = "https://sscctal.soongsilcomputingclub.kr/api/v1/admin/items/add"

# 헤더 (필요 없으면 생략 가능)
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# 파일 열고 한 줄씩 ISBN 추출 후 요청
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        isbn = line.strip()
        if not isbn:
            continue

        url = f"{base_url}/{isbn}"  # 패스 파라미터 포함
        try:
            response = requests.post(url, headers=headers)
            print(f"{isbn} → {response.status_code} | {response.text}")
        except Exception as e:
            print(f"{isbn} → 요청 실패: {e}")

        time.sleep(0.3)  # 서버 보호용 딜레이
