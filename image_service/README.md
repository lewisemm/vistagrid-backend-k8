# Image Service - Handles Image Management including Image Upload, Manipulation and Deletion.

## Setup
### Environment Variables
* SECRET_KEY
* DJANGO_SETTINGS_MODULE
* DATABASE_URL
* AWS_SECRET_ACCESS_KEY
* AWS_ACCESS_KEY_ID
* S3_BUCKET
* CELERY_BROKER_URL
* AUTH_SERVICE_URL

### Background Services
The following background services are required to run the app.

* `user_service` - required to verify jwt tokens.
* A database e.g. MySQL, specified by `DATABASE_URL` environment variable.
* A message broker url e.g. RabbitMQ, specified by `CELERY_BROKER_URL` environment variable.

### Database Migrations
Run the following command to initialize the database.

```sh
python manage.py migrate
```

## Running the app.

### Starting the user_service
The `user_service` needs to be running independently to facilitate verification of jwt tokens.

The root url of the `user_service` also needs to be provided as the `AUTH_SERVICE_URL` environment variable.

Start instructions can be found in the `user_service` [README](../user_service/README.md).

### Starting Celery
Celery needs to be running as a background service to facilitate asynchronous photo uploads to s3.

```sh
celery -A image_service worker -l INFO
```

### Starting the Django app
The Django app can be started by issuing the following command.

```sh
python manage.py runserver
```

## Tests
Tests can be run with the following command.

```sh
python manage.py test
```
