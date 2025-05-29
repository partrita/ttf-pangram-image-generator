    # 파이썬 공식 이미지를 기반으로 합니다.
    FROM python:3.10-slim-buster

    # 작업 디렉토리를 /app으로 설정합니다.
    WORKDIR /app

    # requirements.txt를 먼저 복사하여 종속성 설치를 캐싱합니다.
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # 폰트 디렉토리를 /app/fonts로 복사합니다.
    COPY data/fonts/ ./fonts/

    # src 디렉토리 전체를 /app/src로 복사합니다.
    COPY src/ ./src/

    # 기본 명령어를 쉘 형식으로 설정하여, 컨테이너 실행 시 커맨드라인 인자를 전달할 수 있게 함
    # CMD ["python", "-m", "src.font_renderer.main"]
    ENTRYPOINT ["python", "-m", "src.font_renderer.main"]