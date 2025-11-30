FROM python:3.11-slim

WORKDIR /usr/share/nginx/html/

COPY . /usr/share/nginx/html/

CMD ["python", "-m", "http.server", "80"]