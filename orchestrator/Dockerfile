FROM python:3.9-slim

WORKDIR /app

COPY orchestrator.py /app/orchestrator.py
COPY my_cron /etc/cron.d/my_cron

RUN apt-get update && apt-get install -y cron

RUN chmod 0644 /etc/cron.d/my_cron
RUN crontab /etc/cron.d/my_cron

CMD ["cron", "-f"]
