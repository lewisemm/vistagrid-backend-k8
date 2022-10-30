# User Service - Handles User Management

## Setup
### Environment Variables
* SQLALCHEMY_DATABASE_URI
* JWT_SECRET_KEY
* POSTGRES_PASSWORD
* POSTGRES_HOST
* POSTGRES_DB
* FLASK_APP
* SERVER_NAME

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
