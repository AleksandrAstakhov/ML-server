# Dockerfile client

# задали начальный образ(слой)
FROM python:3.11-slim

# создали временное виртуальное окружение
ENV VENV_PATH="/opt/venv"
RUN python -m venv $VENV_PATH

# добавили в PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# задали рабочую ппапку
WORKDIR /client

# установили зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# скопировали данные
COPY . .


# задали точку входа
CMD ["python", "run_tests.py"]
