FROM python:3.11

WORKDIR /image_service/

COPY Pipfil* /image_service/

RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system && \
    pip install mysqlclient==2.1.1

COPY . /image_service/

EXPOSE 5000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:5000" ]
