# 베이스 이미지로 python:3.10 사용
FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt .
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

# 환경 변수 설정 (GPU 비활성화)
ENV CUDA_VISIBLE_DEVICES=""

# sample_music 디렉토리 복사
COPY sample_music /app/sample_music

# 애플리케이션 코드 복사
COPY . .

# FastAPI 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
