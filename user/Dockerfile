FROM python:3.7

RUN mkdir /code

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY . /code/

EXPOSE 5000

ENV FLASK_APP=app.py

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0"]
