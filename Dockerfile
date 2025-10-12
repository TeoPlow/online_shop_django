FROM python:3.11-slim

WORKDIR /app

COPY ./online_shop /app
COPY requirements.txt /app/
COPY diploma-frontend-0.6.tar.gz /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install /app/diploma-frontend-0.6.tar.gz

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
