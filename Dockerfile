FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -e ".[web]"

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "heizlast.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
