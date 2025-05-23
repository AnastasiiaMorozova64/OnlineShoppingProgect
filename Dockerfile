FROM python:3.11-slim
WORKDIR /app
COPY cactus_shop/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY cactus_shop/ .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]