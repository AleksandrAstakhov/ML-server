FROM python:3.11-slim

ENV VENV_PATH="/opt/venv"
RUN python -m venv $VENV_PATH

ENV PATH="$VENV_PATH/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY .env ./

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
