FROM python:3.11-slim

ENV VENV_PATH="/opt/venv"
RUN python -m venv $VENV_PATH

ENV PATH="$VENV_PATH/bin:$PATH"

WORKDIR /client

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run_tests.py"]
