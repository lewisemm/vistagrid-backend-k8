# User Service - Handles User Management

## Setup
### Environment Variables
* SQLALCHEMY_DATABASE_URI
* JWT_SECRET_KEY
* POSTGRES_PASSWORD
* POSTGRES_HOST
* POSTGRES_DB
* FLASK_APP # export FLASK_APP="api.py"
* SERVER_NAME
* USER_SERVICE_CONFIG_MODULE # e.g export USER_SERVICE_CONFIG_MODULE="user_service.config.config.DevConfig"
* JWT_ACCESS_TOKEN_EXPIRES_MINUTES
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

## Tests
Tests can be run with the following command.

```sh
pytest
```
