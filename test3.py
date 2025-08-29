import pandas as pd
import requests

# 엑셀 파일 경로
excel_path = "학생명단.xlsx"  # 파일명에 맞게 수정

# 서버 정보
url = "http://localhost:8000/create"  # FastAPI 서버 주소
admin_token = 1234  # 관리자 인증용 토큰

# 엑셀 불러오기
df = pd.read_excel(excel_path)

# 기본값 설정
default_gender = "MALE"  # 또는 "FEMALE"
default_email_domain = "example@example.com"  # 이메일이 없을 경우 자동 생성용

# 각 행마다 서버에 요청
for _, row in df.iterrows():
    name = row['이름']
    major = row['전공']
    student_id = int(row['학번'])
    phone_number = row['전화번호']
    
    # 예시 이메일 생성 (중복 방지 위해 학번 기반)
    email = f"{student_id}{default_email_domain}"
    
    user_data = {
        "student_id": student_id,
        "name": name,
        "email": email,
        "phone_number": phone_number,
        "gender": default_gender,
        "major": major,
        "major2": None,
        "minor": None,
        "user_classification": "STUDENT"
    }
    
    response = requests.post(
        url,
        params={"token": admin_token},
        json=user_data
    )
    
    print(f"[{name}] 응답 코드: {response.status_code}, 결과: {response.json()}")
