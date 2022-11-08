FROM python:3.9

WORKDIR /image_service/

COPY Pipfil* /image_service/

RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system

COPY . /image_service/

EXPOSE 8080
