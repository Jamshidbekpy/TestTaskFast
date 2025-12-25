# FROM python:3.12-slim

# WORKDIR /app

# COPY ./requirements.txt /app/requirements.txt

# RUN pip install --no-cache-dir -r /app/requirements.txt

# COPY . /app

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM python:3.12-slim

WORKDIR /app

# uv ni o'rnatish
RUN pip install --no-cache-dir uv

# Tizim kutubxonalari (PostgreSQL uchun)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# pyproject.toml ni copy qilish
COPY pyproject.toml /app/

# UV bilan kutubxonalarni o'rnatish (pyproject.toml dan)
RUN uv pip install --system -e .

# Yoki to'g'ridan-to'g'ri:
# RUN uv pip install --system .

# Qolgan kodni copy qilish
COPY . /app

# Ishga tushirish
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]