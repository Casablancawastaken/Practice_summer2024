# Используем образ joyzoursky/python-chromedriver
FROM joyzoursky/python-chromedriver:3.9-selenium

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы requirements.txt и устанавливаем зависимости
COPY PFP/requirements.txt .
RUN pip install -r requirements.txt

# Копируем оставшийся код приложения
COPY PFP /app/

# Устанавливаем переменные окружения
ENV DB_NAME=${DB_NAME}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}

# Запускаем приложение
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
