import requests
import time

# 파일 경로
file_path = "C:/Users/nhlk1/Downloads/message (1).txt"  # 본인 경로에 맞게 조정

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# 파일을 한 줄씩 읽고 요청 보내기
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split(",")
        if len(parts) != 2:
            continue  # 잘못된 줄 건너뜀
        _, isbn = parts

        # 패스 파라미터 포함한 URL
        url = f"https://sscctal.soongsilcomputingclub.kr/api/v1/admin/items/add/{isbn}"

        try:
            response = requests.post(url, headers=headers)
            print(f"{isbn} → {response.status_code} | {response.text}")
        except Exception as e:
            print(f"{isbn} → 요청 실패: {e}")

        time.sleep(0.3)  # 서버 과부하 방지