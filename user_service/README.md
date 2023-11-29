# User Service - Handles User Management

## Setup
### Environment Variables
* SQLALCHEMY_DATABASE_URI
* JWT_SECRET_KEY
* FLASK_APP - set to the name of the file containing the flask app.
    ```sh
    export FLASK_APP="app.py"
    ```
* SERVER_NAME
* USER_SERVICE_CONFIG_MODULE - The configuration class to use, for example.
    ```sh
    export USER_SERVICE_CONFIG_MODULE="user_service.config.dev.DevConfig"
    ```
* JWT_ACCESS_TOKEN_EXPIRES_MINUTES
* JWT_REFRESH_TOKEN_EXPIRES_DAYS
* REDIS_HOST
* REDIS_PORT

### Database Migrations
Run the following command to initialize the database.

```sh
flask db upgrade
```

### Running the app.
Run the app by issuing the following command.

```sh
flask run
```

### Documentation
The API's documentation can be accessed via http://localhost:5000/swagger-ui/

## Tests
Tests can be run with the following command.

```sh
pytest
```
