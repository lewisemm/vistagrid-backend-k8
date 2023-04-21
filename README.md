[![codecov](https://codecov.io/github/lewisemm/vistagrid-backend-k8/branch/master/graph/badge.svg?token=49IX4RQEHZ)](https://codecov.io/github/lewisemm/vistagrid-backend-k8)

# Getting Started

## Building The Images
To run the entire app on docker, first build the `user_service` and `image_service` images.

```sh
docker-compose -f docker-compose.yml -f deployment/docker/docker-compose-imageservice.yml -f deployment/docker/docker-compose-userservice.yml build
```

## Running The App
The following command will get `user_service`, `image_service` and their dependent images started.

```sh
docker-compose -f docker-compose.yml -f deployment/docker/docker-compose-imageservice.yml -f deployment/docker/docker-compose-userservice.yml up
```

### Prerequisite Setup
#### Database Migrations
Apply migrations for the `user_service` by running the following command.

```sh
docker exec user_service flask db upgrade
```

Apply migrations for the `image_service` by running the following command.

```sh
docker exec image_service python manage.py migrate
```

#### Celery Workers

Start the Celery workers in detached mode to handle asynchronous tasks.

```sh
docker exec -d image_service celery -A image_service worker -l INFO
```

#### Using The App

1. Creating Users
    ```sh
    curl -X POST http://localhost:5000/api/user -H "Content-Type: application/json" -d '{"username":"joe", "password":"joepassword"}'
    ```

2. Obtaining User JWT
    ```sh
    curl -X POST http://localhost:5000/api/user -H "Content-Type: application/json" -d '{"username":"joe", "password":"joepassword"}'
    # example response
    {"access_token": <token string>}
    ```
## Docs
* `user_service` docs: http://localhost:5000/swagger-ui/
