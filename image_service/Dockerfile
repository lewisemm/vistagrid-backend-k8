from python:3.7

WORKDIR /image_service/

COPY requirements.txt /image_service/

RUN pip install -r requirements.txt

COPY . /image_service/

EXPOSE 5000

ENV FLASK_APP=api

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]
