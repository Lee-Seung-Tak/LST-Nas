# 1. Python 공식 이미지 사용
FROM python:3.10

# 2. 작업 디렉터리 설정
WORKDIR /app

# 3. 필요 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 복사
COPY . .

# 5. FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
