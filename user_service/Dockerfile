FROM python:3.11

WORKDIR /user_service/

COPY requirements.txt /user_service/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install psycopg2==2.9.6

COPY . /user_service/

EXPOSE 5000

ENV FLASK_APP=api

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0", "-p 5000" ]
