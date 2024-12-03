FROM python:3.9-slim

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

COPY requirements.txt .
RUN zee_env/bin/pip3.12 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "start.sh"]
