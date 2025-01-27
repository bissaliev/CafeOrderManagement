FROM python:3.12
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./cafe .
COPY ./entrypoint.sh .
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT [ "/app/entrypoint.sh" ]