FROM python:3.7

# create a migrations folder for migrations to be mounted as a volume
# in the userservice container
RUN mkdir -p /user_service/migrations

WORKDIR /user_service/

COPY requirements.txt /user_service/

RUN pip install -r requirements.txt

COPY . /user_service/

EXPOSE 5000

ENV FLASK_APP=api

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]
