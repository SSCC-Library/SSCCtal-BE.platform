import pandas as pd
import requests

# 엑셀 파일 경로
excel_path = "학생명단.xlsx"  # 파일명에 맞게 수정

# 서버 정보
url = "https://sscctal.soongsilcomputingclub.kr/api/v1/admin/users/create"  # FastAPI 서버 주소
admin_token = 1234  # 관리자 인증용 토큰

# 엑셀 불러오기
df = pd.read_excel("C:/Users/nhlk1/OneDrive/바탕 화면/학생명단.xlsx",header=None)

# 기본값
default_gender = "male"
default_email_domain = "@example.com"

# 반복 전송
for idx, row in df.iterrows():
    name = row[0]
    major = row[1]
    student_id = int(row[2])
    phone_number = str(row[3])

    email = f"{student_id}{default_email_domain}"  # 예: 20211397@example.com

    user_data = {
        "student_id": student_id,
        "name": name,
        "email": email,
        "phone_number": phone_number,
        "gender": default_gender,
        "major": major,
        "major2": None,
        "minor": None,
        "user_classification": "staff"
    }

    response = requests.post(
        url,
        json=user_data
    )

    print(f"[{idx}] {name} - 상태 코드: {response.status_code}, 응답: {response.json()}")